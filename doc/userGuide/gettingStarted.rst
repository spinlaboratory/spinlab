===============
Getting Started
===============

This page walks you through the first steps with SpinLab: loading a real data file, inspecting the result, processing the data, and plotting the spectrum. The entire workflow takes less than 10 minutes.

.. note::
   Before starting, make sure SpinLab is installed. See :doc:`../installation` for instructions. SpinLab requires **Python 3.10 or higher**.


Step 1 — Import SpinLab
========================

Open a terminal (e.g. Windows PowerShell, macOS Terminal, or a Jupyter notebook) and import SpinLab:

.. code-block:: python

    import spinlab as sl

SpinLab is imported under the alias ``sl`` by convention. All SpinLab functions are accessible via this alias (e.g. ``sl.load()``, ``sl.plot()``).


Step 2 — Load a Data File
==========================

SpinLab can load many different spectrometer formats. In most cases the file format is detected automatically from the file extension:

.. code-block:: python

    data = sl.load("data/bes3t/1D_CW.DTA")

The result is a :doc:`spindata_object` — SpinLab's central data container. It holds the spectral values together with the axis coordinates and experimental parameters.

To see a summary of what was loaded:

.. code-block:: python

    print(data)

Example output:

.. code-block:: text

    values:
        2250 ndarray (float64)
    dims:
        ['B0']
    coords:
        array([342.055, 342.062, ..., 357.048], shape=(2250,))
    attrs:
        'experiment_type': 'epr_spectrum'
        'mw_frequency': 9.804448
        'center_field': 3495.55
        'power': 1.002
        +12 attrs

The object contains:

* **values** — the spectral data as a NumPy array (2250 points)
* **dims** — the dimension label (``'B0'``, the magnetic field axis)
* **coords** — the field values in mT
* **attrs** — experimental parameters read directly from the file

See :doc:`loading_data` for examples of every supported file format.


Step 3 — Inspect the Data
==========================

You can access any part of the object directly:

.. code-block:: python

    print(data.values.shape)          # (2250,)
    print(data.dims)                  # ['B0']
    print(data.coords["B0"])          # field axis array in mT
    print(data.attrs["mw_frequency"]) # 9.804448 GHz

To see all experimental parameters in a formatted table:

.. code-block:: python

    data.exp_info()


Step 4 — Plot the Spectrum
===========================

Use ``sl.plot()`` to quickly visualize the data:

.. code-block:: python

    sl.plt.figure()
    sl.plot(data)
    sl.plt.tight_layout()
    sl.plt.show()

SpinLab imports Matplotlib internally and exposes the full ``pyplot`` module as ``sl.plt``. Any Matplotlib command works:

.. code-block:: python

    sl.plt.figure()
    sl.plot(data)
    sl.plt.xlabel("Magnetic Field (mT)")
    sl.plt.ylabel("Intensity (a.u.)")
    sl.plt.title("CW EPR Spectrum")
    sl.plt.tight_layout()
    sl.plt.show()

For publication-ready figures with automatic axis labels and formatting based on the experiment type, use ``sl.fancy_plot()``:

.. code-block:: python

    sl.plt.figure()
    sl.fancy_plot(data)
    sl.plt.show()

See :doc:`plotting` for the full list of supported experiment types and plot options.


Step 5 — Process the Data
==========================

SpinLab processing functions always take a ``SpinData`` object as input and return a new one — the original is never modified.

A typical NMR processing sequence (load → apodize → Fourier transform → phase):

.. code-block:: python

    # Load a raw NMR FID from TopSpin
    data = sl.load("experiment/1/")

    # Apply exponential line broadening (5 Hz)
    data = sl.apodize(data, dim="t2", kind="exponential", lw=5)

    # Fourier transform with 2x zero-filling
    data = sl.fourier_transform(data, zero_fill_factor=2)

    # Phase correction
    data = sl.phase(data, p0=12.5)

    # Plot the spectrum
    sl.plt.figure()
    sl.plot(data)
    sl.plt.show()

Every processing step is automatically recorded in the audit log. To inspect it:

.. code-block:: python

    data.proc_info()

See :doc:`processing` for the complete processing reference.


Step 6 — Save the Result
=========================

Save the processed data to SpinLab's HDF5 format, which preserves the full object including axes and the processing audit log:

.. code-block:: python

    sl.save(data, "processed_spectrum.h5")

Reload it at any time with:

.. code-block:: python

    data = sl.load("processed_spectrum.h5")


Next Steps
==========

* :doc:`spindata_object` — understand the ``SpinData`` object in depth
* :doc:`loading_data` — load data from every supported file format
* :doc:`processing` — full processing reference with examples
* :doc:`indexing` — slice and select subsets of your data
* :doc:`plotting` — create publication-quality figures
* :ref:`api-reference` — complete API reference
