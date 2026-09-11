.. _SampleData:

===========
Sample Data
===========

SpinLab comes with a set of sample data (EPR, NMR, etc.) to demonstrate its usage.

Pulsed EPR Data Sets
====================


.. list-table::
  :widths: 10 120 120 100

  * - **#**
    - **Experiment**
    - **Compact-Q (Nitroxide in D2O)**
    - **E580 (BDPA/PS)**
  * - 1
    - Echo Detected Field Sweep

      :ref:`EDFS_Example`
    - :download:`Download Data Set (17478-FSED.zip) <../data/EPR/Echo-Detected Field-Sweep/17478-EDFS.zip>`
    - :download:`Download Data Set (33725-FSED.zip) <../data/EPR/Echo-Detected Field-Sweep/33725-EDFS.zip>`
  * - 2
    - Broadband Echo Detection
    - Under preparation
    - Not available
  * - 3
    - Rabi Nutation (pulse amplitude)
    - Under preparation
    - Under preparation
  * - 4
    - Rabi Nutation (pulse length)
    - Under preparation
    - Under preparation
  * - 5
    - Echo Transient (single trace)
    - Under preparation
    - Under preparation
  * - 6
    - Echo Transient (64 step phase cycle) 
    - Under preparation
    - :download:`Download Data Set (33726-ETPC.zip) <../data/EPR/Echo-Transient-Phase-Cycling/33726-ETPC.zip>`
  * - 7
    - Two-Pulse ESEEM
    - Under preparation
    - :download:`Download Data Set (33727-2PE.zip) <../data/EPR/Two-Pulse ESEEM/33727-2PE.zip>`
  * - 8
    - Three-Pulse ESEEM
    - :download:`Download Data Set (17524-3PE.zip) <../data/EPR/Three-Pulse ESEEM/17524-3PE.zip>`
    - :download:`Download Data Set (33731-3PE.zip) <../data/EPR/Three-Pulse ESEEM/33731-3PE.zip>`
  * - 9
    - Three-Pulse ESEEM vs. tau
    - Under preparation
    - :download:`Download Data Set (33732-3PEvtau.zip) <../data/EPR/Three-Pulse ESEEM vs tau/33732-3PEvtau.zip>`
  * - 10
    - Three Pulse ESEE (full transient)
    - Under preparation
    - Not available
  * - 11
    - HYSCORE
    - Under preparation
    - :download:`Download Data Set (33736-HYSCORE.zip) <../data/EPR/HYSCORE/33736-HYSCORE.zip>`
  * - 12
    - Mims ENDOR
    - Not available
    - Under preparation
  * - 13
    - Mims ENDOR vs. tau
    - Not available
    - Under preparation
  * - 14
    - Davis ENDOR
    - Not available
    - Under preparation
  * - 15
    - Inversion Recovery
    - Under preparation
    - Under preparation
  * - 16
    - Four-Pulse DEER
    - :download:`Download Data Set (33328-4PDEER.zip) <../data/EPR/Four-Pulse DEER/33328-4PDEER.zip>`
    - Under preparation
  * - 17
    - Six-Pulse DQC
    - :download:`Download Data Set (26365-6PDQC.zip) <../data/EPR/Six-Pulse DQC/26365-6PDQC.zip>`
    - Not available





CW EPR Data Sets
================

Bruker ESR5000 field-sweep absorption spectra, both the raw instrument XML and the corresponding ESRStudio ``.DSC``/``.DTA`` export. See :doc:`userGuide/loading_data` for how to load these with ``sl.load()``.

.. list-table::
  :widths: 10 90 90 90

  * - **#**
    - **Sample**
    - **Raw XML (ESR5000)**
    - **ESRStudio Export (.DSC / .DTA)**
  * - 1
    - Dark Roast Coffee

      1D CW field-sweep absorption spectrum
    - :download:`Coffee.xml <../data/esr5000/Coffee.xml>`
    - 2000 pts: :download:`.DSC <../data/esr5000/Dark roast coffee_2000pts.DSC>` / :download:`.DTA <../data/esr5000/Dark roast coffee_2000pts.DTA>`

      60000 pts: :download:`.DSC <../data/esr5000/Dark roast coffee_60000pts.DSC>` / :download:`.DTA <../data/esr5000/Dark roast coffee_60000pts.DTA>`
  * - 2
    - Bitumen

      1D CW field-sweep absorption spectrum
    - :download:`Bitumen.xml <../data/esr5000/Bitumen.xml>`
    - 2000 pts: :download:`.DSC <../data/esr5000/Bitumen_04_result_2000pts.DSC>` / :download:`.DTA <../data/esr5000/Bitumen_04_result_2000pts.DTA>`


.. NMR Data Sets
.. =============

.. .. list-table::
..   :widths: 60 60 60

..   * - **Experiment**
..     - **Compact-Q**
..     - **E580**
..   * - ESEEM
..     - Data Set 1
..     - Data Set 2
..   * - HYSCORE
..     - Data Set 1
..     - Data Set 2
..   * - DEER
..     - Data Set 1
..     - Data Set 2

