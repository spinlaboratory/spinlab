=========
Changelog
=========

All notable changes to SpinLab are documented here.
The versioning follows `Semantic Versioning <https://semver.org/>`_.


Version 1.1.3 (current)
========================

*Released 2026*

**Bug fixes and improvements**

* Improved documentation coverage across all modules
* Fixed typos and grammar errors in docstrings and documentation pages
* Corrected ``load_pdata`` docstring (was incorrectly labelled as Prospa)
* Fixed return unit description in ``w2dBm`` (was incorrectly stated as W instead of dBm)
* Fixed processing audit log attribute name ``cumlative_integrate`` → ``cumulative_integrate``
* Corrected ``dpph_neat`` key reference in ``radicalProperties`` docstring


Version 1.1.0
=============

*Released 2024*

**New features**

* Added ``simulate_enhancement_profiles`` module for Spin enhancement profile simulation
* Added ``rs2d`` I/O module for RS2D file format support
* Extended processing module with ``average``, ``conversion``, and ``interpolation`` submodules
* Added ``fancy_plot`` function with automatic axis labeling based on experiment type


Version 1.0.0
=============

*Released 2024*

**Initial stable release of SpinLab**

SpinLab was created from DNPLab and significantly extended to support both EPR and NMR data.

**Supported file formats**

* Bruker BES3T (Xepr / Elexsys)
* Bruker WinEPR / ESP
* Bruker TopSpin (raw FID and processed pdata)
* Varian / Agilent VnmrJ
* JEOL Delta
* Magritek Prospa
* FeMi SpecMan4EPR
* Tecmag TNMR
* RS2D
* VNA S-parameter files
* SpinLab HDF5

**Core modules**

* ``spinlab.core`` — ``SpinData`` N-dimensional data object with named axes
* ``spinlab.io`` — unified ``load()`` / ``save()`` interface with format autodetection
* ``spinlab.processing`` — apodization, FFT, phasing, alignment, integration, baseline
* ``spinlab.analysis`` — relaxation fitting, peak finding, enhancement profiles
* ``spinlab.math`` — lineshape functions, relaxation models, window functions, pulse shapes
* ``spinlab.plotting`` — publication-quality figures, stack plots, image plots
* ``spinlab.constants`` — MR properties for 100+ nuclei and selected radicals
* ``spinlab.fitting`` — general curve fitting framework
