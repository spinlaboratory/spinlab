==========
Attributes
==========

Every ``SpinData`` object carries two attribute dictionaries that travel with the data through the entire processing workflow:

* **``attrs``** — the raw experimental parameters read directly from the spectrometer file. Keys and values are instrument-specific (e.g. Bruker BES3T uses ``"MF"`` for microwave frequency, TopSpin uses ``"SFO1"``).
* **``spinlab_attrs``** — a normalized layer that SpinLab populates automatically on import. It maps the instrument-specific keys to a common, format-independent set of names so that the same code works regardless of which instrument produced the data.

Both dictionaries are plain Python ``dict`` objects and can be read, updated, or extended at any time:

.. code-block:: python

    # Read a raw attribute
    print(data.attrs["MF"])              # Bruker WinEPR microwave frequency

    # Read a normalized SpinLab attribute
    print(data.spinlab_attrs["frequency"])   # same value, any format

    # Print all raw attributes in a formatted table
    data.exp_info()

    # Print all SpinLab attributes
    data.spinlab_info()


SpinLab Attributes (``spinlab_attrs``)
=======================================

The following attributes are automatically extracted and normalized on import. A value of ``None`` means the attribute is not available for a particular format.

.. list-table::
   :widths: 22 12 18 48
   :header-rows: 1

   * - Attribute
     - Unit
     - Available for
     - Description
   * - ``experiment_type``
     - —
     - All formats
     - String identifying the experiment type. Set automatically on import and used by ``sl.fancy_plot()`` to select axis labels and formatting. Can be changed manually (see below).
   * - ``data_format``
     - —
     - All formats
     - Name of the file format that was imported (e.g. ``"XEPR"``, ``"TopSpin"``, ``"WinEPR"``).
   * - ``data_type``
     - —
     - All formats
     - Technique: ``"EPR"`` or ``"NMR"``.
   * - ``scans``
     - —
     - All formats
     - Number of scans or averages accumulated.
   * - ``frequency``
     - Hz
     - All formats
     - Microwave frequency (EPR) or NMR Larmor frequency. Stored in Hz after unit conversion.
   * - ``power``
     - W
     - EPR, RS2D
     - Microwave or RF power.
   * - ``attenuation``
     - dB
     - EPR (Xepr, Xenon, WinEPR, ESP, RS2D)
     - Attenuator setting.
   * - ``pulse_attenuation``
     - dB
     - EPR (Xepr, Xenon)
     - Pulse attenuator setting (pulsed EPR).
   * - ``center_field``
     - mT
     - EPR
     - Center magnetic field of the sweep.
   * - ``sweep_field``
     - mT
     - EPR, VnmrJ, TNMR, SpecMan
     - Total field sweep width (EPR) or spectral width (NMR).
   * - ``repetition_time``
     - s
     - NMR (Prospa, Delta, VnmrJ, TNMR), SpecMan
     - Repetition time between successive scans.
   * - ``receiver_gain``
     - —
     - EPR (WinEPR, ESP), NMR (Delta, TNMR), RS2D
     - Receiver gain setting.
   * - ``receiver_attenuation``
     - dB
     - (reserved, currently None for all formats)
     - Receiver attenuation.
   * - ``conversion_time``
     - ms
     - EPR (Xepr, Xenon, WinEPR, ESP)
     - ADC conversion time per point (CW EPR).
   * - ``time_constant``
     - ms
     - EPR (Xepr, Xenon, WinEPR, ESP)
     - Filter time constant (CW EPR).
   * - ``modulation_amplitude``
     - mT
     - EPR (Xepr, Xenon, WinEPR, ESP)
     - Field modulation amplitude (CW EPR).
   * - ``modulation_frequency``
     - kHz
     - EPR (Xepr, Xenon, WinEPR, ESP)
     - Field modulation frequency (CW EPR).
   * - ``temperature``
     - K
     - EPR (Xepr, Xenon, WinEPR, ESP), NMR (Delta, VnmrJ, TNMR)
     - Sample temperature.
   * - ``dwell_time``
     - s
     - RS2D
     - Dwell time between digitizer samples.


The ``experiment_type`` Attribute
===================================

``experiment_type`` is the most important attribute in SpinLab. It is stored in ``attrs`` (not ``spinlab_attrs``) and controls how ``sl.fancy_plot()`` formats the figure — which axis labels, title, and marker style are applied.

SpinLab sets it automatically on import based on the file format. You can inspect or change it at any time:

.. code-block:: python

    print(data.attrs["experiment_type"])          # e.g. 'epr_spectrum'

    # Override to use a different plot style
    data.attrs["experiment_type"] = "inversion_recovery"

The following values are currently defined:

.. list-table::
   :widths: 35 15 50
   :header-rows: 1

   * - ``experiment_type``
     - Technique
     - Description
   * - ``epr_spectrum``
     - EPR
     - Continuous-wave EPR spectrum. Default when a CW EPR file is loaded. X-axis: magnetic field (mT).
   * - ``epr_transient``
     - EPR
     - EPR transient from a transient recorder. X-axis: time (µs).
   * - ``epr_transient_E580``
     - EPR
     - EPR transient specific to the Bruker E580 spectrometer. X-axis: time (ns).
   * - ``echo_decay``
     - EPR
     - Echo intensity as a function of pulse separation. X-axis: time (s).
   * - ``eldor_profile``
     - EPR
     - ELDOR profile. X-axis: pump frequency (GHz).
   * - ``saturation_recovery``
     - EPR
     - Saturation recovery experiment. X-axis: evolution time (s).
   * - ``inversion_recovery``
     - NMR
     - Inversion recovery experiment. X-axis: evolution time T\ :sub:`1` (s).
   * - ``polarization_buildup``
     - DNP
     - DNP polarization build-up. X-axis: contact time (s).
   * - ``enhancements_P``
     - DNP
     - DNP enhancement factor vs. microwave power. X-axis: power (dBm).
   * - ``enhancements_PdBm``
     - DNP
     - DNP enhancement factor vs. microwave power in dBm. X-axis: power (dBm).
   * - ``enhancements_PW``
     - DNP
     - DNP enhancement factor vs. microwave power in Watts. X-axis: power (W).
   * - ``sl_enhancement_profile_f``
     - DNP
     - Spin enhancement profile vs. frequency. X-axis: frequency (GHz).


Accessing Attributes
=====================

.. code-block:: python

    import spinlab as sl

    data = sl.load("spectrum.DTA")

    # --- Raw attrs ---
    print(data.attrs)                        # full dictionary
    data.exp_info()                          # formatted table printout

    print(data.attrs["experiment_type"])     # 'epr_spectrum'
    print(data.attrs["frequency"])           # microwave frequency (raw)
    print(data.attrs["nscans"])              # number of scans (Xepr raw key)

    # --- SpinLab attrs ---
    print(data.spinlab_attrs)                # full dictionary
    data.spinlab_info()                      # formatted table printout

    print(data.spinlab_attrs["frequency"])   # same frequency value, normalized
    print(data.spinlab_attrs["scans"])       # number of scans, any format
    print(data.spinlab_attrs["temperature"]) # temperature in K

    # --- Both together ---
    data.show_attrs()                        # prints spinlab_attrs + proc_attrs


Modifying Attributes
====================

Attributes can be added or changed freely. A common use case is correcting the ``experiment_type`` or adding custom metadata before saving:

.. code-block:: python

    # Change experiment type for fancy_plot formatting
    data.attrs["experiment_type"] = "echo_decay"

    # Add a custom annotation
    data.attrs["sample_name"] = "TEMPO in toluene"
    data.attrs["concentration_mM"] = 0.5

    # Save with the updated attributes — all attrs are preserved in HDF5
    sl.save(data, "annotated_data.h5")


Further Reading
===============

* :doc:`spindata_object` — full description of the ``SpinData`` object and its attributes
* :doc:`loading_data` — how attributes are populated for each file format
* :doc:`plotting` — how ``experiment_type`` controls ``fancy_plot`` output
