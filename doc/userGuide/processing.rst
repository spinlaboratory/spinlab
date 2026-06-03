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

``sl.cumulative_integrate()`` returns the running integral (cumulative sum), useful for visualising EPR lineshapes or calculating enhancement profiles:

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


Helpers
=======

Several utility functions assist with common data preparation tasks.

Create a complex dataset from separate real and imaginary arrays:

.. code-block:: python

    data_complex = sl.create_complex(data, real=real_data, imag=imag_data)

    # Or from two slices along a dimension (e.g. "channel")
    data_complex = sl.create_complex(data, real="channel",
                                     real_index=0, imag_index=1)

Signal-to-noise ratio calculation:

.. code-block:: python

    snr = sl.signal_to_noise(data,
                              signal_region=(-1.0, 1.0),
                              noise_region=[(-400, -200), (200, 400)])


Inspecting the Processing Log
==============================

After applying processing steps, the full audit log is available via ``proc_info()``:

.. code-block:: python

    data.proc_info()

Example output:

.. code-block:: text

     1 | window           | kind: exponential, lw: 5
     2 | fourier_transform| dim: t2, zero_fill_factor: 2, shift: True
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
