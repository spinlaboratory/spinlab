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

   
Welcome to the SpinLab documentation. SpinLab is an object-oriented |OpenSource| Python-based package for importing, processing, and analyzing data determined in an Electron Paramagnetic Resonance (EPR), Nuclear Magnetic Resonance (NMR), or Dynamic Nuclear Polarization (DNP) experiment. The aim of the project is to provide a free, turn-key Python-based processing package for Magnetic Resonance (MR) data.


Features
========

* Import many different NMR and EPR data formats (TopSpin, VnmrJ, Prospa, Xepr, ESR5000, SpecMan, ...)
* Create N-dimensional data objects with named axes
* Process and analyze data with a comprehensive function library
* Automatically maintain an audit log of all processing steps
* Create publication-quality figures

Please report all issues on the |SpinlabGitIssueTrackerLink|.


Quick Install
=============

.. code-block:: bash

    $ pip install spinlab

See :doc:`installation` for full installation instructions, virtual environment setup, and version management.


Citing SpinLab
==============

If you are using SpinLab to process your MR data, please add a link to the |SpinlabDocu| to your Materials and Methods section.

.. Table of Contents Structure

.. toctree::
   :caption: Overview
   :maxdepth: 1
   :hidden:

   introduction
   installation
   changelog

.. toctree::
   :caption: User Guide
   :maxdepth: 1
   :hidden:

   userGuide/gettingStarted
   userGuide/spindata_object
   userGuide/loading_data
   userGuide/processing
   userGuide/attributes
   userGuide/indexing
   userGuide/plotting
   

.. toctree::
   :caption: Tutorials and Examples
   :maxdepth: 1
   :hidden:

   sl_examples/index

.. toctree::
   :caption: Sample Data
   :maxdepth: 1
   :hidden:

   sampleData

.. toctree::
   :caption: Reference
   :hidden:

   modules
   api/index

.. toctree::
   :caption: About
   :hidden:

   people
   contributing
   license
   

