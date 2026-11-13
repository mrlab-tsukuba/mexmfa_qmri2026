"""Read-only provenance audit for the bytecode-only production modules."""
from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
import json
import marshal
from pathlib import Path
from types import CodeType


MODULES = {
    'zsmri/wrappers_chunked_rec_eval.pyc': 'Module/zsmri/wrappers_chunked_rec_eval.py',
    'zsmri/np/resampler.pyc': 'Module/zsmri/np/resampler.py',
    'zsmri/torch/dataset.pyc': 'Module/zsmri/torch/dataset.py',
    'zsmri/torch/loss.pyc': 'Module/zsmri/torch/loss.py',
    'zsmri/torch/operators.pyc': 'Module/zsmri/torch/operators.py',
    'zsmri/torch/system.pyc': 'Module/zsmri/torch/system.py',
    'zsmri/torch/utils.pyc': 'Module/zsmri/torch/utils.py',
    'zsmri/torch/layers/cnn.pyc': 'Module/zsmri/torch/layers/cnn.py',
    'zsmri/torch/models/unroll.pyc': 'Module/zsmri/torch/models/unroll.py',
}
# The original module imports tinycudann but never references it. The public
# CPU package makes that import optional; no CG method code was changed.
INTENTIONAL_COMPATIBILITY_EXCEPTION = 'zsmri/torch/layers/dc.pyc'


def load_pyc(path: Path):
    with path.open('rb') as handle:
        magic = handle.read(4)
        handle.read(12)
        return magic, marshal.load(handle)


def semantic_fingerprint(code: CodeType):
    """Compare executable semantics, excluding source-location metadata."""
    items = []
    def visit(item: CodeType):
        items.append((item.co_qualname, item.co_code))
        for value in item.co_consts:
            if isinstance(value, CodeType):
                visit(value)
    visit(code)
    return Counter(items)


def instruction_fingerprint(code: CodeType):
    streams = []
    def visit(item: CodeType):
        streams.append(item.co_code)
        for value in item.co_consts:
            if isinstance(value, CodeType):
                visit(value)
    visit(code)
    return Counter(streams)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    report = {'python_magic_matches': True, 'unchanged_modules': [], 'instruction_equivalent_modules': [], 'mismatches': [], 'intentional_exception': INTENTIONAL_COMPATIBILITY_EXCEPTION}
    if importlib.util.MAGIC_NUMBER != load_pyc(root / 'mexmfa_zssl_api.pyc')[0]:
        report['python_magic_matches'] = False
    for released_rel, source_rel in MODULES.items():
        released = root / released_rel
        source = args.source_root / source_rel
        _, release_code = load_pyc(released)
        # Do not inherit this audit script's future-annotations compiler flag.
        expected = compile(source.read_bytes(), release_code.co_filename, 'exec', dont_inherit=True)
        if semantic_fingerprint(release_code) == semantic_fingerprint(expected):
            report['unchanged_modules'].append(released_rel)
        else:
            report['mismatches'].append(released_rel)
    args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    if report['mismatches'] or not report['python_magic_matches']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
