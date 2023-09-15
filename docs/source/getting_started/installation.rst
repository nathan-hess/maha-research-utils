.. include:: ../constants.rst


.. _section-installation:

Installation
============

Prerequisites
-------------

If running |PackageNameStylized| on a Linux system, ensure that :spelling:word:`libGL`
is installed.  For example, to install this package on Ubuntu, run:

.. code-block:: shell

    sudo apt install libgl1


pip
---

Stable Version
^^^^^^^^^^^^^^

|PackageNameStylized| has been packaged through PyPI, so the easiest way to
install the latest package release is through pip:

.. tab-set::

    .. tab-item:: Linux / MacOS
        :sync: linux_macos

        .. code-block:: shell

            pip install mahautils

    .. tab-item:: Windows
        :sync: windows

        .. code-block:: powershell

            pip install mahautils

As with any Python project, it may be useful to consider setting up a
`virtual environment <https://docs.python.org/3/library/venv.html>`__
and installing packages in it.


Development Version
^^^^^^^^^^^^^^^^^^^

To use the latest |PackageNameStylized| features prior to their release on PyPI,
you can install the package directly from the project's GitHub page using:

.. tab-set::

    .. tab-item:: Linux / MacOS
        :sync: linux_macos

        .. code-block:: shell

            pip install git+https://github.com/nathan-hess/maha-research-utils.git@main

    .. tab-item:: Windows
        :sync: windows

        .. code-block:: powershell

            pip install git+https://github.com/nathan-hess/maha-research-utils.git@main


Source Code
-----------

Alternatively, if you prefer to work from the source code directly, you can download
the source code using Git, and then add the download directory to your ``PYTHONPATH``
environment variable so that the |PackageNameStylized| can be imported from scripts
or Python terminals.

.. note::

    Some functionality, such as command-line utilities, will not be available
    if setting up |PackageNameStylized| using this method.

First, clone the source repository to a location of your choice:

.. tab-set::

    .. tab-item:: Linux / MacOS
        :sync: linux_macos

        .. code-block:: shell

            git clone https://github.com/nathan-hess/maha-research-utils.git

    .. tab-item:: Windows
        :sync: windows

        .. code-block:: powershell

            git clone https://github.com/nathan-hess/maha-research-utils.git

Then, add the root directory of the repository to your ``PYTHONPATH`` environment
variable:

.. tab-set::

    .. tab-item:: Linux / MacOS
        :sync: linux_macos

        .. code-block:: shell

            export PYTHONPATH="$PYTHONPATH:$(pwd)/maha-research-utils"

    .. tab-item:: Windows
        :sync: windows

        .. code-block:: powershell

            set PYTHONPATH=%PYTHONPATH%;%CD%\maha-research-utils

Finally, make sure to install required dependencies through pip:

.. tab-set::

    .. tab-item:: Linux / MacOS
        :sync: linux_macos

        .. code-block:: shell

            pip install -r maha-research-utils/requirements.txt

    .. tab-item:: Windows
        :sync: windows

        .. code-block:: powershell

            pip install -r maha-research-utils\requirements.txt
