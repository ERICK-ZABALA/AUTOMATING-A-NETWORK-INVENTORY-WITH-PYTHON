#!/usr/bin/env python
""" Unit tests for the schemaengine within metaparser package"""

import unittest, yaml
from ipaddress import IPv4Interface, IPv6Interface

from genie.metaparser.util.schemaengine import Schema, Any, Optional, Or, And, Default, Use
from genie.metaparser.util.schemaengine import Fallback
from genie.metaparser.util.schemaengine import (SchemaValueError, SchemaClassError, 
                                       SchemaTypeError, SchemaMissingKeyError,
                                       SchemaUnsupportedKeyError, 
                                       SchemaEmptyParserError)


class TestPathClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global Path, Any

        from genie.metaparser.util.schemaengine import Path, Any

    def test_init(self):
        path = Path((1,2,3))
        self.assertTrue(isinstance(path, tuple))

    def test_dynamic(self):
        path = Path((1, 2, 3))
        self.assertFalse(path.is_dynamic())

        path = Path((1, Any(), 3))
        self.assertTrue(path.is_dynamic())

        path = Path((1, Any(), Any()))
        self.assertTrue(path.is_dynamic())

        path = Path((Any(), Any(), Any()))
        self.assertTrue(path.is_dynamic())

    def test_missing_from(self):
        missings = Path((1, Any(), 2)).missing_from(((1,2,3), (2,3,4)))
        self.assertEqual(missings, [(1,2,2)])
        missings = Path((1, Any(), Any(), 2)).missing_from(((1,2,3,5), 
                                                            (1,3,4)))
        self.assertEqual(missings, [(1,2,3,2)])

        missings = Path((1, Any(), Any(), 5)).missing_from(((1,2,3,5), 
                                                            (1,3,4,6)))
        self.assertEqual(set(missings), set([(1,3,3,5), (1,2,4,5), (1,3,4,5)]))

        missings = Path((1, Any(), Any())).missing_from(((1,2,3), 
                                                            (1,3,4)))
        self.assertEqual(set(missings), set([(1,3,3), (1,2,4)]))

    def test_eq(self):
        self.assertEqual(Path((1, 2, 3)), Path((1, 2, 3)))
        self.assertEqual(Path((1, 2, 3)), Path((1, Any(), 3)))
        self.assertEqual(Path((Any(), 2, 3)), Path((1, Any(), 3)))
        self.assertNotEqual(Path((2, 3)), Path((1, Any(), 3)))

class TestSchemaEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.schema = Schema({
            'devices': {
                Any() : {
                    'type': str,
                    'connections': {
                        Any(): Any(),
                    },
                },
            },
            
            Optional('topology'): {
                Any(): {
                    'interfaces': {
                        Any(): {
                            'type': str,
                            Optional('link'): str,
                            Optional('ipv4'): IPv4Interface,
                            Optional('ipv6'): IPv6Interface,
                            Any(): Any(),
                        },
                    },
                },
            }, 
        })

    def test_simple_scheme(self):
        schema = Schema({'b' : 'b', 'a' : 'a'})

        schema.validate({'b' : 'b', 'a' : 'a'})
    
    def test_default(self):
        schema = Schema(Default(str, ''))
        with self.assertRaises(SchemaEmptyParserError):
            data = schema.validate(None)

        schema = Schema(Default(dict, {'lalala': 'dict'}))
        with self.assertRaises(SchemaEmptyParserError):
            data = schema.validate({})

    def test_default_dict(self):
        schema = Schema({'a': Default(str, 'default')})
        data = schema.validate({'a': 'default'})
        self.assertEqual(data, {'a': 'default'})

    def test_default_dict_nested(self):
        schema = Schema({
            'a': {
                'b': {
                    'c': Default(str, 'default'),
                },
            },
        })
        data = schema.validate({'a': {'b': {'c': 'default'}}})
        self.assertEqual(data, {'a': {'b': {'c': 'default'}}})

    def test_default_dict_nested_complex(self):
        schema = Schema({
            'a': {
                'b': {
                    'c': Default(str, 'default'),
                    'd': int,
                },
            },
        })
        data = schema.validate({
            'a': {
                'b': {
                    'd': 1,
                },
            },
        })
        self.assertEqual(data, {'a': {'b': {'c': 'n/a', 'd': 1}}})

    def test_default_clash(self):
        schema = Schema({
            'a': {
                'b': {
                    'c': Default(str, 'default'),
                }
            }
        })
        data = schema.validate({
            'a': {
                'b': {
                    'c': '1',
                },
            },
        })
        self.assertEqual(data, {'a': {'b': {'c': '1'}}})

    def test_default_fallthrough(self):
        schema = Schema(Default(str, ''))
        data = schema.validate('some string')
        self.assertEqual(data, 'some string')

    def test_default_error(self):
        schema = Schema(Default(str, ''))
        with self.assertRaises(SchemaTypeError):
            schema.validate(1)

        schema = Schema({
            'a': {
                'b': {
                    'c': Default(str, 'default'),
                    'd': str,
                },
            },
        })
        data = {
            'a': {
                'b': {
                    'd': 1,
                },
            },
        }

        with self.assertRaises(SchemaTypeError):
            schema.validate(data)

    def test_simple_fallback(self):
        test_schema = {
            'a': int,
            'b': Fallback(int, 'a')
        }

        schema = Schema(test_schema)
        data = schema.validate({'a': 1})
        self.assertEqual(data['b'], 1)

    def test_complex_fallback(self):
        test_schema = {
            'a': {
                'b': {
                    'c' : {
                        'd': 'd_value',
                    },
                },
            },
            'x': {
                Any():{
                    'y': Fallback(str, 'a.b.c.d'),
                    'z': int,
                }
            }
        }

        data = {
            'a': {
                'b': {
                    'c' : {
                        'd': 'd_value',
                    },
                },
            },
            'x': {
                'any': {
                    'z': 100,
                }
            }
        }

        schema = Schema(test_schema)
        valid_data = schema.validate(data)
        self.assertEqual(valid_data['x']['any']['y'], 'd_value')
        self.assertEqual(valid_data['x']['any']['z'], 100)

    def test_fallback_nested_complex(self):
        test_schema = {
            'a': {
                'b': {
                    'c' : {
                        'd': 'd_value',
                    },
                },
            },
            'x': {
                'y': Fallback(str, 'a.b.c.d'),
                'z': str,
            }
        }

        data = {
            'a': {
                'b': {
                    'c' : {
                        'd': 'd_value',
                    },
                },
            },
            'x': {
                'z': 'woot',
            }
        }

        schema = Schema(test_schema)
        valid_data = schema.validate(data)
        self.assertEqual(valid_data['x']['y'], 'd_value')
        self.assertEqual(valid_data['x']['z'], 'woot')

    def test_fallback_with_default(self):
        test_schema = {
            'a': Default(int, 999),
            'b': Fallback(int, 'a')
        }
        data = {
            'a': 999,
            'b': 999
        }
        schema = Schema(test_schema)
        data = schema.validate(data)
        self.assertEqual(data['a'], 999)
        self.assertEqual(data['b'], 999)

    def test_fallback_with_fallback_to_default(self):
        test_schema = {
            'a': {
                'b': {
                    'c' : {
                        'd': Default(str, 'd_value'),
                    },
                },
            },
            'x': {
                'y': Fallback(str, 'a.b.c.d'),
                'z': str,
            },
            'o': {
                'p': {
                    'q': Fallback(str, 'x.y')
                }
            }
        }

        data = {
            'a': {
                'b': {
                    'c' : {
                        'd': 'd_value',
                    },
                },
            },
            'x': {
                'z': 'woot',
            }
        }

        schema = Schema(test_schema)
        valid_data = schema.validate(data)
        self.assertEqual(valid_data['a']['b']['c']['d'], 'd_value')
        self.assertEqual(valid_data['x']['y'], 'd_value')
        self.assertEqual(valid_data['x']['z'], 'woot')
        self.assertEqual(valid_data['o']['p']['q'], 'd_value')

    def test_mega_fallbacks(self):
        test_schema = {
            'a': {
                'b': {
                    'c' : {
                        'd': Default(str, 'd_value'),
                        'e': Fallback(str, 'a.b.c.d')
                    },
                },
            },
            'x': {
                'y': Fallback(str, 'a.b.c.e'),
                'z': Fallback(str, 'x.y'),
            },
            'o': {
                'p': {
                    'q': Fallback(str, 'x.z')
                }
            }
        }
        data = {
            'a': {
                'b': {
                    'c' : {
                        'd': 'd_value',
                        'e': 'd_value'
                    },
                },
            },
            'x': {
                'y': 'd_value',
                'z': 'd_value',
            },
            'o': {
                'p': {
                    'q': 'd_value'
                }
            }
        }
        schema = Schema(test_schema)
        valid_data = schema.validate(data)
        self.assertEqual(valid_data['a']['b']['c']['d'], 'd_value')
        self.assertEqual(valid_data['a']['b']['c']['e'], 'd_value')
        self.assertEqual(valid_data['x']['y'], 'd_value')
        self.assertEqual(valid_data['x']['z'], 'd_value')
        self.assertEqual(valid_data['o']['p']['q'], 'd_value')

    def test_infinite_fallback_loop(self):
        from genie.metaparser.util.exceptions import SchemaFallbackLoopError
        schema = Schema({
            'a': Fallback(str, 'b'),
            'b': Fallback(str, 'a'),
        })
        data = {
            'a': {'b'},
            'b': {'a'}
        }
        with self.assertRaises(SchemaFallbackLoopError):
            valid_data = schema.validate(data)

    def test_fallback_to_self(self):
        from genie.metaparser.util.exceptions import SchemaFallbackLoopError
        schema = Schema({'a': Fallback(str, 'a')})
        data = {'a': {'a'}}
        with self.assertRaises(SchemaFallbackLoopError):
            schema.validate(data)

    def test_fallback_to_none(self):
        from genie.metaparser.util.exceptions import SchemaFallbackError
        test_schema = {
            'a': {
                'b': {
                    'c' : {
                        'd': Fallback(str, 'x.y.z')
                    },
                },
            },
        }
        data = {
            'a': {
                'b': {
                    'c' : {
                        'd': ''
                    },
                },
            },
        }
        schema = Schema(test_schema)
        with self.assertRaises(SchemaFallbackError):
            valid_data = schema.validate(data)

    def test_dynamic_any(self):
        # dynamic first level *
        schema = Schema({Any() : str})
        schema.validate({'b' : 'b', 'a' : 'a'})

    def test_mandatory_mismatch(self):
        # requirement mismatch (required missing, has extra)
        schema = Schema({'c': ''})
        with self.assertRaises(SchemaMissingKeyError):
            schema.validate({'b' : 'b', 'a' : 'a'})

    def test_or(self):
        schema = Schema(Or(2, 1))
        schema.validate(2)
        schema.validate(1)

    def test_or_as_key(self):
        test_schema = {
            'a': {
                Or(Optional('b'), Optional('c')): {
                    'x' : 'y'
                },
            },
        }
        schema = Schema(test_schema)
        schema.validate({'a': {'b': {'x':'y'}}})
        schema.validate({'a': {'c': {'x':'y'}}})
        with self.assertRaises(SchemaTypeError):
            schema.validate({'a': None})

    def test_and(self):
        schema = Schema(And(1, int))
        schema.validate(1)

        schema = Schema(And(1, None))
        with self.assertRaises(SchemaValueError):
            schema.validate(1)

    def test_optional(self):
        schema = Schema({Optional('a'): str})
        schema.validate({'a': ''})
        schema.validate({'a': 'lalala'})

    def test_type_mismatch(self):
        schema = Schema(dict)
        with self.assertRaises(SchemaTypeError):
            schema.validate(str)

    def test_nested_type_mismatch(self):
        schema = Schema({'': dict})
        with self.assertRaises(SchemaTypeError):
            schema.validate({'': ''})

    def test_use(self):
        def f(x):
            return x+1

        schema = Schema(And(Use(f), int))
        data = schema.validate(1)
        self.assertEqual(data, 2)

    def test_and(self):
        schema = Schema(And(Use(lambda s: s+1), Use(lambda y: str(y)), str))
        data = schema.validate(1)

        self.assertEqual(data, '2')

    def test_type_as_keys(self):
        schema = Schema({str: int})
        schema.validate({'': 1})

        with self.assertRaises(SchemaTypeError):
            schema.validate({'': ''})

        with self.assertRaises(SchemaMissingKeyError):
            schema.validate({1: ''})

    def test_multiple_level_with_any(self):
        schema = Schema({'a' : { Any(): str},
                         'b' : { Any(): {'z': str,
                                       'w': str}},
                         'c': int})
        schema.validate({'a' : {'1': '1',
                                '2': '2'},
                         'b' : {'y': {'z': 'zzz',
                                      'w': 'www'}},
                         'c' : 111})

    def test_multiple_level_errors(self):
        schema = Schema({'a' : { Any(): str},
                         'b' : { Any(): {'z': str,
                                         'w': str}},
                         'c': int})
        with self.assertRaises(SchemaMissingKeyError):
            schema.validate({'a' : {'1': '1',
                                    '2': '2'},
                             'b' : {'y': {'z': 'zzz',
                                          'w': 'www'}},
                             'z' : 111})

        with self.assertRaises(SchemaMissingKeyError):
            schema.validate({'a' : {'1': '1',
                                    '2': '2'},
                             'b' : {'y': {'w': 'www'}},
                             'c' : 111})
    def test_callables(self):
        from ipaddress import IPv4Address, IPv6Address
        schema = Schema({1: IPv4Address,
                         2: IPv6Address,})
        data = schema.validate({1: '192.168.1.1',
                                2: '2001:db8::1000'})
        self.assertEqual(data, {1: IPv4Address('192.168.1.1'),
                                2: IPv6Address('2001:db8::1000')})

    def test_and_callable(self):
        import socket
        from ipaddress import IPv4Address
        schema = And(Use(socket.gethostbyname), IPv4Address)

        data = schema.validate('localhost')
        self.assertTrue(isinstance(data, IPv4Address))
        self.assertEqual(data, IPv4Address(socket.gethostbyname('localhost')))

    def test_callable_err(self):
        from ipaddress import IPv4Address, IPv6Address
        schema = Schema({1: IPv4Address,
                         2: IPv6Address,})
        with self.assertRaises(SchemaClassError):
            schema.validate({1: '192.168.1.1',
                             2: 'blah'})

    def test_minimal_production_schema(self):
        data = yaml.safe_load('''
devices:
    testDevice:
        type: 'test device'
        connections:
            a:
                protocol: telnet
                ip: 1.1.1.1
''')
        # must have at least devices defined
        self.schema.validate(data)

    def test_optional_production_schema_first_level(self):
        data = yaml.safe_load('''
devices:
    testDevice:
        type: 'test device'
        connections:
            a:
                protocol: telnet
                ip: 1.1.1.1

topology:
    testDevice:
        interfaces:
            Eth1:
                type: Ethernet
''')
        self.schema.validate(data)

    def test_production_schema_extra_first_level(self):
        data = yaml.safe_load('''
devices:
    testDevice:
        type: 'test device'
        connections:
            a:
                protocol: telnet
                ip: 1.1.1.1

topology:
    testDevice:
        interfaces:
            Eth1:
                type: Ethernet
iamextra:
''')
        with self.assertRaises(SchemaUnsupportedKeyError):
            self.schema.validate(data)

    def test_pathing_simple_error(self):
        schema = Schema(1)
        with self.assertRaises(SchemaValueError):
            schema.validate(str(1))

    def test_pathing_nested(self):
        schema = Schema({1:{2:{3:{4:{5:6}}}}})
        schema.validate({1:{2:{3:{4:{5:6}}}}})

    def test_pathing_nested_err(self):
        schema = Schema({1:{2:{3:{4:{5:6}}}}})
        with self.assertRaises(SchemaValueError):
            schema.validate({1:{2:{3:{4:{5:7}}}}})

    def test_pathing_complex(self):
        data = yaml.safe_load('''
devices:
    testDevice:
        type: 'test device'
        connections:
            a:
                protocol: telnet
                ip: 1.1.1.1

topology:
    testDevice:
        interfaces:
            Eth1:
                type: Ethernet
                ipv4: 1.1.1.1
''')
        self.schema.validate(data)

    def test_pathing_complex_err(self):
        data = yaml.safe_load('''
devices:
    testDevice:
        type: 'test device'
        connections:
            a:
                protocol: telnet
                ip: 1.1.1.1

topology:
    testDevice:
        interfaces:
            Eth1:
                type: Ethernet
                ipv4: not_an_ip
''')
        with self.assertRaises(SchemaClassError):
            self.schema.validate(data)

    def test_pathing_nested_extras(self):
        data = yaml.safe_load('''
devices:
    testDevice:
        type: 'test device'
        connections:
            a:
                protocol: telnet
                ip: 1.1.1.1
        extra_key:
            lalala: 1
''')
        with self.assertRaises(SchemaUnsupportedKeyError):
            self.schema.validate(data)

    def test_parser_different_context_retry_missing_key_message(self):

        schema = Schema({Optional('intf_list'): list,
              'intf':
                {Any():
                    {'access_map_sequence':
                        {Any():
                            {'neighbor': str,
                             'interface_address': str,
                             'area': str,
                             'state': str,
                             'state_changes': str,
                             'neigh_priority': str,
                             'dr': str,
                             'bdr':str,
                             'uptime':str}
                        }
                    }
                },
            })

        with self.assertRaises(SchemaMissingKeyError):
            schema.validate({'intf':
                                {'GigabitEthernet3':
                                    {'access_map_sequence':
                                        {'yes_we_can':
                                            {'area': '0',
                                             'bdr': '192.0.0.1',
                                             'dr': '192.0.0.2',
                                             'interface_address': '192.0.0.2',
                                             'neigh_priority': '1',
                                             # 'neighbor': '192.0.0.2',
                                             'state': 'FULL',
                                             'state_changes': '6',
                                             'uptime': '05:08:57'}}},
                                 'GigabitEthernet4':
                                    {'access_map_sequence':
                                        {'yes_we_can':
                                            {'area': '0',
                                             'bdr': '192.0.0.5',
                                             'dr': '192.0.0.6',
                                             'interface_address': '192.0.0.6',
                                             'neigh_priority': '1',
                                             'neighbor': '192.0.0.9',
                                             # 'state': 'FULL',
                                             'state_changes': '6',
                                             'uptime': '05:07:51'}}}}})

    def test_missing_key_root_and_sub_levels(self):
        schema = Schema({'a': str,
                         'b': str,
                         'c': {
                             'd': str,
                             'e': str
                         },
                         'f': str
                         })
        try:
            schema.validate({
                'a':'a',
                'c':{
                    'e':'e'
                }
            })
        except SchemaMissingKeyError as e:
            # order does not matter so convert  to set
            self.assertEqual(set(tuple(e) for e in e.missing_list),
                             set(tuple(e) for e in [['b'], ['f'], ['c', 'd']]))

    def test_merge_unsupported_keys(self):
        schema = Schema({'c': {
                            'd': str
                         }})
        try:
            schema.validate({
                'c': {
                    'd': 'd',
                    'a': 'a',
                    'b': 'b',
                }
            })
        except SchemaUnsupportedKeyError as e:
            self.assertEqual(set(tuple(e) for e in e.unsupported_keys),
                            set(tuple(e) for e in [['c','a'],['c', 'b']]))

if __name__ == "__main__": # pragma: no cover
    unittest.main()
