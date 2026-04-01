========
Indexing
========

Here we will give a short overview how to index a SpinLab data object.

Generate an Example Data Set
============================
First, start by generating an example data set. To do this, we Use the Lorentzian function to generate a 2D data set of Lorentzian distributions and create a sldata object.


First create a data set of 2D Lorentzian line shapes, using the built-in function ``math.lineshape.lorentzian`` as follows:

.. code-block:: python

    >>> import numpy as np
    >>> import spinlab as sl
    
    >>> x = np.linspace(-10,10,1024)
    >>> y = np.linspace(-3,3,6)

    >>> values = sl.math.lineshape.lorentzian(x.reshape(-1, 1), y.reshape(1, -1), 0.5)


Next, can create the SpinLab data object

.. code-block:: python

    >>> data = data = sl.SpinData(values, ["x (a.u.)", "x0"], [x, y])

This ``SpinData`` object can be easily ploted using the built-in plotting function

.. code-block:: python

    >>> sl.plt.figure()
    >>> sl.plot(data)
    >>> sl.plt.grid(ls = ":")
    >>> sl.plt.ylabel("Amplitude (a.u.)")
    >>> sl.plt.tight_layout()
    >>> sl.plt.show()






print(data)









..  data = dnp.DNPData(values, ["f2", "sample"], [x, y])




.. from matplotlib.pylab import *








You can index a DNPData object by specifying the name of the dimension and the index of the slice.

.. # %%
.. # Import DNPLab and create a set of data
.. # --------------------------------------
.. # Use the lorentzian function to generate a 2d set of lorentzian distributions.

.. import numpy as np
.. from matplotlib.pylab import *

.. import dnplab as dnp

.. x = np.r_[-50:50:1024j]
.. y = np.r_[-10:10:1]

.. values = dnp.math.lineshape.lorentzian(x.reshape(-1, 1), y.reshape(1, -1), 0.5)

.. data = dnp.DNPData(values, ["f2", "sample"], [x, y])

.. # %%
.. # To specify a slice based on the index, we use an integer. This will select the slice at index 3.

.. data_slice_integer = data["sample", 3]  # get slice by index

.. # Taking the slice does not remove the sample dimension. We can remove dimensions of length 1 with the squeeze method
.. data_slice_integer.squeeze()  # remove "sample" dimension

.. # %%
.. # In many cases, we want the slice at a specific value of the coordinates. To do this, we use a float to specify the slice location. In python, by adding a period after the number, python interprets the number as a float instead of integer.

.. data_slice_float = data[
..     "sample", 3.0
.. ]  # get slice at index closest to coordinates value of 3.
.. data_slice_float.squeeze()  # again, we remove the "sample" dimension.

.. # %%
.. # Plot the result
.. # ---------------
.. # Let's plot the 1d slices:

.. figure()
.. dnp.plot(data_slice_integer)
.. dnp.plot(data_slice_float)
.. xlabel("Frequency (Hz)")
.. ylabel("Signal (a.u.)")
.. tight_layout()

.. # %%
.. # Similarly, we can also slice by specifying a range of values. To do this, we use a tuple specify the minimum and maximum values for the index.

.. data_slice_range = data["sample", (-3, 3)]

.. # %%
.. # For an advanced tutorial how indexing works and how to extract individual data slice from a multi-dimensional dnpData object see the :ref:`plot_02_extract_data` tutorial.



.. .. SpinLab can be easily installed via pip:

.. .. .. code-block:: bash

.. ..     $ pip install spinlab

.. .. Required Packages
.. .. =================
.. .. SpinLab uses a few well-know Python pacakges, which will ba automatically installed during the installation. Currently, the following packages and their respective minimal versions are required:

.. .. .. list-table::
.. ..    :widths: 40 60

.. ..    * - **Package**
.. ..      - **Version**
.. ..    * - NumPy
.. ..      - 2.0.0 or higher
.. ..    * - SciPy
.. ..      - 1.14.0 or higher
.. ..    * - Matplotlib
.. ..      - 3.9.1 or higher
.. ..    * - h5py
.. ..      - 3.11.0 or higher


.. .. Ways to Install SpinLab
.. .. =======================

.. .. Installing Using Pip
.. .. --------------------
.. .. The easiest and most convenient way to install SpinLab is by using |pip|. In a terminal simply type the following command:

.. .. .. code-block:: bash

.. ..    $ python -m pip install spinlab

.. .. or just:

.. .. .. code-block:: bash

.. ..    $ pip install spinlab

.. .. If you prefer to install SpinLab from the source code, check out our GitHub repository |SpinlabGitLink|. The newest developments are always merged into the *Development* branch.


.. .. Confirm Successful Installation
.. .. -------------------------------

.. .. To confirm a successful SpinLab installation execute the following command in a terminal window:

.. .. .. code-block:: bash

.. ..     $ pip show spinlab

.. .. The output will look similar to this (note, the actual version and path to location depends on your local installation):

.. .. .. code-block:: bash

.. ..     Name: spinlab
.. ..     Version: 1.0.0
.. ..     Summary: SpinLab - Bringing the Power of Python to MR Spectroscopy
.. ..     Home-page:
.. ..     Author:
.. ..     Author-email:
.. ..     License-Expression: MIT
.. ..     Location: Path/to/Package
.. ..     Editable project location: Path/to/editable/location
.. ..     Requires:
.. ..     Required-by:


.. .. Specify a SpinLab Version to Install
.. .. ------------------------------------

.. .. If you wish to install a specific SpinLab version exectute the following command in a terminal window:

.. .. .. code-block:: bash
    
.. ..     $ pip install spinlab==1.0.0


.. .. Install Preliminary Release
.. .. ---------------------------

.. .. If you wish to use a pre-release version of SpinLab (downloaded from the GitHub repository) we recommend first uninstalling the current SpinLab version. Clone (or download or fork ...) the desired branch from the GitHub repository. In a terminal window navigate into the directory that contains the spinlab folder (important, **DO NOT** navigate **into** the folder) and execute the following command:

.. .. .. code-block:: bash
    
.. ..     $ pip install -e spinlab

.. .. Once the installation is finished verify the path and version of the package by executing the following command in a terminal window:

.. .. .. code-block:: bash
    
.. ..     $ pip show spinlab

.. .. If the version does not match the version of the checked-out branch, you may have to first uninstall SpinLab (:code:`pip uninstall spinlab`), then re-install the version you would like to use (:code:`pip install spinlab`), and then run (:code:`pip install -e spinlab`) if you would like to make your own changes to the code.


.. .. Upgrading SpinLab
.. .. =================

.. .. To upgrade the currently installed version of SpinLab execute the following command in a terminal window:

.. .. .. code-block:: bash

.. ..     $ pip install --upgrade spinlab


.. .. Uninstalling SpinLab
.. .. ====================

.. .. Don't like SpinLab? Please let us know how to improve the package.

.. .. The safest method to uninstall SpinLab is to use pip by executing the following command in a terminal window:
    
.. .. .. code-block:: bash
    
.. ..     $ pip uninstall spinlab


.. .. Installing SpinLab Using a Virtual Enviroment (Ubuntu)
.. .. ------------------------------------------------------

.. .. Starting from Ubuntu 23.10 ``pip3`` will issue a warning when trying to install SpinLab from PyPi. It is recommended to not perform a global install but instead use a virtual enviroment (venv). If you do not have already created a virtual enviroment you can create a folder at a convenient location where the enviroment will be located (see example below).

.. .. In this example this will be in our home folder and the folder will be named SpinLab.
.. .. To create this enviroment use the command

.. .. .. code-block:: bash

.. ..    $ python3 -m venv ~/SpinLab

.. .. Note that you need to activate the enviroment to use it and install packages via pip3. You can activate the virtual environment by sourcing the activate script that should be located in ~/SpinLab/bin

.. .. .. code-block:: bash

.. ..   $ source ~/SpinLab/bin/activate

.. .. This needs to be done, everytime you start this particular enviroment. To simplify this process, you can create an alias "spinlab" and add it to your .bash_aliases file

.. .. .. code-block:: bash

.. ..   $ echo "spinlab = 'source ~/SpinLab/bin/activate'" >> ~/.bash_aliases

.. .. To deactivate the virtual enviroment enter the following command in a terminal.

.. .. .. code-block:: bash

.. ..   $ deactivate

