:orphan:

Overview
========
The easiest way to learn how to use SpinLab is by following our examples. Below is a collection of different examples describing how to import, process and analyze data in SpinLab.


.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. thumbnail-parent-div-close

.. raw:: html

    </div>

Importing Data And Basic Processing
===================================



.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example demonstrates how to load and process a single 1D NMR spectrum recorded on a Bruker spectrometer acquired using TopSpin. This examples also demonstrates how to access the various components of the data object and generally how to interact with the functions.">

.. only:: html

  .. image:: /auto_examples/01_ImportingData/images/thumb/sphx_glr_plot_01_load_1D_NMR_spectrum_Bruker_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_01_ImportingData_plot_01_load_1D_NMR_spectrum_Bruker.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Load 1D NMR spectrum in TopSpin format</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="In this example we demonstrate how to import two ODNP-enhanced NMR spectra, one recorded with a microwave power of 0 W (off-signal) and one with a microwave power of 2 W (on-signal). The spectra are recorded using a Magritek Kea system.">

.. only:: html

  .. image:: /auto_examples/01_ImportingData/images/thumb/sphx_glr_plot_02_load_1D_NMR_spectrum_Kea_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_01_ImportingData_plot_02_load_1D_NMR_spectrum_Kea.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Load two 1D NMR spectra in Kea format</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="In this example we demonstrate how to load and EPR spectrum and process the data.">

.. only:: html

  .. image:: /auto_examples/01_ImportingData/images/thumb/sphx_glr_plot_03_load_EPR_Spectrum_Bruker_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_01_ImportingData_plot_03_load_EPR_Spectrum_Bruker.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Load EPR spectrum in Bruker EMX format</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example demonstrates how to import a list of Spin-NMR spectra and create a 2D sldata object.">

.. only:: html

  .. image:: /auto_examples/01_ImportingData/images/thumb/sphx_glr_plot_04_create_dnpdata_object_from_individual_files_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_01_ImportingData_plot_04_create_dnpdata_object_from_individual_files.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Create a 2D sldata object from set of individual spectra</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example demonstrates how to select a slice of a SpinData object.">

.. only:: html

  .. image:: /auto_examples/01_ImportingData/images/thumb/sphx_glr_plot_05_indexing_dnpdata_objects_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_01_ImportingData_plot_05_indexing_dnpdata_objects.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">How to select a slice from a 2D sldata object</div>
    </div>


.. thumbnail-parent-div-close

.. raw:: html

    </div>

Data Analysis
=============



.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example demonstrates how to import Spin-NMR data in form of a 2D sldata object from an hdf5 file, calculate the Spin enhancement factors and plot the enhancement vs. the applied microwave power. This example uses the 2D data object that was created in a previous tutorial (plot_04_create_sldata_object_from_individual_files). The sample is 10 mM TEMPO in Toluene measured at 14.5MHz (X-Band ODNP spectroscopy).">

.. only:: html

  .. image:: /auto_examples/02_Analysis/images/thumb/sphx_glr_plot_01_load_2D_calculate_DNP_enhancements_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_02_Analysis_plot_01_load_2D_calculate_DNP_enhancements.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Load a 2D sldata object and calculate enhancements</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example demonstrates how to import TopSpin data from an inversion recovery NMR experiment and determine the T1 relaxation rate through a fit.">

.. only:: html

  .. image:: /auto_examples/02_Analysis/images/thumb/sphx_glr_plot_02_analyze_inversion_recovery_experiments_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_02_Analysis_plot_02_analyze_inversion_recovery_experiments.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Analyze T1 Inversion-Recovery Experiments</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example demonstrates how to determine the linewidth of peaks in an NMR spectrum.">

.. only:: html

  .. image:: /auto_examples/02_Analysis/images/thumb/sphx_glr_plot_03_peak_linewidth_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_02_Analysis_plot_03_peak_linewidth.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Peak Linewidth</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example demonstrates how to reference spectra using Toluene as an example.">

.. only:: html

  .. image:: /auto_examples/02_Analysis/images/thumb/sphx_glr_plot_04_reference_spectra_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_02_Analysis_plot_04_reference_spectra.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Reference  Spectra</div>
    </div>


.. thumbnail-parent-div-close

.. raw:: html

    </div>

Advanced Processing and Analysis
================================



.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="In example plot_01_load_2D_calculate_Spin_enhancements we calculated the ODNP enhancement for all protons in toluene, across the entire spectrum. However, the resolution of the spectrum is high enough to resolve the individual NMR peaks of the methyl group and the aromatic protons. This will allow us to calculate the enhancements for the individual peaks. However, as common in low-field NMR spectroscopy, we first have to correct spectra because of the field drift. While magnetic field drift is not an issue in high-field NMR systems using a superconducting magnet, this is not the case in low field systems that either use a electromagnet or a permanent magnet. Peaks will drift and simply averaging over a longer period of time will result in broadened peaks and therefore decreased resolution.">

.. only:: html

  .. image:: /auto_examples/03_Advanced/images/thumb/sphx_glr_plot_01_align_nmr_spectra_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_03_Advanced_plot_01_align_nmr_spectra.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Align NMR Spectra</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example demonstrates how to extract data from a multidimensional sldata object. For example, extracting a single spectrum (or a set of spectra) for a 2D set of spectra.">

.. only:: html

  .. image:: /auto_examples/03_Advanced/images/thumb/sphx_glr_plot_02_extract_data_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_03_Advanced_plot_02_extract_data.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Extract Individual Spectra</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="Typically, cw EPR spectra are recorded and shown as its first derivative, because the spectrum is detected using a lock-in amplifier. In contrast, a echo-detected field sweep spectrum is recorded as the absorption spectrum. To simulated the effect of the lock-in detection on an absorption spectrum to compare spectra, the data can be pseudo-modulated to calculate the derivative of the spectrum and to filter out noise. The same attention needs to be paid to the modulation amplitude as in an actual cw experiment. The spectrum can easily be overmodulated if the value of the modulation amplitude is too high.">

.. only:: html

  .. image:: /auto_examples/03_Advanced/images/thumb/sphx_glr_plot_03_pseudo_modulation_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_03_Advanced_plot_03_pseudo_modulation.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Pseudo Modulation of EPR Spectra</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example demonstrates how to use the phase cycling function on sldata objects.">

.. only:: html

  .. image:: /auto_examples/03_Advanced/images/thumb/sphx_glr_plot_04_phase_cycling_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_03_Advanced_plot_04_phase_cycling.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Using the spinlab phase cycling function</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example demonstrates how to use the SpinLab autophase function on a sldata object.">

.. only:: html

  .. image:: /auto_examples/03_Advanced/images/thumb/sphx_glr_plot_05_autophasing_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_03_Advanced_plot_05_autophasing.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Using the SpinLab autophase function</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example demonstrates how to use the SpinLab fit function on a sldata object.">

.. only:: html

  .. image:: /auto_examples/03_Advanced/images/thumb/sphx_glr_plot_06_fitting_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_03_Advanced_plot_06_fitting.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Using the SpinLab Fit function</div>
    </div>


.. thumbnail-parent-div-close

.. raw:: html

    </div>

SpinLab Tools
============

SpinLab contains several tools to make day-to-day operation when running Spin experiments in the lab easier. These are little helper scripts and function to calculate the electron and nuclear Larmor frequency at a given magnetic field, or calculate the approximate magnetic field positions for specific radicals. Below is a gallery with different types of examples.


.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example demonstrates how to use the tool to calculate the nuclear Larmor frequency.">

.. only:: html

  .. image:: /auto_examples/04_Tools/images/thumb/sphx_glr_plot_01_larmor_frequency_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_04_Tools_plot_01_larmor_frequency.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Calculate/Plot Nuclear Larmor Frequency</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example demonstrates how to use common numpy functions to manipulate sldata objects.">

.. only:: html

  .. image:: /auto_examples/04_Tools/images/thumb/sphx_glr_plot_02_using_numpy_functions_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_04_Tools_plot_02_using_numpy_functions.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Using common NumPy functions on sldata objects</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example demonstrates how to use SpinLab to download datasets from LOGS.">

.. only:: html

  .. image:: /auto_examples/04_Tools/images/thumb/sphx_glr_plot_03_download_datasets_from_logs_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_04_Tools_plot_03_download_datasets_from_logs.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Downloading datasets from LOGS</div>
    </div>


.. thumbnail-parent-div-close

.. raw:: html

    </div>


.. toctree::
   :hidden:
   :includehidden:


   /auto_examples/01_ImportingData/index.rst
   /auto_examples/02_Analysis/index.rst
   /auto_examples/03_Advanced/index.rst
   /auto_examples/04_Tools/index.rst


.. only:: html

  .. container:: sphx-glr-footer sphx-glr-footer-gallery

    .. container:: sphx-glr-download sphx-glr-download-python

      :download:`Download all examples in Python source code: auto_examples_python.zip </auto_examples/auto_examples_python.zip>`

    .. container:: sphx-glr-download sphx-glr-download-jupyter

      :download:`Download all examples in Jupyter notebooks: auto_examples_jupyter.zip </auto_examples/auto_examples_jupyter.zip>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_
