============
Why SpinLab?
============

The aim of SpinLab is to provide an |OpenSource|, object-oriented, turn-key data processing environment for magnetic resonance (NMR, EPR, DNP) data. The software package is entirely written in Python and no proprietary software is required.

Instrumentation for MR spectroscopy can vary largely. Many labs use commercially available instruments, but it is quite commonn that experiments are performed on home-built systems. Each system is running on their own software, resulting in spectra in different formats (e.g. TopSpin, VnmrJ, Delta, Prospa, ...), each presenting their own cahllenge to be imported. Additional information is often stored in log files (e.g. temperature, or microwave power), data that needs to be imported when analyzing the experimental data.

Many labs have created their own routines to import, process, and analyze MR data, using an organically grown collection of home-written scripts, maintained by past and present lab members and relying on that one "software-wizard" in the group that can help whenever help is needed. Naturally, this approach has several drawbacks:

1. No centrally maintained repository of scripts. Everyone uses and modifies their own copy of scripts to perform the task at hand.
2. Typically, no version control is used, but even if version control such as |Git| is used, often standard practices in software development (e.g. branching, pull requests ...) are poorly implemented.
3. Data and the processes for analysis are not easily shared between labs because of incompatible software formats.
4. The lack of standardized data processing can lead to unreproducible data.
5. Some techniques (e.g. CPMG data acquisition) require special processing workflows that are beyond the capabilities of the spectrometer acquisition software.

Often, this results in a time-consuming workflow. In the worst case, the lack of processing software may discourage researchers to enter this new field.

SpinLab was written with these key points in mind. The main features are:

* Import MR data in various formats (Bruker, Varian, JEOL,  Magritek, Tecmag, Text Files, ...) 
* Process and analyze data, including experiment dependent workflows
* Create publication-quality figures

The SpinLab Workflow
====================

SpinLab is object-oriented and processing is script based. A typicall workflow is as follows:

1. Import EPR, NMR, DNP, ... data. SpinLab will create a SpinLab data object, facilitating all further processing
2. Process raw data
3. Optional, save Data in h5 format for further processing
4. Additional data pProcessing and analysis
5. Create Report

SpinLab can be easily installed via pip:

.. code-block:: bash

    $ pip install spinlab
