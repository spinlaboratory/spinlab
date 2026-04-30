=============
Plotting Data
=============

SpinLab uses MatplotLib to plot data and the entire ``pyplot`` module of matplotlib is available in SpinLab. For example after importing SpinLab the pyplot ``figure()`` commands can be used in the following way:


.. code-block:: python

    >>> import spinlab as sl
    >>> sl.plt.figure()

Fancy Plot
==========
SpinLab has a built-in plotting function called ``fancy_plot`` to generate publication ready figures. The appearance of the figure is controlled by the attribute ``experiment-type`` of the sldata object. This attribute is set automatically, when a data set is imported and the axis labeling, (default) title, appearance is controlled through the value of this sldata object attribute.

The following table gives a list of available attributes. These parameters are defined in the SpinLab configuration file.


.. list-table::
  :widths: 10 50 50 120

  * - **#**
    - **Attribute**
    - **Type**
    - **Description**
  * - 1
    - `echo_decay`
    - EPR
    - Echo intensity measured as a function of the pulse separation
  * - 2
    - `eldor_profile`
    - EPR
    - ELDOR profile
  * - 3
    - `enhancements_P`
    - DNP
    - Description
  * - 4
    - `enhancements_PdBm`
    - DNP
    - Description
  * - 5
    - `enhancements_PW`
    - DNP
    - Description
  * - 6
    - `epr_spectrum`
    - EPR
    - Description
  * - 7
    - `epr_transient`
    - EPR
    - Description
  * - 8
    - `epr_transient_E580`
    - EPR
    - Description
  * - 9
    - `inversion_revovyer`
    - EPR/NMR
    - Description
  * - 10
    - `polarization_buildup`
    - DNP
    - Description
  * - 11
    - `saturation_recovery`
    - EPR/NMR
    - Description
  * - 12
    - `sl_enhancement_profile_f`
    - EPR/NMR
    - Description

Generic Plotting Function
=========================
If no experimnent type is specified, SpinLab has a generic plotting function to plot a SpinLab data object (here data). Simply use the ``sl.plot()`` command:

.. code-block:: python

    >>> sl.plot(data)

