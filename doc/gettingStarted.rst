=================
Getting Started
=================

The following is a very simple example to show how to import, process, and plot data using SpinLab. For this, we will be using some sample data that is distributed with the SpinLab package. In this first example all commands are executed in a terminal window.

Import Data
===========

To get started, open a terminal window (e.g. Windows PowerShell) and launch Python:

.. code-block:: bash

    $ Python
    Python 3.11.9 (tags/v3.11.9:de54cf5, Apr  2 2024, 10:12:12) [MSC v.1938 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>>

Next import the SpinLab Python package,

.. code-block:: bash

    >>> import spinlab as sl
    >>>

followed by importing an EPR spectrum. DNPLab can import many different file formats created by different spectrometers (e.g. Bruker ElexSys, SpecMan4EPR, ...). In most cases SpinLab will be able to detect the file format based on the file extension. In this example we will load a cw EPR specrum recorded on a Bruker EMX spectrometer:

.. code-block:: bash

    >>> data = sl.load("data/bes3t/1D_CW.DTA")
    >>>

SpinLab will import the experimental data and will automatically create a SpinLab data object (sldata object) called `data`. You can examine the data object by simply typing the data object name followed by a return:

.. code-block:: bash

    >>> data
    nddata(values = array([-0.56268479, -0.56062199, -0.54530182, ..., -0.53001783,
       -0.53928231, -0.54952391], shape=(2250,)), coords = Coords([array([342.055     , 342.06166667, 342.06833333, ..., 357.03499997,
       357.04166663, 357.0483333 ], shape=(2250,))]), dims = ['B0'], attrs = {'data_dim': 1, 'x_unit': 'G', 'frequency': 9.804448, 'center_field': 3495.55, 'power': 1.002, 'attenuation': 23, 'nscans': 2, 'conversion_time': 20.0, 'modulation_amplitude': 1.0, 'modulation_frequency': 100.0, 'time_constant': 10.24, 'temperature': 295.0, 'x_dim': 1, 'spectrometer_format': 'xepr', 'experiment_type': 'epr_spectrum', 'nrScans': 2})

This will plot the content of the data object, for example the data values (values), the detected coordinates (coords), dimension (dims), and imported attributes (attrs). Examining the sldata object in a terminal window is often helpful to understand the imported data structure. Alternatively, you can plot the data. SpinLab uses Matplotlib to plot data and the Python package is a requirement when installing SpinLab.

For convience, SpinLab imports Matplotlib and all commands of the pyplot module are accessible in SpinLab using the ``sl.plt`` command prefix. To plot the sldata object use the following commands ``sl.plt.figure()``, followed by ``sl.plot(data)``, and ``sl.plt.show()``:

.. code-block:: bash

    >>> sl.plt.figure()
    <Figure size 640x480 with 0 Axes>
    >>> sl.plot(data)
    [<matplotlib.lines.Line2D object at 0x000002283662B1D0>]
    >>> sl.plt.show()
    >>>

The SpinLab ``plot()`` is a built-in command to easily plot the values of the sldata object and is not part of Matlplotlib.


Process Data
============



.. # %%
.. # Process EPR Data
.. # ----------------
.. # In this section, we will demonstrate some basic EPR processing.

.. # %%
.. # First, let's perform a baseline correction using a zeroth order polynomial to remove a DC offset:
.. data_proc = dnp.remove_background(data, dim="B0")

.. # %%
.. # Here a new dnpData object is created containing the corrected data. This is helpful, if the processing for different data sets need to be compared. The remove_background function will calculate a zero order polynomial background and will subtract this value from the data. To plot the corrected spectrum simply use:



Plot Results
============

.. dnp.fancy_plot(data_proc, xlim=[344, 354], title="EPR Spectrum")

.. # %%
.. # The ''fancy_plot'' function is very helpful to create simple plots. For more complicated figures the matplotlib functions can be used. Note, that the plotting functions of the matplotlib package are already loaded into the DNPLab environment.

.. dnp.plt.figure()
.. dnp.plt.plot(data.coords["B0"], data.values.real, label="No Background Correction")
.. dnp.plt.plot(
..     data_proc.coords["B0"], data_proc.values.real, label="Background Correction"
.. )
.. dnp.plt.xlabel("Magnetic Field (mT)")
.. dnp.plt.ylabel("EPR Signal Intensity (a.u.)")
.. dnp.plt.grid(True)
.. dnp.plt.tight_layout()
.. dnp.plt.legend()
.. dnp.plt.show()

.. # %%
.. # Note the DC offset of about -0.5.

.. # %%
.. # Show EPR Attributes
.. # -------------------
.. # To show a list of attributes with the EPR spectrum

.. dnp.fancy_plot(data_proc, xlim=[344, 354], title="EPR Spectrum", showPar=True)
.. dnp.plt.show()


