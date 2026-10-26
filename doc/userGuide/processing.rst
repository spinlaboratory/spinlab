================
Processing Data
================

SpinLab provides a comprehensive set of processing functions for NMR and EPR data. All functions follow the same design pattern:

* They accept a ``SpinData`` object as their first argument.
* They return a **new** ``SpinData`` object — the original is never modified.
* They automatically stamp a record of the processing step (name + parameters) into ``proc_attrs``.

A typical NMR processing workflow looks like this:

.. code-block:: python

    import spinlab as sl

    data = sl.load("path/to/fid/")           # load raw FID
    data = sl.apodize(data, lw=5)            # apply window function
    data = sl.fourier_transform(data)        # Fourier transform
    data = sl.phase(data, p0=45)             # phase correction
    data = sl.remove_background(data)        # baseline correction

    sl.plot(data)                            # plot the spectrum


Apodization (Window Functions)
==============================

``sl.apodize()`` multiplies the time-domain signal by a window function before Fourier transformation to improve sensitivity or resolution.

.. code-block:: python

    # Exponential line broadening (most common for NMR)
    data = sl.apodize(data, dim="t2", kind="exponential", lw=5)

    # Gaussian window
    data = sl.apodize(data, kind="gaussian", lw=5)

    # Hann or Hamming window (good for EPR ESEEM)
    data = sl.apodize(data, kind="hann")
    data = sl.apodize(data, kind="hamming")

    # Sin-squared (common for 2D EPR)
    data = sl.apodize(data, kind="sin2")

    # Lorentz-Gauss transformation (resolution enhancement)
    data = sl.apodize(data, kind="lorentz_gauss", lw=4, gauss_lw=8)

    # TRAF window
    data = sl.apodize(data, kind="traf", lw=5, gauss_lw=10)

Available window functions:

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - ``kind``
     - Description
   * - ``"exponential"``
     - Exponential decay — line broadening, improves sensitivity
   * - ``"gaussian"``
     - Gaussian window — line broadening with Gaussian shape
   * - ``"hann"``
     - Hann (von Hann) window — reduces spectral leakage
   * - ``"hamming"``
     - Hamming window — similar to Hann, slightly different shape
   * - ``"sin2"``
     - Sine-squared — commonly used for 2D EPR experiments
   * - ``"lorentz_gauss"``
     - Lorentz-to-Gauss transformation — resolution enhancement
   * - ``"traf"``
     - TRAF function — sensitivity/resolution compromise


Fourier Transform
=================

``sl.fourier_transform()`` performs a fast Fourier transform (FFT) along the chosen dimension. The time axis is renamed automatically (e.g. ``"t2"`` → ``"f2"``).

.. code-block:: python

    # Basic Fourier transform along t2 (default)
    data = sl.fourier_transform(data)

    # Zero-fill to twice the original length before transforming
    data = sl.fourier_transform(data, zero_fill_factor=2)

    # Fourier transform along t1 in a 2D dataset
    data = sl.fourier_transform(data, dim="t1")

    # Suppress fftshift (zero frequency stays at edge)
    data = sl.fourier_transform(data, shift=False)

.. note::
   For NMR data imported from TopSpin, the frequency axis is automatically
   converted to **ppm** using the NMR frequency stored in ``attrs``.
   Set ``convert_to_ppm=False`` to keep the axis in Hz.

The inverse Fourier transform is available as ``sl.inverse_fourier_transform()``.


Phase Correction
================

``sl.phase()`` applies zero-order (``p0``) and first-order (``p1``) phase corrections to complex spectral data.

.. code-block:: python

    # Zero-order phase correction only
    data = sl.phase(data, p0=45.0)

    # Zero- and first-order correction with a pivot point
    data = sl.phase(data, p0=45.0, p1=120.0, pivot=0.0)

    # Apply a different phase to each spectrum in a 2D dataset
    import numpy as np
    phases = np.array([10.0, 15.0, 20.0, 25.0])
    data = sl.phase(data, p0=phases)

For automated phase correction use ``sl.autophase()``:

.. code-block:: python

    # Autophase all spectra independently (entropy minimization)
    data = sl.autophase(data)

    # Autophase using a specific reference slice
    data = sl.autophase(data, reference_slice=("Average", 0))


Baseline / Background Correction
=================================

``sl.remove_background()`` fits and removes a polynomial background from the data.

.. code-block:: python

    # Remove DC offset (0th-order polynomial, most common)
    data = sl.remove_background(data)

    # Remove a linear background (1st order)
    data = sl.remove_background(data, deg=1)

    # Fit background only in specified regions (leaving signal untouched)
    data = sl.remove_background(data, deg=1, regions=[(-500, -200), (200, 500)])

    # Use a custom fitting function (e.g. exponential background)
    data = sl.remove_background(data, dim="tau",
                                func=sl.relaxation.general_exp,
                                p0=(1, -1, 900))


Alignment
=========

``sl.ndalign()`` aligns a series of spectra using FFT cross-correlation. This is useful for correcting small frequency drifts across a set of repeated measurements.

.. code-block:: python

    # Align all spectra to the last one (default reference)
    data = sl.ndalign(data)

    # Align using only a sub-region of the spectrum
    data = sl.ndalign(data, center=10.0, width=5.0)

    # Align to a specific reference spectrum
    reference = data["Average", 0]
    data = sl.ndalign(data, reference=reference)


Integration
===========

``sl.integrate()`` calculates the area under the curve using the trapezoidal rule.

.. code-block:: python

    # Integrate over the entire dimension
    result = sl.integrate(data, dim="f2")

    # Integrate over a specific region
    result = sl.integrate(data, dim="f2", regions=[(-10, 10)])

``sl.cumulative_integrate()`` returns the running integral (cumulative sum), useful for visualizing EPR lineshapes or calculating enhancement profiles:

.. code-block:: python

    data_cumint = sl.cumulative_integrate(data, dim="B0")


Conversion
==========

SpinLab provides unit conversion utilities in the ``sl.processing.conversion`` module:

.. code-block:: python

    # Convert microwave power from Watts to dBm
    power_dBm = sl.w2dBm(power_W)

    # Convert from dBm to Watts
    power_W = sl.dBm2w(power_dBm)


Axis Manipulation
=================

``sl.left_shift()`` removes points from the beginning of a time-domain signal.
This is used to discard dead-time artefacts at the start of a pulse EPR or NMR
acquisition.

.. code-block:: python

    # Remove the first 8 points from the t2 dimension
    data = sl.left_shift(data, dim="t2", shift_points=8)

``sl.reference()`` shifts the frequency axis of an NMR spectrum so that a known
peak lands at the correct chemical shift value (e.g. TMS at 0 ppm, or CDCl₃ at
7.26 ppm).

.. code-block:: python

    # Move the CHCl3 solvent peak from its measured position to 7.26 ppm
    data = sl.reference(data, dim="f2", old_ref=7.31, new_ref=7.26)

    # Reference TMS to 0 ppm
    data = sl.reference(data, dim="f2", old_ref=0.05, new_ref=0.0)


Normalization
=============

``sl.normalize()`` scales a spectrum so that its maximum absolute amplitude (or
area) equals 1, while preserving the sign of the original data.

.. code-block:: python

    # Normalize to the global maximum
    data = sl.normalize(data)

    # Normalize to the maximum within a specific spectral region
    data = sl.normalize(data, dim="f2", regions=(-5, 5))

    # Normalize to area instead of amplitude
    data = sl.normalize(data, amplitude=False)


Smoothing
=========

``sl.smooth()`` applies a Savitzky-Golay filter to reduce noise while preserving
peak shapes. The filter fits a low-order polynomial through a sliding window of
data points.

.. code-block:: python

    # Default: window of 11 points, 3rd-order polynomial
    data = sl.smooth(data)

    # Stronger smoothing
    data = sl.smooth(data, dim="B0", window_length=21, polyorder=3)

.. note::
   ``window_length`` must be odd and greater than ``polyorder``.


Pseudo-Modulation
=================

``sl.pseudo_modulation()`` numerically converts a continuous-wave (CW) EPR
absorption spectrum into its field-modulated derivative, based on the convolution
method described by Hyde et al. (*Applied Magnetic Resonance*, 1, 1990).

This avoids re-measuring with physical modulation and allows flexible
post-acquisition harmonic selection.

.. code-block:: python

    # 1st derivative (standard CW EPR presentation), field axis in Tesla
    data_mod = sl.pseudo_modulation(data, modulation_amplitude=0.001)

    # 2nd harmonic derivative
    data_mod = sl.pseudo_modulation(data, modulation_amplitude=0.001, order=2)

    # Specify the field dimension explicitly
    data_mod = sl.pseudo_modulation(data, modulation_amplitude=0.001, dim="B0")

.. note::
   The unit of ``modulation_amplitude`` must match the unit of the field axis
   (e.g. T if the axis is in Tesla, mT if in millitesla).


Enhancement Calculation
=======================

``sl.calculate_enhancement()`` computes signal enhancements from a power series.
It expects a ``SpinData`` object whose ``experiment_type`` attribute is
``"integrals"`` (i.e. the output of ``sl.integrate()`` applied to an Overhauser
DNP or ELDOR dataset).

.. code-block:: python

    # Full DNP enhancement workflow
    data     = sl.load("path/to/dnp_data")
    spectrum = sl.fourier_transform(data)
    integrals = sl.integrate(spectrum, dim="f2", regions=[(-5, 5)])
    enhancements = sl.calculate_enhancement(integrals)

    sl.fancy_plot(enhancements)


Complex Data
============

``sl.create_complex()`` combines separate real and imaginary arrays into a single
complex ``SpinData`` object. Two calling styles are supported.

**From explicit arrays** — pass the real and imaginary numpy arrays directly:

.. code-block:: python

    data_complex = sl.create_complex(data,
                                     real=data.values[..., 0],
                                     imag=data.values[..., 1])

**From a dimension** — when a dataset stores real and imaginary parts as two
slices along a named dimension (e.g. ``"channel"``), pass the dimension name:

.. code-block:: python

    # Combine channel index 0 (real) and index 1 (imag) into a complex dataset
    data_complex = sl.create_complex(data, real="channel",
                                     real_index=0, imag_index=1)

The source dimension is collapsed and removed from the output object.


Signal-to-Noise Ratio
=====================

``sl.signal_to_noise()`` estimates the SNR of a spectrum by comparing the peak
amplitude in a signal region to the standard deviation of the noise in one or more
baseline regions.

.. code-block:: python

    # Signal near 0 ppm, noise in the wings
    snr = sl.signal_to_noise(data,
                              signal_region=(-1.0, 1.0),
                              noise_region=[(-400, -200), (200, 400)])

    # With automatic background removal before noise estimation
    snr = sl.signal_to_noise(data,
                              signal_region=(-1.0, 1.0),
                              noise_region=[(200, 400)],
                              remove_background=[(200, 400)])

The return value is a ``SpinData`` object whose ``"signal_region"`` dimension
holds one SNR value per input spectrum (useful for 2D datasets).


Inspecting the Processing Log
==============================

After applying processing steps, the full audit log is available via ``proc_info()``:

.. code-block:: python

    data.proc_info()

Example output:

.. code-block:: text

     1 | window           | kind: exponential, lw: 5
     2 | fourier_transform | dim: t2, zero_fill_factor: 2, shift: True
     3 | phase            | p0: 45.0, p1: 0.0, pivot: None
     4 | remove_background| dim: f2, deg: 0, regions: None


Full NMR Processing Example
============================

.. code-block:: python

    import spinlab as sl

    # 1. Load raw FID from TopSpin
    data = sl.load("experiment/1/")

    # 2. Apply exponential line broadening (5 Hz)
    data = sl.apodize(data, dim="t2", kind="exponential", lw=5)

    # 3. Fourier transform with 2x zero-filling
    data = sl.fourier_transform(data, zero_fill_factor=2)

    # 4. Phase correction
    data = sl.phase(data, p0=12.5)

    # 5. Remove linear baseline
    data = sl.remove_background(data, deg=1)

    # 6. Plot
    sl.plt.figure()
    sl.plot(data)
    sl.plt.xlabel("Chemical shift (ppm)")
    sl.plt.tight_layout()
    sl.plt.show()

    # 7. Save the processed spectrum
    sl.save(data, "processed.h5")


Full EPR ESEEM Processing Example
===================================

.. code-block:: python

    import spinlab as sl

    # 1. Load raw ESEEM time trace
    data = sl.load("eseem_data.d01")

    # 2. Remove background decay
    data = sl.remove_background(data, dim="t2", deg=3)

    # 3. Apply Hamming window
    data = sl.apodize(data, dim="t2", kind="hamming")

    # 4. Fourier transform with 4x zero-filling
    data = sl.fourier_transform(data, zero_fill_factor=4)

    # 5. Take the absolute value
    import numpy as np
    data.values = np.abs(data.values)

    # 6. Plot the ESEEM spectrum
    sl.plt.figure()
    sl.plot(data)
    sl.plt.xlabel("Frequency (MHz)")
    sl.plt.tight_layout()
    sl.plt.show()


Further Reading
===============

* :doc:`spindata_object` — the ``SpinData`` object that all functions operate on
* :doc:`loading_data` — how to load data before processing
* :doc:`plotting` — how to visualize the results
* :ref:`api-processing` — full API reference for all processing functions
