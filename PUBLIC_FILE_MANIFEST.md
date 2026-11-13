# Public file manifest

Repository: `mrlab-tsukuba/mexmfa_qmri2026` (private registration completed
on 2026-11-13; initial commit `2b8ddfee87cd0937c35402061c613d3cb0c43801`).
The 34 entries listed below were included in that initial private commit.
No public GitHub Release has been made.

The following are the intended tracked release files.  `results/`, Python
cache directories, notebook checkpoints, and every other file are excluded
from the release unless this manifest is deliberately updated and re-audited.

```text
.dockerignore
.gitignore
Dockerfile
docker-compose.yml
README.md
RELEASE_VALIDATION.md
FINAL_AUDIT.md
THIRD_PARTY_LICENSES.md
GITHUB_REGISTRATION_PREP.md
PUBLIC_FILE_MANIFEST.md
requirements.txt
sample.ipynb
data/synthetic_af4_zssl.npz
mexmfa_demo/__init__.pyc
mexmfa_demo/core.pyc
mexmfa_zssl.pyc
mexmfa_zssl_api.pyc
scripts/audit_provenance.py
scripts/audit_operators_equivalence.py
scripts/generate_synthetic_data.py
scripts/run_demo.py
scripts/verify_release.py
zsmri/wrappers_chunked_rec_eval.pyc
zsmri/np/resampler.pyc
zsmri/torch/dataset.pyc
zsmri/torch/loss.pyc
zsmri/torch/operators.pyc
zsmri/torch/system.pyc
zsmri/torch/utils.pyc
zsmri/torch/layers/cnn.pyc
zsmri/torch/layers/dc.pyc
zsmri/torch/models/unroll.pyc
audit/provenance_audit.json
audit/operator_equivalence.json
```

The five Python scripts are transparent data-generation, launch, verification,
and provenance/equivalence-audit helpers. They are not reconstruction or
fitting source.
All reconstruction and fitting implementation files are CPython 3.11 bytecode
listed above.

`FINAL_AUDIT.md` documents the completed Cartesian SENSE equivalence audit and
the remaining project-license/copyright approval required before release.
