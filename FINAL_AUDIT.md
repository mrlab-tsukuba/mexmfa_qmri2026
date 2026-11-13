# Final pre-publication audit

Date: 2026-11-13 (Asia/Tokyo)

## Passed checks

- A no-cache Docker build followed by `docker run --rm` (without a workspace
  mount) completed the 20-condition synthetic ZS-SSL demo successfully.
- The run performed two training and validation epochs, wrote a loss CSV,
  selected the best validation weights, performed unrolled inference, and
  wrote T1, T2*, M0, and reference-metric outputs.
- The release tree contains no real MRI formats, private notebooks, source
  parameter maps, credential files, or non-public path strings in the checked
  bytecode filenames.
- All core algorithm modules are CPython 3.11 bytecode. Python source is
  limited to five transparent generation, launch, and audit scripts.
- A final static scan found 14 `.pyc` files, all with CPython 3.11 magic
  `a70d0d0a`; no cache directories, credential-pattern matches, or common
  MRI/raw-data file formats were present.
- All nine production modules, including `zsmri/torch/operators.pyc`, match
  the original source at bytecode level when compiled without inherited future
  flags. The CG module has the documented unused-import compatibility change
  for CPU use.

## Resolved Cartesian SENSE equivalence check

The former `operators.pyc` discrepancy was an audit false positive: the audit
script's `from __future__ import annotations` flag had been inherited while
recompiling the original source. Recompiling with `dont_inherit=True` and the
public bytecode's filename (so that the non-semantic `co_filename` path is
normalized) produced no differences in any nested code-object metadata,
constants, bytecode, line/position fields, or processing order. The full result is in
`audit/operator_equivalence.json`.

In a deterministic complex64 Cartesian test (batch 1, coils 2, echoes 3,
matrix 6 x 6), released versus production forward, adjoint, and 10-iteration
CG data-consistency outputs each had maximum absolute and relative errors of
0. Production and release adjointness residuals were both 2.3841858e-06
absolute and 1.3113087e-07 relative; the acceptance criterion was absolute or
relative error <= 5e-06. The production CG class was loaded with only its known unused
`tinycudann` import made optional for CPU import; its method body was not
changed. Cartesian SENSE equivalence is therefore confirmed for the audited
route.

## License status

The direct dependency review is in `THIRD_PARTY_LICENSES.md`. The project
license and copyright owner for the MExMFA bytecode have not been chosen or
confirmed, so a project `LICENSE` is intentionally absent. This is a release
blocker, not a runtime blocker.

## GitHub status

The planned repository name is `mexmfa_qmri2026`. Registration steps are in
`GITHUB_REGISTRATION_PREP.md`, and the exact intended release tree is in
`PUBLIC_FILE_MANIFEST.md`. No Git repository, remote, commit, push, or GitHub
publication was created.
