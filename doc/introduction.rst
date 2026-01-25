============
Introduction
============

Why SpinLab?
============

The aim of SpinLab is to provide an |OpenSource|, object-oriented, turn-key data processing environment for magnetic resonance (NMR, EPR, DNP) data. The software package is entirely written in Python and no proprietary software is required.

Instrumentation for magnetic resonance (MR) spectroscopy can vary largely. Many labs use commercially available instruments, but home-built instruments are ubiquiteous. Each system is running on their own software, producing spectra in different formats (e.g. BES3T, TopSpin, VnmrJ, Delta, Prospa, ...), each presenting their own challenge to be imported. Additional meta data is often stored in auxillarary log files (e.g. temperature, or microwave power), data that needs to be imported when analyzing the experimental data.

Many labs rely on the own routines to import, process, and analyze MR data, often using an organically grown collection of home-written scripts, maintained by past and present lab members and relying on that one "software-wizard" in the group who can help whenever help is needed. Naturally, this approach has several drawbacks:

1. No centrally maintained repository of scripts. Everyone uses and modifies their own copy of scripts to perform the task at hand.
2. Oten, no version control is used, but even if version control such as |Git| is used, often standard practices in software development (e.g. branching, pull requests ...) are poorly implemented.
3. Data and processing scripts can not easily be shared between labs because of incompatible software formats.
4. The lack of standardized data processing can lead to unreproducible data.
5. Some techniques (e.g. CPMG data acquisition) require special processing workflows that are beyond the capabilities of the spectrometer acquisition software.

Often, this results in a time-consuming workflow. In the worst case, the lack of processing software may discourage researchers to enter this new field.

SpinLab was written with these key points in mind. The main features are:

* Easy import MR data present in various formats (Bruker, Varian, JEOL,  Magritek, Tecmag, Text Files, ...) 
* Process and analyze data, including experiment dependent workflows. An audit log is automatically created to document the individual processing steps
* Create publication-quality figures

The SpinLab Workflow
====================

SpinLab is object-oriented and data processing is script based. A typicall workflow is as follows:

1. Import EPR, NMR, DNP, ... data. SpinLab will automatically create a SpinLab data object, facilitating all further processing
2. Process raw data and automatically create an audit log
3. Optional, save Data in h5 format for further processing
4. Additional data Processing and analysis
5. Create Report


SpinLab can be easily installed via pip:

.. code-block:: bash

    $ pip install spinlab
