# Third-party dependency license review

This repository distributes source-independent Python bytecode and Docker build
instructions; it does not vendor Python dependency wheels or container images.
The Docker build installs the pinned dependencies below. Before a release,
maintainers should retain the relevant upstream license notices with any
redistributed image or binary archive.

| Direct dependency | Pinned version | Reported upstream license | Review note |
| --- | ---: | --- | --- |
| Python | 3.11.8 | PSF License | Docker base image |
| PyTorch / torchvision | 2.2.2 / 0.17.2 | BSD-3-Clause; wheel includes third-party notices | retain wheel notices |
| MIRTorch | 0.1.2 | BSD-3-Clause | required by Cartesian SENSE base class |
| torchkbnufft | 1.4 | MIT | imported by the production operator module |
| NumPy | 1.26.4 | BSD-3-Clause | |
| SciPy | 1.12.0 | BSD-3-Clause | qMRI fitting |
| scikit-image | 0.22.0 | BSD-3-Clause and component notices | metric calculation |
| JupyterLab | 4.1.5 | BSD-3-Clause | notebook environment |

This is a release checklist, not legal advice. The repository owner must confirm the licenses for the exact pinned
distributions and ensure any applicable institutional and third-party distribution
requirements are satisfied. The repository maintainer approved distribution
of the compiled package on 2026-11-13. The project owner elected **not** to add a project `LICENSE`
file, consistent with the prior repository; this does not override the
third-party dependency license terms or grant unrestricted reuse rights.
