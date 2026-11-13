# Production ZS-SSL release-candidate validation

Date: 2026-11-13 (Asia/Tokyo)

## Code correspondence

The representative read-only notebook calls `Module.zsmri.embryo.gpuchunk.run_MEMFAsim_rec_only`. Its common multi-contrast route creates `MoDL2D(n_layers=5, k_iters=7, n_filter=64, cg_iters=10, n_channel=2*E)`, where E=20. The public adapter instantiates the same configuration with `n_channel=40`, then calls the same copied `zsssdu_multicontrast_recon_chunked` function.

| Production component | Public bytecode file | Status |
| --- | --- | --- |
| MoDL 7-unroll model | `zsmri/torch/models/unroll.pyc` | unchanged |
| 5-block, 13-convolution regularizer | `zsmri/torch/layers/cnn.pyc` | unchanged |
| CG data consistency, max 10 | `zsmri/torch/layers/dc.pyc` | algorithm unchanged; unused-import compatibility change |
| Cartesian multi-contrast SENSE | `zsmri/torch/operators.pyc` | unchanged; nested-code and numerical equivalence confirmed |
| ZS-SSL mask partition and normalization | `zsmri/wrappers_chunked_rec_eval.pyc`, `zsmri/np/resampler.pyc` | unchanged |
| training/validation, best model, loss CSV | `zsmri/torch/system.pyc` and wrapper | unchanged |
| synthetic-NPZ adapter and qMRI hand-off | `mexmfa_zssl_api.pyc` | public I/O adapter only |

The only source-level compatibility change was making the unused `tinycudann` import optional in the CG module. The CG computation does not reference that import. `operators.pyc` passed a nested-code comparison after the audit compiler was corrected not to inherit its own future-annotations flag; deterministic complex64 forward, adjoint, and 10-iteration CG outputs were also exactly equal to the production route. The release uses a 24 × 24 numerical phantom and two epochs; network architecture, data partition, loss, and unrolled CG route are not substituted.

## Docker execution

The container is CPython 3.11.8 with pinned CPU PyTorch 2.2.2, mirtorch 0.1.2, torchkbnufft 1.4, NumPy 1.26.4, and SciPy 1.12.0. The final validation ran from the built image without a source-code mount.

- `MoDL2D(..., n_channel=40)` initialized successfully.
- Two full ZS-SSL training and validation epochs ran on 20 input conditions.
- `loss_zssl.csv` was written; final run loss values were 1.0222/1.0144 and 0.9771/1.0109 (train/validation).
- Best validation weights were loaded and unrolled reconstruction ran.
- T1, T2*, and M0 maps plus FS-reference metrics were written.
- `scripts/verify_release.py` passed after inspecting bytecode filenames for disallowed `/workdir`, data-root, and research-version paths.

The final synthetic result was NRMSE 0.1544, PSNR 14.9690 dB, and SSIM 0.9032 (mean across conditions). It is a functional check, not a manuscript result.

## Public-content check

The package contains no human data, original notebooks, external imaging formats, fitted maps, credentials, or source MRI paths. Only five transparent generation/launch/validation/audit scripts are `.py`; all algorithm modules are Python 3.11 `.pyc`. GitHub publication has not been performed.

## Remaining scope limits

This verifies the CPU small-phantom route only. GPU execution, 200 epochs, large 3-D volumes, original binary-image loading, acquisition-specific masks, B1 maps, and manuscript numerical results have not been revalidated here.
