=======
Modules
=======

SpinLab is structured into several different Python modules according to their specific tasks. The individual functions are located inside these modules.

The following modules are currently part of SpinLab:

.. list-table::
   :widths: 25 55 20
   :header-rows: 1

   * - Module
     - Description
     - API Reference
   * - ``spinlab.analysis``
     - Peak finding and relaxation fitting functions
     - :ref:`api-analysis`
   * - ``spinlab.config``
     - Configuration file handling and plot settings
     - —
   * - ``spinlab.constants``
     - Physical constants used throughout SpinLab
     - :ref:`api-constants`
   * - ``spinlab.core``
     - The ``SpinData`` object and core data structures
     - :ref:`api-core`
   * - ``spinlab.fitting``
     - General-purpose curve fitting and lineshape fitting
     - :ref:`api-fitting`
   * - ``spinlab.io``
     - Data import and export for all supported spectrometer formats
     - :ref:`api-io`
   * - ``spinlab.math``
     - Mathematical functions — lineshapes, window functions
     - :ref:`api-math`
   * - ``spinlab.plotting``
     - Plotting functions including ``plot()`` and ``fancy_plot()``
     - :ref:`api-plotting`
   * - ``spinlab.processing``
     - Signal processing — FFT, phase, baseline, normalization, and more
     - :ref:`api-processing`
