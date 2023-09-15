"""Runs MahaUtils CLI and GUI tools

This module allows MahaUtils tools to be run from the command line using:

.. code-block:: shell

    python3 -m mahautils [COMMAND]

Where ``[COMMAND]`` is one of the following:

- ``simviewer``: Simulation results viewer
"""

import sys

from .multics.sim_results_viewer.app import main as run_sim_results_viewer
from .multics.sim_results_exporter.app import main as run_sim_results_exporter


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('MahaUtils: error: No command provided')
        sys.exit(1)

    command = sys.argv[1]
    if command.lower() == 'simviewer':
        run_sim_results_viewer(sys.argv[2:])
    elif command.lower() == 'simexporter':
        run_sim_results_exporter(sys.argv[2:])
    else:
        print(f'MahaUtils: error: Invalid command "{command}"')
