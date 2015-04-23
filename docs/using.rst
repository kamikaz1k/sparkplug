Using Sparkplug
---------------

.. highlight:: ini

Sparkplug is driven by a collection of config files defining elements of the
messaging configuration. Included in the sparkplug source is an example::

    [connection:main]
    # The host (or host:port) of the broker node to connect to.
    host = localhost
    # The virtual host to connect to.
    virtual_host = /
    # The user to connect as.
    userid = guest
    # The user's password.
    password = guest
    # If set, forces the use of SSL to connect to the broker.
    ssl = False
    
    [queue:events]
    # Will the queue be declared as durable, and survive broker restarts?
    durable = True
    # Will the queue be declared as auto-deleted, and be removed if all
    # consumers exit?
    auto_delete = False
    # Is the queue exclusive to this program?
    exclusive = False
    # Extra arguments to be passed down to `channel.queue_declare`
    # See http://amqp.readthedocs.org/en/latest/reference/amqp.channel.html#amqp.channel.Channel.queue_declare
    # The value is parsed as a JSON string into a Python dictionary
    arguments = {}
    
    [exchange:postoffice]
    # The exchange type ('direct', 'fanout', or 'topic')
    type = direct
    # Will the exchange be declared as durable, and survive broker restarts?
    durable = True
    # Will the exchange be declared as auto-deleted, and be removed if all
    # producers exit?
    auto_delete = False
    
    [binding:postoffice/events]
    # The name of the queue to bind
    queue = events
    # The exchange to bind to.
    exchange = postoffice
    # The routing key to bind under (optional for some exchange types)
    routing_key = events
    
    [consumer:echo]
    # Entry point identifier
    use = sparkplug#echo
    # Queue to consume against
    queue = events
    # Other parameters will be passed passed to the entry point
    format = %%(body)s
    
    # Configure Python logging
    # <http://docs.python.org/library/logging.html#configuration-file-format>
    #
    # For daemon mode, you probably want to send this to a file or to syslog,
    # not to stdout.
    [loggers]
    keys=root
    
    [handlers]
    keys=consoleHandler
    
    [formatters]
    keys=simpleFormatter
    
    [logger_root]
    level=DEBUG
    handlers=consoleHandler
    
    [handler_consoleHandler]
    class=StreamHandler
    level=DEBUG
    formatter=simpleFormatter
    args=(sys.stdout,)
    
    [formatter_simpleFormatter]
    format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
    datefmt=

.. automodule:: sparkplug.config.connection
.. automodule:: sparkplug.config.queue
.. automodule:: sparkplug.config.exchange
.. automodule:: sparkplug.config.binding
.. automodule:: sparkplug.config.consumer

Magic Placeholders
==================

The `--fork` option allows sparkplug to run multiple processes. Applications
can use this feature to run multiple instances of the same configuration (to
provide some degree of parallelism) or to run a series of closely-related
configurations. Sparkplug provides a value named `worker-number` while parsing
the configuration file, which will be substituted with the serial number of
the sparkplug process. Worker numbers start at `0`.

For example, the configuration::

    [exchange:events]
    type = direct
    
    [queue:events-%(worker-number)s]
    auto_delete = True
    
    [binding:events/events-%(worker-number)s]
    exchange = events
    queue = events-%(worker-number)s
    routing_key = events
    
    [consumer:events]
    use = sparkplug#echo
    queue = events-%(worker-number)s
    
    format = %%(body)s

will create two queues (with `--fork=2`) named `events-0` and `events-1`, with
associated bindings and consumers.

The `worker-number` placeholder is set to `0` if `--fork` is not set.
