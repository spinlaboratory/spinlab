===================
The SpinData Object
===================

The ``SpinData`` object is the central data structure in SpinLab. Every time data is loaded from a file — or created manually — SpinLab returns a ``SpinData`` object. All processing, analysis, and plotting functions operate on ``SpinData`` objects.

Understanding its structure is the most important step to working effectively with SpinLab.


Overview
========

A ``SpinData`` object bundles five things together:

.. list-table::
   :widths: 20 80

   * - **values**
     - The actual data, stored as a NumPy ``ndarray`` (can be real or complex, any dtype)
   * - **dims**
     - A list of strings labeling each dimension of ``values`` (e.g. ``['B0']``, ``['t2', 't1']``)
   * - **coords**
     - A list of 1D NumPy arrays — one per dimension — giving the physical axis values
   * - **attrs**
     - A dictionary of experimental parameters imported from the spectrometer file
   * - **proc_attrs**
     - An automatically maintained audit log of every processing step applied to the object

The key design principle is that **dims and coords always travel with the data**. When you slice, add, or Fourier-transform a ``SpinData`` object, the axes are updated automatically. You never lose track of what the numbers mean.


Creating a SpinData Object
==========================

SpinLab creates ``SpinData`` objects automatically when you load a file:

.. code-block:: python

    import spinlab as sl
    data = sl.load("path/to/my_spectrum.DTA")

You can also create one manually, which is useful for testing or for wrapping data you have computed yourself:

.. code-block:: python

    import numpy as np
    import spinlab as sl

    x = np.linspace(330, 360, 1024)          # magnetic field axis in mT
    y = sl.math.lineshape.lorentzian(x, 345, 1.0)  # simulated EPR line

    data = sl.SpinData(
        values = y,
        dims   = ["B0"],
        coords = [x],
        attrs  = {"experiment_type": "epr_spectrum", "mw_frequency": 9.8e9}
    )

For a 2D dataset (e.g. 1024 field points × 10 averages):

.. code-block:: python

    field  = np.linspace(330, 360, 1024)
    scans  = np.arange(10)
    values = np.random.randn(1024, 10)

    data_2d = sl.SpinData(
        values = values,
        dims   = ["B0", "Average"],
        coords = [field, scans]
    )

.. note::
   The order of ``dims`` and ``coords`` must match the axis order of ``values``.
   ``values.shape[0]`` must equal ``len(coords[0])``, and so on.


The Four Core Attributes
========================

values
------

The raw data, always a NumPy ``ndarray``. You can read and write it directly:

.. code-block:: python

    print(data.values)          # the numpy array
    print(data.values.shape)    # e.g. (1024,) for 1D or (1024, 10) for 2D
    print(data.values.dtype)    # e.g. float64, complex128

    data.values = data.values * 2   # scale the data in-place

dims
----

A Python list of strings — one label per dimension. Labels are used throughout SpinLab to identify axes by name rather than by integer index, making code more readable and less error-prone:

.. code-block:: python

    print(data.dims)        # e.g. ['B0'] or ['t2', 't1']

    # Rename a dimension
    data.rename("B0", "field")
    print(data.dims)        # ['field']

coords
------

A ``Coords`` object (behaves like a list of NumPy arrays). Each entry corresponds to one dimension and holds the physical axis values. You can access individual axes by name or by integer index:

.. code-block:: python

    print(data.coords["B0"])       # field axis array
    print(data.coords[0])          # same, by integer index

    # Replace an axis
    data.coords["B0"] = np.linspace(330, 360, 1024)

attrs
-----

A plain Python dictionary holding experimental parameters that were read from the spectrometer file — things like microwave frequency, temperature, number of scans, modulation amplitude, etc.:

.. code-block:: python

    print(data.attrs)                      # all parameters
    print(data.attrs["mw_frequency"])      # single parameter

    data.attrs["my_key"] = "my_value"     # add a new entry

A particularly important key is ``experiment_type``, which controls how SpinLab's ``fancy_plot`` function labels and formats the figure. It is set automatically on import, but can be changed:

.. code-block:: python

    data.attrs["experiment_type"] = "epr_spectrum"


Printing a SpinData Object
==========================

Calling ``print()`` on a ``SpinData`` object gives a compact summary of its contents:

.. code-block:: python

    print(data)

Example output for a 1D EPR spectrum:

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

To print the full ``attrs`` dictionary without truncation use ``data.exp_info()``.


Inspecting Attributes
=====================

SpinLab provides three convenience methods for printing the different attribute dictionaries in a formatted table:

.. code-block:: python

    data.exp_info()        # print experimental parameters (attrs)
    data.spinlab_info()    # print internal SpinLab parameters
    data.proc_info()       # print processing audit log

    data.show_attrs()      # print spinlab_info + proc_info together

The processing audit log (``proc_info``) is particularly useful for reproducibility — it records every processing step that has been applied to the object, along with the parameters used:

.. code-block:: text

     1 | fourier_transform | dim: t2, zero_fill_factor: 2
     2 | apodization       | dim: t2, linewidth: 10
     3 | phase             | p0: -12.4, p1: 0.0


Key Methods
===========

copy
----

Returns a deep copy of the object. Always use ``copy()`` before modifying data if you want to keep the original unchanged — all SpinLab processing functions do this internally:

.. code-block:: python

    data_copy = data.copy()

squeeze
-------

Removes all dimensions of length 1. This is commonly needed after indexing, which retains the indexed dimension even when only one slice is selected:

.. code-block:: python

    data_slice = data["t1", 3]   # shape is (1024, 1) — t1 dimension kept
    data_slice.squeeze()          # shape becomes (1024,)

rename
------

Renames a dimension in-place. The corresponding ``coords`` entry is updated automatically:

.. code-block:: python

    data.rename("x0", "t1")

select
------

Selects a subset of slices from a 2D object. Accepts integers, ``range`` objects, or a list/tuple mixing both:

.. code-block:: python

    data.select(3)                    # single slice at index 3
    data.select(range(2, 8))          # slices 2 through 7
    data.select((1, range(5, 10), 15))  # slices 1, 5–9, and 15

add_proc_attrs
--------------

Stamps a processing step into the audit log. This is called automatically by every SpinLab processing function, but you can also call it manually to record custom steps:

.. code-block:: python

    data.add_proc_attrs("my_custom_step", {"param1": 1.0, "param2": "value"})


Arithmetic Operations
=====================

``SpinData`` objects support standard arithmetic operators directly. Operations are applied element-wise to ``values``:

.. code-block:: python

    # With scalars or numpy arrays
    data_scaled  = data * 2.0
    data_shifted = data + 1000

    # Between two SpinData objects — axes are aligned automatically
    data_sum  = data_a + data_b
    data_diff = data_a - data_b
    data_prod = data_a * data_b
    data_div  = data_a / data_b

SpinLab also has basic NumPy compatibility, so many NumPy functions (e.g. ``np.abs``, ``np.real``, ``np.imag``) work directly on ``SpinData`` objects and return a ``SpinData`` object with the correct axes intact.


Further Reading
===============

* :doc:`indexing` — detailed guide to slicing and selecting data by index, integer, and float
* :doc:`plotting` — how to plot ``SpinData`` objects using ``sl.plot()`` and ``sl.fancy_plot()``
* :doc:`../api/core` — full API reference for the ``SpinData`` class and related modules
