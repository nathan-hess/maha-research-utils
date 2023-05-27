# MahaUtils

[![CI/CD](https://github.com/nathan-hess/maha-research-utils/actions/workflows/cicd.yml/badge.svg)](https://github.com/nathan-hess/maha-research-utils/actions/workflows/cicd.yml)
[![codecov](https://codecov.io/gh/nathan-hess/maha-research-utils/branch/main/graph/badge.svg)](https://codecov.io/gh/nathan-hess/maha-research-utils)
[![Documentation Status](https://readthedocs.org/projects/mahautils/badge/?version=latest)](https://mahautils.readthedocs.io)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/mahautils?label=PyPI%20downloads&logo=python&logoColor=yellow)](https://pypi.org/project/mahautils)


## Overview

MahaUtils provides a collection of Python tools to support research work at the [Maha Fluid Power Research Center](https://engineering.purdue.edu/Maha/) at [Purdue University](https://www.purdue.edu/).  The classes, functions, and other objects in this package are intended to assist with general-purpose research tasks as well as simplify interaction with the [Maha Multics](https://avaccadev.github.io/Multics/) software.

> **Warning**
> The MahaUtils source code and documentation refers to the "Maha Multics" software in a number of places.  **The "Maha Multics" software is NOT related to the [Multics operating system](https://en.wikipedia.org/wiki/Multics).**  It is an unrelated fluid simulation software designed for analyzing hydraulic pumps and motors.

Most of the tools in this package were originally separate scripts, written by Nathan Hess during various research work.  They were combined into a single Python package as a way to reduce duplicate code, ensure these "utility scripts" were tested and robust, and make it easier to share the code.


## Installation

The recommended way to install MahaUtils is through [pip](https://pypi.org/project/mahautils/):

```
pip install mahautils
```

For more information about configuring Python and using packages, refer to the official Python documentation on [setting up Python](https://docs.python.org/3/using/index.html) and [installing packages](https://packaging.python.org/en/latest/tutorials/installing-packages/).


## Usage and Documentation

Detailed documentation for the MahaUtils project can be found here: https://mahautils.readthedocs.io.

The project documentation contains example code, file format specifications, and detailed API reference.  If you're still not certain how to do something after reading it, feel free to [create a discussion post](https://github.com/nathan-hess/maha-research-utils/discussions/categories/q-a)!


## Feature Highlights

### SimViewer GUI

The MahaUtils package includes an interactive tool for plotting and exploring Maha Multics simulation results.  SimViewer runs in a web browser, so it is compatible with nearly any operating system and platform.

Once you've installed the MahaUtils package, simply open a terminal and launch SimViewer by running:

```shell
$ SimViewer
```

> :test_tube: **Try It Out!**
>
> Want to give the GUI a try?  The quickest way is to launch a GitHub Codespaces instance:
>
> [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/nathan-hess/maha-research-utils)
>
> If you need some files to experiment with, give these a try: [`sim_results_underdamped.txt`](https://github.com/nathan-hess/maha-research-utils/blob/main/demo_files/sim_results_underdamped.txt) and [`sim_results_overdamped.txt`](https://github.com/nathan-hess/maha-research-utils/blob/main/demo_files/sim_results_overdamped.txt)

The primary aim of the SimViewer GUI is to provide a visually-appealing, configurable interface for quickly reviewing and comparing simulation results, with sufficient control over plot styling to generate and export presentation-quality plots.  Here's a demonstration of what it looks like in action:

![](https://raw.githubusercontent.com/nathan-hess/maha-research-utils/main/docs/source/usage/simviewer/images/simviewer_demo.gif)


### Reading and Editing Maha Multics Files

MahaUtils includes utilities to make it easier to interact with Maha Multics input and output files.  Rather than interacting with the raw content of the files, MahaUtils provides Python-based interfaces to edit file attributes.  This avoids the need to understand and ensure that your files are correctly formatted -- MahaUtils performs error checks and formats the file behind-the-scenes before writing it.

For instance, here's an example of how to extract data from and edit a Maha Multics simulation results file:

```python
from mahautils.multics import SimResults

# Read the file
sim_results = SimResults('simulation_results.txt')

# Print a list of variables in the file
print(sim_results.variables)

# Extract data from the file, with automatic unit conversions
position_meters = sim_results.get_data('xBlock', 'm')
position_inches = sim_results.get_data('xBlock', 'in')

# Edit data in the file
sim_results.set_description('xBlock', 'Position of the block')
sim_results.overwrite()
```

Similar tools are available for interacting with fluid property files, polygon files, and VTK files.


### Generating Polygon Geometry

Maha Multics uses "polygon files" to specify geometry and apply boundary conditions in simulations.  It can be tedious to create these files manually and ensure the correct format.

MahaUtils makes this process easier.  It provides methods to create common geometric shapes and add them to polygon files, and then plot the file to ensure the geometry matches your expectations.

```python
from mahautils.multics import PolygonFile
from mahautils.shapes import Circle, Layer

# Initialize the file
polygon_file = PolygonFile()

polygon_file.polygon_merge_method = 0
polygon_file.time_extrap_method = 0
polygon_file.time_units = 's'

# Add a translating circle
for i in range(25):
    polygon_file.polygon_data[i] = Layer(
        Circle(center=(i, 0), radius=4, units='mm',
               default_num_coordinates=1000),
        color='blue',
    )

# Preview the polygon file geometry
polygon_file.plot()

# Write to a file
polygon_file.write('my_polygon_file.txt')
```


## Acknowledgments

Project source code is hosted on [GitHub](https://github.com/nathan-hess/maha-research-utils), releases are distributed through [PyPI](https://pypi.org/project/mahautils), and documentation is hosted through [Read the Docs](https://docs.readthedocs.io/en/stable/index.html).  Some README badges were generated using [Shields.io](https://shields.io).
