from setuptools import setup, find_packages

setup(
    name='sparkplug',
    version='1.0.4',
    author='Owen Jacobson',
    author_email='owen.jacobson@grimoire.ca',
    url='http://alchemy.grimoire.ca/python/sites/sparkplug/',
    download_url='http://alchemy.grimoire.ca/python/releases/sparkplug/',
    description='An AMQP message consumer daemon',
    
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
        'Topic :: Utilities'
    ],
    
    packages = find_packages(exclude=['*.test', '*.test.*']),
    
    tests_require=[
        'nose >= 0.10.4',
        'mock >= 0.5.0'
    ],
    install_requires=[
        'amqplib >= 0.6.1',
        'python-daemon == 1.5.5',
        'functional',
        'python-graph-core == 1.6.2',
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
