==================
Welcome to SpinLab
==================

.. image:: https://img.shields.io/pypi/v/spinlab
   :target: https://pypi.org/project/spinlab/
   :alt: SpinLab

.. image:: https://img.shields.io/pypi/pyversions/spinlab
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://pepy.tech/badge/spinlab/month
   :target: https://pepy.tech/project/spinlab
   :alt: Downloads

   
Welcome to the SpinLab documentation. SpinLab is an object-oriented |OpenSource| Python-based package for importing, processing, and analyzing data determined in an Electron Paramagnetic Resonance (EPR), Nuclear Magnetic Resonance (NMR), or Dynamic Nuclear Polarization (DNP) experiment. The aim of the project is to provide a free, turn-key python-based processing package for Magnetic Resonance (MR) data.


.. note::
   DNPLab was recently renamed to SpinLab and with that we are also updating the documentation. Please make sure to check back as this document is growing.


To install SpinLab:

.. code-block:: bash

    $ pip install spinlab


Features
========

* Import many different NMR and EPR data formats (Topspin, VnmrJ, Prospa, Xepr, ESR5000...)
* Create N-dimensional data objects
* Easy data processing (e.g. apodization, zero-filling, Fourier transformations, alignment, ...)

Please report all issues on the |SpinlabGitIssueTrackerLink|.


Citing SpinLab
==============

If you are using SpinLab to process your MR data please add a link to the |SpinlabDocu| to your Materials and Methods section.


Installation
============

SpinLab can be easily installed via pip:

.. code-block:: bash

    $ pip install spinlab

.. Table of Contents Structure

.. toctree::
   :caption: Overview
   :maxdepth: 1
   :hidden:

   introduction
   installation
   currentRelease

.. toctree::
   :caption: User Guide
   :maxdepth: 1
   :hidden:

   userGuide/gettingStarted
   userGuide/indexing
   userGuide/plotting
   

.. toctree::
   :caption: Tutorials and Examples
   :maxdepth: 1
   :hidden:

   sl_examples/index
   sampleData

.. toctree::
   :caption: Reference
   :hidden:

   modules
   functions

.. toctree::
   :caption: About
   :hidden:

   people
   license
   

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
