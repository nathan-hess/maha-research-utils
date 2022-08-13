.. include:: ../constants.rst


Installation
============

pip
---

|PackageNameStylized| has been packaged through PyPI, so the easiest way to
install the package is through pip:

.. code-block:: shell

    pip install mahautils


Source Code
-----------

Alternatively, if you prefer to download the source code directly, you can do
so using Git.  First, clone the source repository to a location of your choice:

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
