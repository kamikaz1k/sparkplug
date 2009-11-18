from __future__ import with_statement

import ConfigParser
import optparse
import logging
import logging.config
import os
import sys
import daemon
import daemon.pidlockfile
import functional
import sparkplug.options
import sparkplug.config
import sparkplug.logutils

_log = sparkplug.logutils.LazyLogger(__name__)

def sparkplug_options(args):
    options = optparse.OptionParser(
        usage="%prog [options] CONFIG [CONFIG2 CONFIG3 ...]",
        description="An AMQP message handler daemon.",
        option_class=sparkplug.options.Option
    )
    options.add_option("-c", "--connection",
                       action="store",
                       help="the name of the connection configuration to host (default: %default)",
                       default="main")
    options.add_option("-C", "--connector",
                       action="store",
                       help="overrides the connector implementation entry point (default: %default)",
                       default="connection")
    daemon_options = optparse.OptionGroup(
        options,
        "Daemon options",
        "The following options configure sparkplug to run as a daemon process."
    )
    daemon_options.add_option("-d", "--daemon",
                              action="store_true",
                              help="run as a daemon rather than as an immediate process",
                              default=False)
    daemon_options.add_option("-p", "--pidfile",
                              action="store",
                              help="the daemon PID file (default: %default)",
                              default="sparkplug.pid")
    daemon_options.add_option("-w", "--working-dir",
                              action="store",
                              metavar="DIR",
                              help="the directory to run the daemon in (default: %default)",
                              default=".")
    daemon_options.add_option("-u", "--uid",
                              action="store",
                              help="the userid to run the daemon as (default: inherited from parent process)",
                              type="uid",
                              default=os.getuid())
    daemon_options.add_option("-g", "--gid",
                              action="store",
                              type="gid",
                              help="the groupid to run the daemon as (default: inherited from parent process)",
                              default=os.getgid())
    daemon_options.add_option("-U", "--umask",
                              action="store",
                              type="umask",
                              help="the umask for files created by the daemon (default: 0022)",
                              default=0022)
    daemon_options.add_option("--stdout",
                              help="sends standard output to the file STDOUT if set",
                              action="store")
    daemon_options.add_option("--stderr",
                              help="sends standard error to the file STDERR if set",
                              action="store")
    options.add_option_group(daemon_options)
    return options.parse_args(args)

def collate_configs(filenames):
    _log.debug("Loading configuration files: %r", filenames)
    
    config = ConfigParser.SafeConfigParser()
    config.read(filenames)
    return config

def start_logging(filenames, configure=logging.config.fileConfig):
    for file in filenames:
        configure(file)

def run_sparkplug(
    options,
    conf_files,
    configparse=collate_configs,
    configurer_factory=sparkplug.config.create_configurer,
    connector_factory=sparkplug.config.create_connector,
    configure_logging=start_logging,
):
    configure_logging(conf_files)

    config = configparse(conf_files)
    channel_configurer = configurer_factory(config)
    connector = connector_factory(
        config,
        channel_configurer,
        options.connector,
        options.connection
    )

    try:
        _log.info("Starting sparkplug.");
        connector.run()
    except (SystemExit, KeyboardInterrupt):
        print # GNU Readline hates dangling ^Cs.
    _log.info("Exiting sparkplug normally.");

def main(
    args=sys.argv[1:],
    optparse=sparkplug_options,
    daemon_entry_point=run_sparkplug
):
    options, conf_files = optparse(args)

    if options.daemon:
        with daemon.DaemonContext(
            pidfile=daemon.pidlockfile.PIDLockFile(options.pidfile),
            working_directory=options.working_dir,
            uid=options.uid,
            gid=options.gid,
            umask=options.umask
        ):
            if options.stdout:
                sys.stdout = open(options.stdout, 'a')
            if options.stderr:
                sys.stderr = open(options.stderr, 'a')
        
            try:
                daemon_entry_point(options, conf_files)
            except:
                _log.exception("Dying horribly now.")
                raise
    else:
        daemon_entry_point(options, conf_files)
