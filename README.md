[![PyPI version](https://img.shields.io/pypi/v/spinlab)](https://pypi.org/project/spinlab/)
[![Python Version](https://img.shields.io/pypi/pyversions/spinlab)](https://www.python.org/downloads/)
[![Downloads](https://pepy.tech/badge/spinlab/month)](https://pepy.tech/project/spinlab)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# SpinLab — Bringing the Power of Python to MR Spectroscopy

SpinLab is an open-source, object-oriented Python package for importing, processing, and analyzing data from:

- [Electron Paramagnetic Resonance (EPR)](https://en.wikipedia.org/wiki/Electron_paramagnetic_resonance) spectroscopy
- [Nuclear Magnetic Resonance (NMR)](https://en.wikipedia.org/wiki/Nuclear_magnetic_resonance) spectroscopy
- [Dynamic Nuclear Polarization (DNP)](https://en.wikipedia.org/wiki/Dynamic_nuclear_polarization) spectroscopy

**Documentation:** [spinlaboratory.com](https://spinlaboratory.com)

---

## Features

- **Universal data import** — load data from 13 spectrometer formats with automatic format detection
- **N-dimensional data objects** — the `SpinData` object keeps data, axes, and experimental parameters together at all times
- **Comprehensive processing** — apodization (7 window functions), Fourier transform with zero-filling, phase correction, baseline removal, alignment, integration, and more
- **Analysis tools** — relaxation fitting, peak finding, DNP enhancement profile simulation
- **Publication-quality figures** — `fancy_plot()` automatically applies axis labels and formatting based on the experiment type
- **Processing audit log** — every processing step is automatically recorded with its parameters for full reproducibility
- **HDF5 save/load** — store complete `SpinData` objects including axes, attributes, and audit log

---

## Supported File Formats

| Spectrometer / Software | Extension |
|------------------------|-----------|
| Bruker Xepr / Elexsys (BES3T) | `.DSC`, `.DTA` |
| Bruker WinEPR / ESP | `.par`, `.spc` |
| Bruker TopSpin | experiment directory |
| Varian / Agilent VnmrJ | `.fid` directory |
| JEOL Delta | `.jdf` |
| Magritek Prospa | `.1d`, `.2d`, `.3d`, `.4d` |
| FeMi SpecMan4EPR | `.d01`, `.exp` |
| Tecmag TNMR | `.tnt` |
| RS2D | `.xml`, `.dat` |
| VNA (S-parameters) | `.s1p`, `.s2p` |
| SpinLab HDF5 | `.h5` |
| CSV | (via `sl.load_csv()`) |

---

## Quick Start

```python
import spinlab as sl

# Load data — format detected automatically
data = sl.load("spectrum.DTA")

# Inspect the data object
print(data)

# Plot
sl.plt.figure()
sl.plot(data)
sl.plt.show()
```

**NMR processing workflow:**

```python
import spinlab as sl

data = sl.load("experiment/1/")                         # load TopSpin FID
data = sl.apodize(data, kind="exponential", lw=5)       # line broadening
data = sl.fourier_transform(data, zero_fill_factor=2)   # FFT with zero-filling
data = sl.phase(data, p0=12.5)                          # phase correction
data = sl.remove_background(data, deg=1)                # baseline correction

sl.plt.figure()
sl.plot(data)
sl.plt.show()

sl.save(data, "processed.h5")                           # save result
```

---

## Installation

SpinLab requires **Python 3.10 or higher**.

```console
pip install spinlab
```

To upgrade an existing installation:

```console
pip install --upgrade spinlab
```

---

## Documentation

Full documentation including user guides, processing reference, and API reference is available at:

**[spinlaboratory.com](https://spinlaboratory.com)**

---

## Development

Contributions are welcome! See the [Contributing Guide](https://spinlaboratory.com/contributing.html) for details on setting up a development environment, running tests, and opening pull requests.

```console
git clone https://github.com/SpinLab/spinlab
cd spinlab
pip install -e spinlab
python -m pytest
```

---

## Citing SpinLab

If you use SpinLab to process data for a publication, please add a reference to the [SpinLab documentation](https://spinlaboratory.com) in your Materials and Methods section.

---

## Authors

**Current maintainers:**
Timothy Keller, Yen-Chun Huang, Thorsten Maly

**SpinLab originally started as [DNPLab](https://github.com/DNPLab/DNPLab), created by:**
- [Bridge12 Technologies, Inc.](http://www.bridge12.com/)
- [Han Lab, Northwestern University](https://hanlab.northwestern.edu/)
- [Franck Lab, Syracuse University](https://jmfrancklab.github.io/)

---

## License

SpinLab is released under the [MIT License](LICENSE.txt).
