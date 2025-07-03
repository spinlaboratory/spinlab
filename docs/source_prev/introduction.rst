============
Introduction
============

The aim of SpinLab is to provide a turn-key data processing environment for |SpinNMR| data. The software package is entirely written in Python and no proprietary software is required.

The field of |SpinNMR| spectroscopy is relatively new and the instrumentation can vary largely. Some labs use commercially available Spin-NMR systems (mostly for solid-state Spin-NMR experiments) but it is quite common that Spin-NMR experiments are performed on home-built instruments. This often results in spectra recorded in different formats (e.g. TopSpin, VnmrJ, Delta, Prospa, ...) that need to be imported. Additional information is often stored in log files (e.g. temperature, or microwave power), data that needs to be imported when analyzing the experimental data.

Many labs therefore create their own routines to import, process, and analyze Spin-NMR data, using an organically grown collection of home-written scripts, maintained by past and present graduate students and post-docs and relying on that one "software-wizard" in the group that can hep whenever help is needed However, this approach has several drawbacks:

1. No centrally maintained repository of scripts. Everyone uses and modifies their own copy of scripts to perform the task at hand.
2. Often there is no version control and even if a version control software such as |Git| is used, often standard practices in software development (e.g. branching, pull requests ...) are ignored.
3. Data and the analysis is not easily shared between labs because of incompatible software formats.
4. The lack of standardized data processing can lead to unreproducible data.

Often, this results in a time-consuming workflow. In the worst case, the lack of processing software may discourage researchers to enter this new field.

Why SpinLab?
===========

SpinLab was written with these key points in mind. The main features are:

* Import NMR spectra in various formats (Bruker - TopSpin, Varian - (Open) VnmrJ, JEOL - Delta,  Magritek - Kea, Tecmag - TNMR) 
* Process NMR data
* Determine enhancement factors, fit power saturation measurements, analyze enhancement field profiles
* Extract hydration dynamics information
* Create publication-quality figures

The SpinLab Workflow
===================

In the following section, we introduce the intended workflow for processing Spin-NMR data with SpinLab. The general workflow is as follows:

1. Import Spin-NMR Data
2. Process Data
3. Save Data in h5 Format
4. Further Processing and Data Analysis
5. Create Report

.. Importing Data
.. --------------
.. The data is imported using the :ref:`slImport <slImport>`  sub-package. This sub-package calls modules for importing various spectrometer formats (e.g. topspin, vnmrj, prospa, etc.).

.. The data is imported as a :ref:`sldata <slData>` object. The sldata object is a container for data (values), coordinates for each dimension (coords), dimension labels (dims), and experimental parameters (attrs). In addition, each processing step applied to the data is saved in the sldata object (stored as proc_attrs).

.. The sldata object is a flexible data format which can handle N-dimensional data and coordinates together.

.. The imported data is stored in a sldata object and the first object that is created during the import process is the *raw* object. It contains the raw data from the spectrometer and will be accessible at any time. All processing steps are automatically documented and the entire workspace can be saved as a single file in the h5 format.


.. Processing Data
.. ---------------
.. The SpinLab workspace has the concept of a "processing_buffer" (typically called proc). The processing buffer specifies the data which is meant for processing. Typically one will add (raw) data to the workspace and copy or move the data to the processing buffer (proc). SpinLab is primarily designed for processing and analyzing Spin-NMR data. Processing Spin-NMR data is performed using the the :ref:`slNMR <slNMR>` module. 

.. Saving Data
.. -----------
.. Once the data is processed, the entire workspace can be saved in a single file in the h5 format. This is done using the :ref:`slSave <slSave>` module. The workspace can then be loaded, subsequent processing can be performed and the data can be saved again.


.. Workflow
.. ========

.. .. figure:: _static/images/Spinlab_workflow.png
..     :width: 400
..     :alt: Spinlab Workflow
..     :align: center

..     Overview of the Spinlab Workflow


.. Creating a workspace
.. --------------------
.. The workspace can be created with the "create_workspace" function in SpinLab. Once the data is imported, it is added to a workspace which is a python dictonary-like class that stores multiple sldata objects. A workspace is a collection of sldata objects and allows for raw and processed data to be saved in the same h5 file. That way, the raw data is always available, even if the data on the spectrometer does not exist anymore.

.. Creating a single h5 file has the advantage that data can be easily shared among collaborators.

