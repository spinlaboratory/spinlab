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

The following table gives a list of available attributes. The parameters are defined in the SpinLab configuration file.

To have the data plotted in a a specific plot, change the ``experiment-type`` attribute after loading the data. For example to show an EPR transient in the correct format:

.. code-block:: python

    >>> import spinlab as sl
    >>> data = sl.load("Path to my data set")
    >>> data.attrs["experiment-type"] = "epr_transient"



EPR Specific Plots
------------------

.. list-table::
  :widths: 10 50 50 120

  * - **#**
    - **Attribute**
    - **Type**
    - **Description**
  * - 1
    - `echo_decay`
    - EPR
    - Plot the echo intensity measured as a function of the pulse separation at a static magnetic field position
  * - 2
    - `eldor_profile`
    - EPR
    - Plot the ELDOR profile versus the pump frequency.
  * - 3
    - `epr_spectrum`
    - EPR
    - This is a standard EPR spectrum. It is the default when an EPR measurement is loaded using SpinLab.
  * - 4
    - `epr_transient`
    - EPR
    - EPR transient from the transient recorder. The signal intensity is plotted as a function of the time.
  * - 5
    - `epr_transient_E580`
    - EPR
    - EPR transient from the transient recorder. The signal intensity is plotted as a function of the time. This attribute is specific to when data from the Bruker E580 is imported.
  * - 6
    - `inversion_revovyery`
    - EPR
    - Inversion recovery experiment. The echo (or FID) amplitude is plotted as a function of the time separating the inversion pulse from the detection sequence.
  * - 7
    - `saturation_recovery`
    - EPR 
    - Saturation recovery experiment. The echo (or FID) amplitude is plotted as a function of the time separating the saturation pulse from the detection sequence.


NMR/DNP Specific Plots
----------------------

.. list-table::
  :widths: 10 50 50 120

  * - **#**
    - **Attribute**
    - **Type**
    - **Description**
  * - 1
    - `enhancements_P`
    - DNP
    - Plotting the DNP enhancement factor as a function of the applied microwave power in Watt (W).
  * - 2
    - `enhancements_PdBm`
    - DNP
    - Plotting the DNP enhancement factor as a function of the applied microwave power in dBm.
  * - 3
    - `enhancements_PW`
    - DNP
    - Plotting the DNP enhancement factor as a function of the applied microwave power in Watt (W).
  * - 4
    - `inversion_revovyer`
    - NMR
    - Inversion recovery experiment. The signal amplitude is plotted as a function of the time separating the inversion pulse from the detection sequence.
  * - 5
    - `polarization_buildup`
    - DNP
    - Plotting the DNP enhancement factor as a function of the polarization time.
  * - 6
    - `sl_enhancement_profile_f`
    - DNP
    - Plotting the DNP enhancement factor as a function of the frequency.


Generic Plotting Function
=========================
If no experimnent type is specified, SpinLab has a generic plotting function to plot a SpinLab data object (here data). Simply use the ``sl.plot()`` command:

.. code-block:: python

    >>> import spinlab as sl
    >>> data = sl.load("Path to my data set")
    >>> sl.plot(data)

