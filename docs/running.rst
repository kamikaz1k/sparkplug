Running Sparkplug
-----------------

Sparkplug comes with a launcher script named ``sparkplug`` which manages the message consumer process. When started, ``sparkplug`` examines the config files named on the command line for configuration elements, then starts up the ``main`` connection. The configuration files are also used to configure the `logging <http://docs.python.org/library/logging.html>`_ module.

Options
*******

By default, Sparkplug looks for a configuration section named ``connection:main``. However, both the name and the type of the block can be adjusted.

--connection  the name of the connection block to use ("main")
--connector   the type of the connection block to use ("connection")

Sparkplug also supports running several instances of the same configuration, trading AMQP's delivery guarantees for higher throughput via concurrency.

--fork=N      the number of copies of the configuration to run. If this option is specified, the entire sparkplug environment is run N times. (default: no forking)

Important note for Sparkplug 1.x users
**************************************

The ``sparkplug`` command no longer accepts daemon-related options and no
longer self-daemonizes. Self-daemonizing processes are surprisingly tricky to
get right, and the trend towards daemon-managing supervisors makes it mostly
irrelevant anyways. Consider using upstart, systemd, launchd, or similar if
your OS supports it; for userland equivalents, consider supervisord or
Foreman.

If you absolutely must have sparkplug daemonize itself, use your distro's
daemon wrappers (``start-stop-daemon`` and friends).

Example
*******

.. highlight:: bash

To run the included example::

    sparkplug example.ini
