============
Contributing
============

We welcome contributions of all kinds — bug reports, feature requests, documentation improvements, new test cases, and code fixes. Every contribution helps make SpinLab better for the entire magnetic resonance community.


Ways to Contribute
==================

* **Report a bug** — open an issue on the |SpinlabGitIssueTrackerLink|
* **Request a feature** — open a feature request on the |SpinlabGitIssueTrackerLink|
* **Improve the documentation** — fix a typo, expand an example, or add a new guide page
* **Add a test case** — help improve test coverage
* **Submit a code fix** — fix a bug or implement a new feature
* **Become a maintainer** — see the section below


Reporting Bugs and Requesting Features
=======================================

SpinLab uses the GitHub issue tracker for all bugs and enhancement requests.

When reporting a **bug**, please include:

1. A short, self-contained Python snippet that reproduces the problem
2. The SpinLab version (``pip show spinlab``)
3. Your Python version and operating system
4. What you expected to happen and what actually happened

When requesting a **feature**, please describe:

1. What you are trying to accomplish
2. Why the current functionality does not cover the use case
3. If possible, a sketch of the desired API


Working with the Code
=====================

Setting Up a Development Environment
--------------------------------------

1. Fork the repository on GitHub and clone your fork locally:

   .. code-block:: bash

       git clone https://github.com/<your-github-username>/spinlab spinlab-dev
       cd spinlab-dev
       git remote add upstream https://github.com/SpinLab/spinlab.git

2. Create a virtual environment with Python 3.10 or higher and install SpinLab in editable mode:

   .. code-block:: bash

       python -m venv venv
       source venv/bin/activate        # macOS / Linux
       venv\Scripts\activate           # Windows

       pip install -e spinlab

3. Switch to the ``Development`` branch, which contains the latest in-progress work:

   .. code-block:: bash

       git checkout Development
       git pull upstream Development


Branching and Committing
-------------------------

Always branch from ``Development``:

.. code-block:: bash

    git checkout Development
    git pull upstream Development
    git checkout -b yourname-gh-<issue-number>

Make small, focused commits. After making changes, verify nothing is broken:

.. code-block:: bash

    python -m pytest

Check for syntax errors and formatting:

.. code-block:: bash

    python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    python -m black .


Opening a Pull Request
-----------------------

Push your branch to your fork and open a pull request against ``SpinLab/Development``:

.. code-block:: bash

    git push -u origin yourname-gh-<issue-number>

In your pull request description, briefly explain what the change does and reference the related issue (e.g. ``Closes #42``). Automated checks will run; a maintainer will review and merge once everything passes.


Contributing to the Documentation
==================================

The documentation is written in reStructuredText and built with `Sphinx <https://www.sphinx-doc.org/>`_. Source files live in the ``doc/`` directory.

To build the docs locally:

.. code-block:: bash

    cd doc
    make html             # macOS / Linux
    .\make.bat html       # Windows

The built HTML is written to ``doc/_build/html/``. Open ``index.html`` in a browser to preview.

Documentation contributions are especially welcome — if something is unclear, a pull request fixing it is the fastest way to help the whole community.


Becoming a Maintainer
======================

We warmly welcome committed individuals to help maintain SpinLab. You do not need to be a Python expert or a magnetic resonance expert — enthusiasm and reliability matter more. Please reach out to any of the :doc:`current team members <people>` if you are interested.


License
=======

By contributing, you agree that your contributions will be licensed under the `MIT License <https://opensource.org/licenses/MIT>`_ that covers this project.
