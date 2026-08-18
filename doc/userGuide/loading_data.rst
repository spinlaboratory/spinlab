============
Loading Data
============

SpinLab can import data from a wide range of spectrometer formats. The universal entry point is the ``sl.load()`` function — in most cases it detects the file format automatically from the file extension or directory contents.

.. code-block:: python

    import spinlab as sl
    data = sl.load("path/to/my/data")

The result is always a :doc:`spindata_object` ready for processing.


Automatic Format Detection
==========================

SpinLab inspects the file extension (or the contents of a directory) to determine the format. The table below shows which formats are detected automatically:

.. list-table::
   :widths: 35 30 35
   :header-rows: 1

   * - Spectrometer / Software
     - Extension / Indicator
     - Format string
   * - Bruker Xepr / Elexsys (BES3T)
     - ``.DSC``, ``.DTA``, ``.YGF``
     - ``"xepr"``
   * - Bruker WinEPR / ESP
     - ``.par``, ``.spc``
     - ``"winepr"``
   * - Bruker TopSpin (raw)
     - directory with ``acqus``
     - ``"topspin"``
   * - Bruker TopSpin (processed)
     - directory with ``procs``
     - ``"topspin pdata"``
   * - Varian / Agilent VnmrJ
     - ``.fid`` directory
     - ``"vnmrj"``
   * - JEOL Delta
     - ``.jdf``
     - ``"delta"``
   * - Magritek Prospa
     - ``.1d``, ``.2d``, ``.3d``, ``.4d``
     - ``"prospa"``
   * - FeMi SpecMan4EPR
     - ``.d01``, ``.exp``
     - ``"specman"``
   * - Tecmag TNMR
     - ``.tnt``
     - ``"tnmr"``
   * - RS2D
     - ``.xml``, ``.dat``
     - ``"rs2d"``
   * - Bruker ESR5000
     - ``.xml``
     - ``"esr5000"``
   * - VNA (S-parameters)
     - ``.s1p``, ``.s2p``
     - ``"vna"``
   * - SpinLab HDF5
     - ``.h5``
     - ``"h5"``
   * - CSV
     - (use ``sl.load_csv`` directly)
     - —

If autodetection fails, pass the format explicitly:

.. code-block:: python

    data = sl.load("path/to/data", data_format="topspin")


Format-by-Format Examples
==========================

Bruker Xepr / Elexsys (BES3T)
------------------------------

Point ``sl.load()`` at the ``.DTA`` or ``.DSC`` file. Axis files (``.XGF``, ``.YGF``, ``.ZGF``) are loaded automatically if present:

.. code-block:: python

    data = sl.load("experiment/1D_CW.DTA")
    print(data)

Bruker WinEPR / ESP
--------------------

Pass the ``.par`` or ``.spc`` file:

.. code-block:: python

    data = sl.load("spectrum.par")

Bruker TopSpin (raw FID / SER)
-------------------------------

Pass the **experiment directory** (the folder containing ``acqus``). SpinLab reads the ``fid`` or ``ser`` binary file and applies the acquisition parameters automatically:

.. code-block:: python

    data = sl.load("path/to/topspin/1/")

Bruker TopSpin (processed pdata)
---------------------------------

Pass the ``pdata/1`` subdirectory (the folder containing ``procs``):

.. code-block:: python

    data = sl.load("path/to/topspin/1/pdata/1/")

Varian / Agilent VnmrJ
-----------------------

Pass the ``.fid`` directory:

.. code-block:: python

    data = sl.load("experiment.fid/")

JEOL Delta
----------

Pass the ``.jdf`` file:

.. code-block:: python

    data = sl.load("spectrum.jdf")

Magritek Prospa
---------------

Pass the ``.1d`` (or ``.2d``, ``.3d``, ``.4d``) file:

.. code-block:: python

    data = sl.load("experiment.1d")

FeMi SpecMan4EPR
-----------------

Pass the ``.d01`` or ``.exp`` file:

.. code-block:: python

    data = sl.load("experiment.d01")

CSV Files
---------

CSV files are not handled by ``sl.load()`` — use ``sl.load_csv()`` directly. By default it expects columns: time (col 0), real (col 1), imaginary (col 2):

.. code-block:: python

    data = sl.load_csv(
        "data.csv",
        tcol=0,      # column index for the time/x axis
        real=1,      # column index for real part
        imag=2,      # column index for imaginary part
        skiprows=1,  # skip one header row
        delimiter=","
    )

SpinLab HDF5 (``.h5``)
-----------------------

HDF5 is SpinLab's own storage format (see :ref:`saving-data`). Load it exactly like any other file:

.. code-block:: python

    data = sl.load("experiment.h5")

If the ``.h5`` file contains multiple datasets (saved as a dictionary), a Python dictionary of ``SpinData`` objects is returned:

.. code-block:: python

    workspace = sl.load("workspace.h5")
    data_nmr = workspace["nmr"]
    data_epr = workspace["epr"]


Loading Multiple Files
======================

Pass a list of paths together with a ``dim`` name and a ``coord`` array to concatenate several files along a new dimension in one step. This is useful for, e.g., a power series or a time series:

.. code-block:: python

    import numpy as np

    paths  = ["power_1mW.DTA", "power_5mW.DTA", "power_10mW.DTA"]
    powers = np.array([1e-3, 5e-3, 10e-3])   # in Watts

    data = sl.load(paths, dim="power", coord=powers)
    print(data.dims)    # ['B0', 'power']
    print(data.shape)   # (2250, 3)

The individual spectra are stacked along the new ``"power"`` dimension. The ``coord`` array must have the same length as the list of paths.


.. _saving-data:

Saving Data
===========

Use ``sl.save()`` to write a ``SpinData`` object to an HDF5 file. HDF5 preserves the full object — values, axes, all attributes, and the processing audit log:

.. code-block:: python

    sl.save(data, "processed_data.h5")

To save multiple datasets in a single file, pass a dictionary:

.. code-block:: python

    workspace = {"nmr": data_nmr, "epr": data_epr}
    sl.save(workspace, "workspace.h5")

.. note::
   By default ``sl.save()`` will raise an error if the file already exists.
   Pass ``overwrite=True`` to allow overwriting:

   .. code-block:: python

       sl.save(data, "processed_data.h5", overwrite=True)


Further Reading
===============

* :doc:`spindata_object` — understand the object that ``sl.load()`` returns
* :doc:`processing` — process the data after loading
* :ref:`api-io` — full API reference for all I/O functions
