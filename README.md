# MExMFA qMRI: reproducibility demonstration

This repository is a **pre-publication, private** synthetic-data demonstration
package for the manuscript
**“Joint Multi-Echo and Multi-Flip-Angle Reconstruction for High-Resolution
Quantitative MRI of Human Embryos.”**

**Manuscript authors:** Yasuhiko Terada and Shigehito Yamada.
**Status:** Manuscript in preparation for submission to *Tomography*.
This package is not publicly released; distribution remains subject to
authorization to distribute the compiled code and final documentation review.

It follows the study workflow: 20 SPGR
conditions (5 flip angles × 4 echo times) are reconstructed jointly, then a
single joint SPGR--T2* fit produces **T1**, **T2***, and **M0** maps.

## Quick start

Docker Desktop with Compose is required. From this directory:

```bash
docker compose up --build
```

Open `http://localhost:8888/lab`, then run `sample.ipynb`. The notebook makes
`data/synthetic_af4_zssl.npz` if it is absent, runs the compiled production ZS-SSL reconstruction and
fit module, saves outputs under `results/`, and displays image metrics against
the numerical fully-sampled reference.

For a non-notebook smoke test:

```bash
docker compose run --rm mexmfa-demo python scripts/run_demo.py
```

## Contents

- `mexmfa_zssl_api.pyc` and `zsmri/**/*.pyc` — bytecode-only extraction of
  the production MExMFA ZS-SSL route and its minimal dependencies.
- `mexmfa_demo/core.pyc` — synthetic numerical data and qMRI fitting helper;
  source is intentionally omitted.
- `sample.ipynb` — user-facing demo notebook.
- `scripts/` — transparent launch helpers, not reconstruction source.
- `data/` — generated numerical phantom only (never human MRI data).
- `Dockerfile`, `docker-compose.yml`, and version-pinned `requirements.txt`.

## What the demo does

The numerical phantom uses TR = 100 ms, FA = 10/30/50/70/90°, and TE =
5/15/25/35 ms, matching the 20-condition arrangement used by the representative
retrospective reconstruction notebook. A variable-density Cartesian mask has a
nominal AF of 4. The demo initializes the same 40-channel `MoDL2D`
configuration used by the representative pipeline: 7 unrolls, a
5-residual-block/13-convolution regularizer, and CG data consistency with at
most 10 iterations. It applies the original Cartesian ZS-SSL mask splitting
(validation 20%; training-loss 40% of the remainder), normalized L1/L2
k-space loss, scan-specific Adam optimization, validation, best-weight
loading, and unrolled inference.

The public demo is deliberately small and CPU-portable: it uses a 24 × 24
numerical input and two epochs, rather than the manuscript-scale volumes and
200-epoch schedule. These reductions do not change the network structure,
ZS-SSL partitioning, loss, or data-consistency algorithm. Demo metrics are
functional checks only and must not be quoted as manuscript results.

## Scope and restrictions

No human embryo images, acquisition files, masks, source paths, identifiers,
credentials, or fitted maps are included. Real-data reproduction additionally
requires the institutionally controlled raw MRI data, acquisition-specific
sampling masks, B1 maps, the production reconstruction environment, and the
approved study processing configuration. `M0` is used consistently; it is not
labeled proton density.

The compiled module targets CPython 3.11 exactly, which is pinned by the
Docker base image. It is not a cross-version Python binary.

## Environment and validation scope

The Docker image uses CPython 3.11.8, CPU PyTorch 2.2.2, mirtorch 0.1.2,
torchkbnufft 1.4, NumPy 1.26.4, and SciPy 1.12.0; the full pinned list is in
`requirements.txt`. Validation is limited to a 24 × 24 synthetic AF4 phantom,
two ZS-SSL train/validation epochs, output-map fitting, and numerical
FS-reference checks. Complete reproduction of paper results requires
non-public human-embryo MRI data, acquisition-specific masks, B1 maps, and
the approved study configuration; those materials are not included.

## Citation and data availability

Please cite the MExMFA manuscript identified above when publication details
become available. This demo builds on prior work on ZS-SSL reconstruction for
human embryo MRI: Iwazaki, K.; Fujita, N.; Yamada, S.; Terada, Y.
*Compressed Sensing Reconstruction with Zero-Shot Self-Supervised Learning
for High-Resolution MRI of Human Embryos*, *Tomography* **2025**, 11, 88.
DOI: 10.3390/tomography11080088.

The repository supplies a compiled implementation and synthetic test data;
it does **not** include the ethically restricted human embryo MRI data.
The synthetic demo is not sufficient to reproduce all numerical results of
the manuscript.

## Project license

This package intentionally does not include a project `LICENSE` file, in line
with the earlier `zs_ssl_recon2025` distribution. Making the repository public
does not itself grant permissions to reuse, modify, or redistribute the code;
the applicable copyright rules remain in force. Third-party dependency
licenses are described separately in `THIRD_PARTY_LICENSES.md`.

## Before publishing

Run `scripts/verify_release.py` in Docker, inspect the generated report, and
confirm code-distribution authorization, authorship and ethics wording. Do not publish until the
maintainers approve the content and the final `.pyc` build.
