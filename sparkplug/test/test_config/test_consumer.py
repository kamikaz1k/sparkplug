import mock

from sparkplug.config.consumer import parse_use, ConsumerConfigurer

def _raise(type, value=None):
    raise type, value

def test_parse_use_basic():
    load_entry_point = mock.Mock()
    load_entry_point.return_value = mock.sentinel.entry_point
    
    entry_point = parse_use("test group", "funkydist#start_here", load_entry_point=load_entry_point)
    
    assert mock.sentinel.entry_point == entry_point
    assert (('funkydist', 'test group', 'start_here'), {}) == load_entry_point.call_args

def test_parse_use_oops():
    load_entry_point = mock.Mock()
    load_entry_point.side_effect = lambda *args: _raise(ImportError)
    
    try:
        parse_use("test group", "ohfail#throw now please", load_entry_point=load_entry_point)
        assert False
    except ImportError:
        pass

def test_configure_basic():
    builder = mock.Mock()
    
    