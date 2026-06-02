=================
Getting Started
=================

The following is a simple example to show how to import, process, and plot data using SpinLab. For this, we will be using some sample data that is distributed with the SpinLab package. For this example all commands are executed in a terminal window.

In a terminal window (e.g. Windows PowerShell) start Python and execute the following commands:

.. code-block:: bash

    $ Python
    Python 3.11.9 (tags/v3.11.9:de54cf5, Apr  2 2024, 10:12:12) [MSC v.1938 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.

    >>> import spinlab as sl
    >>>

.. code-block:: bash

    >>> data = sl.load("data/bes3t/1D_CW.DTA")
    >>>

.. code-block:: bash

    >>> data
    nddata(values = array([-0.56268479, -0.56062199, -0.54530182, ..., -0.53001783,
       -0.53928231, -0.54952391], shape=(2250,)), coords = Coords([array([342.055     , 342.06166667, 342.06833333, ..., 357.03499997,
       357.04166663, 357.0483333 ], shape=(2250,))]), dims = ['B0'], attrs = {'data_dim': 1, 'x_unit': 'G', 'frequency': 9.804448, 'center_field': 3495.55, 'power': 1.002, 'attenuation': 23, 'nscans': 2, 'conversion_time': 20.0, 'modulation_amplitude': 1.0, 'modulation_frequency': 100.0, 'time_constant': 10.24, 'temperature': 295.0, 'x_dim': 1, 'spectrometer_format': 'xepr', 'experiment_type': 'epr_spectrum', 'nrScans': 2})
    >>>

.. code-block:: bash

    >>> sl.plt.figure()
    <Figure size 640x480 with 0 Axes>
    >>> sl.plot(data)
    [<matplotlib.lines.Line2D object at 0x000002283662B1D0>]
    >>> sl.plt.show()
    >>>

SpinLab can import many different file formats created by different spectrometers (e.g. Bruker ElexSys, SpecMan4EPR, ...). In most cases SpinLab will be able to detect the file format based on the file extension.

When importing the experimental data SpinLab will automatically create a SpinLab data object (sldata object) called `data`. When printing the content of the sldata object in a terminal window, you will get an idea of the structure of the object. The object typically contains:

    * **values**: These are the data values (e.g. the spectrum) typically stored in a numpy array.
    * **dims**: This describes the dimensions. In this example a field axis called B0.
    * **coords**: These are the values of the detected coordinates. Here, the magnetic field values.
    * **attrs**: Imported attributes.

The SpinLab command ``plot()`` is a built-in command to easily plot the values of the sldata object and is not part of Matplotlib. SpinLab uses Matplotlib to plot data and the Python package is a requirement when installing SpinLab. For convience, SpinLab imports Matplotlib and all commands of the pyplot module are accessible in SpinLab using the ``sl.plt.`` command prefix (e.g. ``sl.plt.figure()``, ``sl.plt.show()``).
