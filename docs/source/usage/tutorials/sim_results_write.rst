.. include:: ../../constants.rst

.. spelling:word-list::

    txt


Writing Simulation Results Files
================================

Prior to running a Maha Multics simulation, it is necessary to add a list of
all variables to be saved when running the simulation.  The
:py:class:`mahautils.multics.SimResults` class can make this process easier.


Setup
-----

For this example, suppose that we want to output the following variables
from our simulation:

- ``t`` with units of ``s``
- ``position_x`` with units of ``m``
- ``position_y`` with units of ``micron``
- ``position_z`` with units of ``micron``
- ``speed_x`` with units of ``m/s``
- ``speed_y`` with units of ``mm/s``
- ``speed_z`` with units of ``mm/s``

We'll consider that simulation time ``t`` and position are "required"
(simulation will exit with error if variable can't be outputted) and the
speed is "optional" (simulation will still run, even if variable can't be
outputted).


Creating the ``SimResults`` Instance
------------------------------------

First, make sure you've imported the |PackageNameStylized| package:

>>> import mahautils

Next, create a :py:class:`mahautils.multics.SimResults` instance:

>>> sim_results = mahautils.multics.SimResults()

You can optionally add a title to describe the simulation results file you're
creating:

>>> sim_results.title = 'Tutorial Simulation Results File'


Adding Simulation Results Variables
-----------------------------------

To add variables to the simulation results file, use the
:py:meth:`mahautils.multics.SimResults.append` method:

>>> sim_results.append('t', required=True, units='s')
>>> sim_results.append('position_x', required=True, units='m')
>>> sim_results.append('position_y', required=True, units='micron')
>>> sim_results.append('position_z', required=True, units='micron')
>>> sim_results.append('speed_x', required=False, units='m/s')
>>> sim_results.append('speed_y', required=False, units='mm/s')
>>> sim_results.append('speed_z', required=False, units='mm/s')

We can verify that all desired variables have been added by viewing the
:py:attr:`mahautils.multics.SimResults.variables` attribute:

>>> print(sim_results.variables)
('t', 'position_x', 'position_y', 'position_z', 'speed_x', 'speed_y', 'speed_z')

Alternatively, we can also view the list of variables with the
:py:meth:`mahautils.multics.SimResults.search` method:

>>> sim_results.search('')
No Group Assigned
  t          : [Required] [Units: s]
  position_x : [Required] [Units: m]
  position_y : [Required] [Units: micron]
  position_z : [Required] [Units: micron]
  speed_x    : [Optional] [Units: m/s]
  speed_y    : [Optional] [Units: mm/s]
  speed_z    : [Optional] [Units: mm/s]


Writing to a File
-----------------

Now that we've defined the desired variables, to write our simulation results
file to the disk, simply run:

>>> sim_results.write('simulation_results.txt')

A file named ``simulation_results.txt`` should have been created in your working
directory with the following content:

.. code-block:: ini
    :caption: simulation_results.txt
    :linenos:

    # Title: Tutorial Simulation Results File

    printDict{
        @t             [s]
        @position_x    [m]
        @position_y    [micron]
        @position_z    [micron]
        ?speed_x       [m/s]
        ?speed_y       [mm/s]
        ?speed_z       [mm/s]
    }


.. testcleanup::

    import os
    os.remove('simulation_results.txt')
