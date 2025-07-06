============
Installation
============

Required Packages
=================
All required Python packages will be automatically installed during the installation. Currently, the following packages and their respective minimal versions are required:

.. list-table::
   :widths: 40 60

   * - **Package**
     - **Version**
   * - NumPy
     - 2.0.0 or higher
   * - SciPy
     - 1.14.0 or higher
   * - Matplotlib
     - 3.9.1 or higher
   * - h5py
     - 3.11.0 or higher


Ways to Install SpinLab
=======================

Installing Using Pip
--------------------
The easiest and most convenient way to install SpinLab is by using |pip|. In a terminal simply type the following command:

.. code-block:: bash

   $ python -m pip install spinlab

or just:

.. code-block:: bash

   $ pip install spinlab

If you prefer to install SpinLab from the source code, check out our GitHub repository |SpinlabGitLink|. The newest developments are always merged into the *Development* branch.


Installing SpinLab Using a Virtual Enviroment
---------------------------------------------

Starting from Ubuntu 23.10 ``pip3`` will issue a warning when trying to install spinlab from PyPi. It is recommended to not perform a global install but instead use a virtual enviroment (venv). If you do not have already created a virtual enviroment you can create a folder at a convenient location where the enviroment will be located (see example below).

In this example this will be in our home folder and the folder will be named SpinLab.
To create this enviroment use the command

.. code-block:: bash

   $ python3 -m venv ~/SpinLab

Note that you need to activate the venv to use it and install packages via pip3. You can activate the virtula environment by sourcing the activate script that should be located in ~/SpinLab/bin

.. code-block:: bash

  $ source ~/SpinLab/bin/activate

This needs to be done, everytime you start this particular enviroment. To simplify this process, you can create an alias "spinlab" and add it to your .bash_aliases file

.. code-block:: bash

  $ echo "spinlab = 'source ~/SpinLab/bin/activate'" >> ~/.bash_aliases

To deactivate the virtual enviroment enter the following command in a terminal.

.. code-block:: bash

  $ deactivate


Confirm Successful Installation
-------------------------------

To confirm a successful installation execute the following command in a terminal:

.. code-block:: bash

    $ pip show spinlab

The output will look similar to this (note, the actual version and path to location depends on the local installation):

.. code-block:: bash

    Name: spinlab
    Version: 1.0.0
    Summary: SpinLab - Bringing the Power of Python to MR Spectroscopy
    Home-page:
    Author:
    Author-email:
    License-Expression: MIT
    Location: Path/to/Package
    Editable project location: Path/to/editable/location
    Requires:
    Required-by:


Specify SpinLab Version to Install
----------------------------------

If you wish to install a specific version of SpinLab exectute the following command in a terminal window:

.. code-block:: bash
    
    $ pip install spinlab==1.0.0


Install Preliminary Release
---------------------------

If you wish to use a pre-release version of SpinLab (downloaded from the GitHub repository) we recommend first uninstalling the current SpinLab version. Clone (or download or fork ...) the desired branch from the GitHub repository. In a terminal window navigate into the directory that contains the spinlab folder (important, do not navigate into the folder). Execute the following in a terminal window:

.. code-block:: bash
    
    $ pip install -e spinlab

Once you ran this command check the path and version of the package by executing the following command in a terminal window:

.. code-block:: bash
    
    $ pip show spinlab

.. If the version does not match the version of the checked-out branch, you may have to first uninstall SpinLab (:code:`pip uninstall spinlab`), then re-install the version you would like to use (:code:`pip install spinlab`) and then running (:code:`pip install -e spinlab`) if you would like to make your own changes to the code.


Upgrading SpinLab
=================

To upgrade the currently installed version of SpinLab execute the following command in a terminal:

.. code-block:: bash

    $ pip install --upgrade spinlab


Uninstalling SpinLab
====================

Don't like SpinLab? Please let us know how to improve the package. The safest method to uninstall SpinLab is to use pip by executing the following command in a terminal window:
    
.. code-block:: bash
    
    $ pip uninstall spinlab
