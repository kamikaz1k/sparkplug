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

Daemon Mode
***********

For production use, ``sparkplug`` can also be started as a daemon using the ``-d`` (``--daemon``) option. There are a number of related options, which tune the daemon's behaviour:

--daemon            run as a daemon rather than as an immediate process
--pidfile=PIDFILE   the daemon PID file (default: sparkplug.pid)
--working-dir=DIR   the directory to run the daemon in (default: .)
--uid=UID           the userid to run the daemon as (default: inherited from parent process)
--gid=GID           the groupid to run the daemon as (default: inherited from parent process)
--umask=UMASK       the umask for files created by the daemon (default: 0022)
--stdout=STDOUT     sends standard output to the file STDOUT if set
--stderr=STDERR     sends standard error to the file STDERR if set

Example
*******

.. highlight:: bash

To run the included example as a daemon::

    sparkplug --daemon example.ini
