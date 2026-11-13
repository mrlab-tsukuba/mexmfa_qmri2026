"""Compare production Cartesian SENSE source with the released bytecode.

The source paths are supplied by the reviewer and are never stored in output.
The comparison uses one deterministic complex64 Cartesian example.  The
production CG module is loaded after replacing only its unused tinycudann
import with ``tcnn = None``; this is the documented CPU import compatibility
measure and does not alter the CG class body.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.machinery
import json
import marshal
from pathlib import Path
from types import CodeType, ModuleType

import torch


FIELDS = (
    "co_argcount", "co_posonlyargcount", "co_kwonlyargcount", "co_nlocals",
    "co_stacksize", "co_flags", "co_code", "co_consts", "co_names",
    "co_varnames", "co_filename", "co_name", "co_qualname", "co_firstlineno",
    "co_linetable", "co_exceptiontable", "co_freevars", "co_cellvars",
)
LOCATION_FIELDS = {"co_filename", "co_firstlineno", "co_linetable"}


def load_pyc(path: Path) -> CodeType:
    with path.open("rb") as handle:
        handle.read(16)
        return marshal.load(handle)


def nested(code: CodeType, path: str = "<module>"):
    yield path, code
    for index, value in enumerate(code.co_consts):
        if isinstance(value, CodeType):
            yield from nested(value, f"{path}/const[{index}]={value.co_qualname}")


def scalar_constants(code: CodeType):
    return tuple((type(value).__name__, repr(value)) for value in code.co_consts if not isinstance(value, CodeType))


def summarize(value):
    if isinstance(value, bytes):
        return {"bytes": len(value), "sha256": hashlib.sha256(value).hexdigest()}
    if isinstance(value, tuple):
        return {"tuple": len(value), "repr": repr(value)[:500]}
    return repr(value)[:500]


def metadata_differences(release: CodeType, production: CodeType):
    def by_qualname(code):
        result = {}
        for _, item in nested(code):
            if item.co_qualname in result:
                raise RuntimeError(f"ambiguous code-object qualname: {item.co_qualname}")
            result[item.co_qualname] = item
        return result
    rel = by_qualname(release)
    prod = by_qualname(production)
    result = []
    for key in sorted(set(rel) | set(prod)):
        if key not in rel or key not in prod:
            result.append({"code_object": key, "field": "presence", "release": key in rel, "production": key in prod, "location_metadata": False})
            continue
        for field in FIELDS:
            left, right = getattr(rel[key], field), getattr(prod[key], field)
            if field == "co_consts":
                left, right = scalar_constants(rel[key]), scalar_constants(prod[key])
            if left != right:
                result.append({
                    "code_object": key,
                    "field": field,
                    "location_metadata": field in LOCATION_FIELDS,
                    "release": summarize(left),
                    "production": summarize(right),
                })
    return result


def load_source_module(path: Path, name: str, import_patch: bool = False) -> ModuleType:
    source = path.read_text(encoding="utf-8")
    if import_patch:
        needle = "import tinycudann as tcnn"
        if needle not in source:
            raise RuntimeError("expected unused tinycudann import was not found")
        source = source.replace(needle, "tcnn = None  # unused import made optional for CPU audit", 1)
    module = ModuleType(name)
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec", dont_inherit=True), module.__dict__)
    return module


def load_pyc_module(path: Path, name: str) -> ModuleType:
    loader = importlib.machinery.SourcelessFileLoader(name, str(path))
    module = ModuleType(name)
    loader.exec_module(module)
    return module


def error_metrics(reference: torch.Tensor, candidate: torch.Tensor):
    delta = (reference - candidate).abs()
    maximum = float(delta.max().item())
    scale = max(float(reference.abs().max().item()), 1.0e-12)
    return {"max_abs_error": maximum, "max_relative_error": maximum / scale}


def complex_randn(*shape: int) -> torch.Tensor:
    return (torch.randn(*shape) + 1j * torch.randn(*shape)).to(torch.complex64)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--operators-source", required=True, type=Path)
    parser.add_argument("--dc-source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    release_code = load_pyc(root / "zsmri/torch/operators.pyc")
    production_code = compile(args.operators_source.read_bytes(), release_code.co_filename, "exec", dont_inherit=True)
    diffs = metadata_differences(release_code, production_code)

    production = load_source_module(args.operators_source, "production_operators")
    released = load_pyc_module(root / "zsmri/torch/operators.pyc", "released_operators")
    production_dc = load_source_module(args.dc_source, "production_dc", import_patch=True)
    released_dc = load_pyc_module(root / "zsmri/torch/layers/dc.pyc", "released_dc")

    torch.manual_seed(20261113)
    batch, coils, echoes, height, width = 1, 2, 3, 6, 6
    smaps = complex_randn(batch, coils, height, width)
    smaps = smaps / torch.sqrt((smaps.abs() ** 2).sum(dim=1, keepdim=True))
    masks = (torch.rand(batch, echoes, height, width) > 0.35)
    x = complex_randn(batch, echoes, height, width)
    k = complex_randn(batch, coils, echoes, height, width)
    op_production = production.SenseMC(smaps, masks, norm="ortho", batchmode=True)
    op_release = released.SenseMC(smaps, masks, norm="ortho", batchmode=True)

    forward_production, forward_release = op_production * x, op_release * x
    adjoint_production, adjoint_release = op_production.H * k, op_release.H * k
    lamda = 0.05
    us_img = op_production.H * forward_production
    z = complex_randn(batch, echoes, height, width)
    dc_production = production_dc.CGbasedDataConsistency(max_iter=10, tol=1e-10)
    dc_release = released_dc.CGbasedDataConsistency(max_iter=10, tol=1e-10)
    dc_production.update(us_img, op_production, lamda)
    dc_release.update(us_img, op_release, lamda)
    cg_production, cg_release = dc_production(z), dc_release(z)

    lhs = torch.sum(torch.conj(forward_production) * k)
    rhs = torch.sum(torch.conj(x) * adjoint_production)
    lhs_release = torch.sum(torch.conj(forward_release) * k)
    rhs_release = torch.sum(torch.conj(x) * adjoint_release)
    adjointness = error_metrics(lhs.reshape(1), rhs.reshape(1))
    atol = 5e-6
    rtol = 5e-6
    numerical = {
        "dtype": "complex64",
        "shape": {"smaps": list(smaps.shape), "masks": list(masks.shape), "image": list(x.shape)},
        "tolerance": {"atol": atol, "rtol": rtol},
        "forward": error_metrics(forward_production, forward_release),
        "adjoint": error_metrics(adjoint_production, adjoint_release),
        "cg_data_consistency": error_metrics(cg_production, cg_release),
        "adjointness_production": adjointness,
        "adjointness_release": error_metrics(lhs_release.reshape(1), rhs_release.reshape(1)),
    }
    def passes(metrics):
        return metrics["max_abs_error"] <= atol or metrics["max_relative_error"] <= rtol
    numerical["pass"] = all(passes(numerical[name]) for name in ("forward", "adjoint", "cg_data_consistency", "adjointness_production", "adjointness_release"))
    semantic_fields = {d["field"] for d in diffs if not d.get("location_metadata")}
    report = {
        "metadata_differences": diffs,
        "non_location_difference_fields": sorted(semantic_fields),
        "numerical": numerical,
        "conclusion": "equivalent" if not semantic_fields and numerical["pass"] else "unresolved",
    }
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["conclusion"] != "equivalent":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
