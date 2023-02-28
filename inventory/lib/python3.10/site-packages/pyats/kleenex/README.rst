Kleenex - Dynamic testbed launch/teardown and physical clean services
=====================================================================

.. note::

        For better viewing/reading of this document, use restview_.

        .. _restview: https://pypi.python.org/pypi/restview

        For example::

            restview -l 0:8080 README.rst

        And then browse to http://your_machine:8080


Please refer to the bringup `online documentation`_.

.. _online documentation: http://wwwin-pyats.cisco.com/documentation/html/kleenex/index.html

Working Examples
----------------

This module does not have any working bringup examples, but instead serves as a
base for other dynamic topology orchestration classes.

Please see the cisco_shared `dyntopo documentation`_ for working examples.

.. _dyntopo documentation: http://wwwin-pyats.cisco.com/cisco-shared/html/dyntopo/docs/index.html


How to run unit tests:
----------------------
::

    cd $VIRTUAL_ENV/lib/py*/site-packages/ats/kleenex/tests
    python -m unittest

Developer's Guide
-----------------
This guide contains details on how to extend kleenex with new orchestrators.

.. _pyATS argument propagation policy: http://wwwin-pyats.cisco.com/documentation/html/easypy/usages.html#argument-propagation

Adding a new Bringup Orchestrator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
There are a few things to keep in mind when you want to add a new orchestrator:

- You must inherit from ``pyats.kleenex.BringUpWorkerBase`` and call
  the parent ``__init__`` in the first line of your ``__init__``.

- You should inherit from ``pyats.kleenex.ArgvQuotingParser`` as it provides
  extra debugging in the event an exception is thrown in CLI argument
  processing.

- You should use ``pyats.kleenex.parse_cli_args`` as all required common
  logic is provided for you, this adheres to the
  `pyATS argument propagation policy`_.

- You should use exceptions such as ``pyats.kleenex.TopologyDidntComeUpInTime``
  as they provide a consistent way of reporting issues common to multiple
  orchestrators.

- Expect ``pyats.kleenex.SignalError`` to be raised at any time as part of
  pyATS core bringup's signal handling model.

- You must implement ``_launch_topology`` and ``_tear_down_topology``.

- You must define a CLI parser that contains the same parameter names as
  those in your ``__init__`` prototype (as per
  `pyATS argument propagation policy`_.
  Any parameter specified via CLI will override parameters given in the
  constructor.  Any internal paramaeters that don't directly face the user
  may be excused from this policy as long as they are documented.

- You must implement a version of ``main.py`` that auto-assigns the
  ``-orchestrator``
  input to the pyATS core bringup tool to your worker class, think up a
  name for your decoupled bringup tool and update setup.py entry_points.
  Have your tool's ``main`` call ``pyats.kleenex.main()``.
  If the tool name ends with the characters ``bringup`` then the
  ``-orchestrator`` parameter does not appear in the tool's ``-help`` display.

- You must check ``self.help`` and follow the appropriate logic path when
  bringup is being run via a decoupled tool in ``-help`` mode.  Typically
  this means skipping bringup altogether.

- You must implement ``update_help`` so that your decoupled bringup tool will
  have a correct help display.

- You must identify those CLI parameters that have an equivalent in the
  clean schema, and must tag them with ``help_suppress_kleenex`` when
  adding arguments to your orchestrator's CLI command parser.

- You must implement ``_set_log_level`` and set the log level of all your
  modules.

- You must provide the actual-to-logical device name translation
  by populating ``self.dev_name_xref``.

- You must call ``self._process_tb_config`` when the actual topology
  configuration is ready to be handed off to pyATS core bringup for
  post-processing and ultimate exposure to the user.

- If you introduce new orchestrator-specific keys into the logical topology
  schema, be sure to document them and append them to the worker's
  ``self._logical_device_keys_to_ignore`` and
  ``self._logical_interface_keys_to_ignore`` members to ensure they are
  not merged into the final testbed content.
