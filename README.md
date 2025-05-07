# AI_weather_quest
To participate in the AI Weather Quest, you will need to install the AI-WQ-package Python package. This package requires Python version 3, and its source code is available on GitHub.

*AI-WQ-package* is a Python library designed to streamline participation in the AI Weather Quest. This guide provides step-by-step instructions on how to:

- Submit a forecast to the AI Weather Quest competition.
- Evaluate sub-seasonal forecasts using tools developed by the AI Weather Quest.
- Download training data for initially developing sub-seasonal forecast models. 

The package leverages capability developed through xarray for efficient data handling.

We highly recommend use the ReadTheDocs documentation as a guide for using this package: *https://ecmwf-ai-weather-quest.readthedocs.io/en/latest/*

Installation
--------------
To install the *AI-WQ-package* on Linux, run the following command:

**python3 -m pip install AI-WQ-package**

For guidance on installing Python 3 or pip, refer to the official documentation.

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

**python3 -m pip install --upgrade AI-WQ-package**

This project is being actively developed. New updates may be released periodically with detailed annoucements given on the ECMWF-hosted forum.


