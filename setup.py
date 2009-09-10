from setuptools import setup, find_packages

setup(
    name='sparkplug',
    version='1.0',
    
    packages = find_packages(exclude=['*.test', '*.test.*']),
    
    tests_require=[
        'nose >= 0.10.4',
        'mock >= 0.5.0'
    ],
    install_requires=[
        'amqplib >= 0.6.1',
        'python-daemon',
        'functional',
        'python-graph',
        'setuptools' # for pkg_resources, mostly.
    ],
    
    entry_points = {
        'console_scripts': [
            'sparkplug = sparkplug.cli:main'
        ],
        'sparkplug.connectors': [
            'connection = sparkplug.config.connection:AMQPConnector'
        ],
        'sparkplug.configurers': [
            'queue = sparkplug.config.queue:QueueConfigurer',
            'exchange = sparkplug.config.exchange:ExchangeConfigurer',
            'binding = sparkplug.config.binding:BindingConfigurer',
            'consumer = sparkplug.config.consumer:ConsumerConfigurer',
        ],
        'sparkplug.consumers': [
            'echo = sparkplug.examples:EchoConsumer'
        ]
    },
    
    test_suite = 'nose.collector'
)
