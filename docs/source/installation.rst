Installation
======================
To install the *AI-WQ-package* on Linux, run the following command:

.. code-block:: bash

   python3 -m pip install AI-WQ-package 

From August 10th 2026, the AI Weather Quest will be using ECBox functionality. To ensure capability with `ECBox <https://sites.ecmwf.int/docs/public/services/ecbox/overview/>`_, please also install the *sites-toolkit* from the ECMWF repository:

.. code-block:: bash

   python3 -m pip install sites-toolkit -i https://get.ecmwf.int/repository/pypi-all/simple

For guidance on installing `Python 3 <https://wiki.python.org/moin/BeginnersGuide/Download>`__ or `pip <https://pip.pypa.io/en/stable/installation/>`__, refer to the official documentation.

.. toctree::
   :maxdepth: 2

   dependencies
   upgrading

Dependencies
------------
The AI-WQ-package requires the following dependencies:

- **numpy** (version 1.23 or higher)
- **xarray** (version 2024.09.0 or higher)
- **dask** (version 2024.9.0)
- **pandas** (version 2.2.3 or higher)
- **scipy** (version 1.14.1 or higher)
- **netCDF4** (version 1.7.2 or higher)
- **requests** (versions 2.32.2 or higher)
- **matplotlib** (versions 3.8 or higher)
- **cartopy** (versions 0.22 or higher)

If these dependencies conflict with your current working environment, consider installing the package in a new virtual environment.

Upgrading the Package
----------------------
To upgrade to the latest version, run:

.. code-block:: bash

   python3 -m pip install --upgrade AI-WQ-package 

As mentioned above, from August 10th 2026 the AI Weather Quest will leverage ECBox functionality. Please make sure you've also installed the *sites-toolkit*:

.. code-block:: bash

   python3 -m pip install sites-toolkit -i https://get.ecmwf.int/repository/pypi-all/simple

.. note::

   This project is actively developed. Updates and announcements are shared on the
   `ECMWF-hosted forum <https://forum.ecmwf.int/c/workshop-and-events/ai-weather-quest/41>`__.

