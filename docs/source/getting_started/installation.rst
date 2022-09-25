.. include:: ../constants.rst


.. _section-installation:

Installation
============

pip
---

Stable Version
^^^^^^^^^^^^^^

|PackageNameStylized| has been packaged through PyPI, so the easiest way to
install the latest package release is through pip:

.. code-block:: shell

    pip install mahautils


Development Version
^^^^^^^^^^^^^^^^^^^

To use the latest |PackageNameStylized| features prior to their release on PyPI,
you can install the package directly from the project's GitHub page using:

.. code-block:: shell

    pip install git+https://github.com/nathan-hess/maha-research-utils.git@main


Source Code
-----------

Alternatively, if you prefer to download the source code directly, you can do
so using Git.  Note that some functionality, such as command-line utilities,
will not be available if setting up |PackageNameStylized| using this method.

First, clone the source repository to a location of your choice:

.. code-block:: shell

    git clone https://github.com/nathan-hess/maha-research-utils.git

Then, add the root directory of the repository to your ``PYTHONPATH`` environment
variable:

.. tab-set::

    .. tab-item:: Linux / MacOS

        .. code-block:: shell

            export PYTHONPATH="$PYTHONPATH:$(pwd)/maha-research-utils"

    .. tab-item:: Windows

        .. code-block:: powershell

            set PYTHONPATH=%PYTHONPATH%;%CD%\maha-research-utils

Finally, make sure to install required dependencies through pip:

.. code-block:: shell

    pip install -r maha-research-utils/requirements.txt
