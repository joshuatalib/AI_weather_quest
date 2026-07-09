# AI Weather Quest (`AI-WQ-package`)

> **Disclaimer:** This package is provided for research and competition participation purposes only. It is **not** intended for use in any operational or production context. It is not an officially supported ECMWF product. Use it at your own risk.

## Overview

`AI-WQ-package` is a Python library that supports participation in the **ECMWF AI Weather Quest**, a competition to develop and evaluate AI-based sub-seasonal forecasts.

The package enables you to:

- **Submit forecasts** to the AI Weather Quest competition.
- **Evaluate sub-seasonal forecasts** using tools developed by the AI Weather Quest team.
- **Download training data** for developing sub-seasonal forecast models.

It builds on [xarray](https://xarray.dev/) for efficient NetCDF-based data handling.

---

## Installation

To install the *AI-WQ-package* on Linux, run the following command:

**python3 -m pip install AI-WQ-package**

For guidance on installing Python 3 or pip, refer to the official documentation.

---

## Dependencies

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

---

## Upgrading the Package

To upgrade to the latest version, run:

**python3 -m pip install --upgrade AI-WQ-package**

This project is being actively developed. New updates may be released periodically with detailed annoucements given on the ECMWF-hosted forum.

---

## Software Maturity

| Attribute        | Status |
|------------------|--------|
| **Maturity**     | [![Static Badge](https://github.com/ecmwf/codex/raw/refs/heads/main/Project%20Maturity/sandbox_badge.svg)](https://github.com/ecmwf/codex/raw/refs/heads/main/Project%20Maturity#sandbox) |
| **Support level**| Best effort — no guaranteed response time |
| **Operational use** | Not suitable for operational use |


> \[!IMPORTANT\]
> This software is **Sandbox**, is under active development, and subject to ECMWF's guidelines on [Software Maturity](https://github.com/ecmwf/codex/raw/refs/heads/main/Project%20Maturity). Releases are made periodically; announcements are posted on the [ECMWF Community Forum]([https://forum.ecmwf.int/](https://forum.ecmwf.int/c/workshop-and-events/ai-weather-quest/41)).

---

## Support

This package is **not officially supported** by ECMWF. Community contributions and questions are welcome via GitHub Issues on the upstream repository or on the [ECMWF Community Forum]([https://forum.ecmwf.int/](https://forum.ecmwf.int/c/workshop-and-events/ai-weather-quest/41)).

For general ECMWF-related enquiries, please use the [ECMWF Service Desk](https://support.ecmwf.int/).

---

## Documentation

Full documentation is available on ReadTheDocs:

**https://ecmwf-ai-weather-quest.readthedocs.io/en/latest/**
