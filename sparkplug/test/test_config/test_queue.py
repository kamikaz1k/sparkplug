from nose.tools import eq_
from mock import Mock, call
from sparkplug.config.queue import QueueConfigurer


def test_queue_configurer_arguments_not_passed():
    qc = QueueConfigurer('some_queue', durable='True')
    eq_(qc.create_args,  {'durable': True})
    channel = Mock()
    qc.start(channel)
    eq_([call(queue='some_queue', durable=True)],
        channel.queue_declare.call_args_list)


def test_queue_configurer_takes_arguments():
    arguments = '{"x-dead-letter-exchange": "dlx", "x-ttl": 6000}'
    qc = QueueConfigurer('some_queue', arguments=arguments)
    channel = Mock()
    qc.start(channel)
    eq_([call(queue='some_queue', arguments={
        'x-dead-letter-exchange': 'dlx',
        'x-ttl': 6000})],
        channel.queue_declare.call_args_list)
