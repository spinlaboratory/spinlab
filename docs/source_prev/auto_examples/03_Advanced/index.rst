

.. _sphx_glr_auto_examples_03_Advanced:

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


.. toctree::
   :hidden:

   /auto_examples/03_Advanced/plot_01_align_nmr_spectra
   /auto_examples/03_Advanced/plot_02_extract_data
   /auto_examples/03_Advanced/plot_03_pseudo_modulation
   /auto_examples/03_Advanced/plot_04_phase_cycling
   /auto_examples/03_Advanced/plot_05_autophasing
   /auto_examples/03_Advanced/plot_06_fitting

