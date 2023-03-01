#!/usr/bin/env python
""" Unit tests for the metaparser cisco-shared package. """

import unittest
from unittest.mock import Mock
import xmltodict
import copy

# Unicon
import unicon

from genie.metaparser import MetaParser
from genie.metaparser.util import keynames_exist
from genie.metaparser.util.schemaengine import Any, Optional
from genie.metaparser.util.traceabledict import TraceableDict
from genie.metaparser.util.exceptions import SchemaEmptyParserError,\
                                       SchemaMissingKeyError,\
                                       SchemaUnsupportedKeyError,\
                                       InvalidCommandError

class TestMetaparser(unittest.TestCase):
    def setUp(self):
        pass

    def test_parse_cli(self):
        parser = ShowVersion(device=Mock(), arg='')
        output = parser.parse()

        keylist = ['hardware.bootflash', 'hardware.chassis', 'hardware.cpu',
                   'hardware.device_name', 'hardware.memory',
                   'hardware.model', 'hardware.processor_board_id']
        self.assertEqual(keynames_exist(output, keylist), None)

    def test_parse_cli_with_filter(self):
        parser = ShowVersion(device=Mock())
        selected_keys = [['hardware', 'bootflash'],
                         ['cmp', 'module', r'.*', 'bios_compile_time'],
                         ['hardware', r'^slot']]

        output = parser.parse(selected_keys = selected_keys)

        keylist = ['hardware.bootflash', 'cmp.module.1.bios_compile_time',
                   'hardware.slot0', 'hardware.slots']

        self.assertEqual(keynames_exist(output, keylist), None)

    def test_parse_with_raw_data(self):
        device = Mock()
        device.is_connected.return_value = True
        device.execute.return_value = 'raw output'

        expected_raw_output = [
            {'command': 'some command', 'kwargs': {}, 'output': 'raw output'}]
        parser = ShowRawData(device=device)
        output = parser.parse(raw_data=True)

        self.assertEqual(parser.raw_output, expected_raw_output)
        self.assertEqual(parser.parsed_output, output)

    def test_parse_with_schemachecking_failed(self):
        parser = ShowVersion(device=Mock())
        parser.schema = {'cmp': {
                        'module': {
                                 Any(): {
                                         'bios_compile_time': str,
                                         'bios_version': str,
                                         'image_compile_time': str,
                                         'image_version': str,
                                         'status': str},}},
                         'fake': Any(),}
        with self.assertRaises(Exception):
            parser.parse()

    def test_parse_with_select_keys_failed(self):
        parser = ShowVersion(device=Mock())
        selected_keys = [['fake', 'bootflash'],
                         ['cmp', 'module', '*', 'bios_compile_time'],
                         ['hardware', r'^slot']]
        with self.assertRaises(KeyError):
            parser.parse(selected_keys=selected_keys)

    def test_parse_with_select_keys_failed_tuple_format(self):
        parser = ShowVersion(device=Mock())
        selected_keys = [('fake', 'bootflash'),
                         ('cmp', 'module', '*', 'bios_compile_time'),
                         ('hardware', r'^slot')]
        with self.assertRaises(KeyError):
            parser.parse(selected_keys=selected_keys)

    def test_parser_init_failed(self):
        with self.assertRaises(AssertionError):
            ShowVersion(device=Mock(), context='text')

    def test_parse_nonimplementation_error(self):
        parser = ShowVersion_NoCli(device=Mock())
        with self.assertRaises(AttributeError):
            parser.parse()

    def test_parse_Invalid_command(self):
        parser = ShowVersion_InvalidCommand(device=Mock())
        with self.assertRaises(InvalidCommandError):
            parser.parse()

    def test_parse_xml(self):
        parser = ShowVersion(device=Mock(), context='xml')
        output = parser.parse()

        keylist = ['cmp.module.*.bios_compile_time',
                   'cmp.module.*.bios_version',
                   'cmp.module.*.image_compile_time',
                   'cmp.module.*.image_version',
                   'cmp.module.*.status']
        self.assertEqual(keynames_exist(output, keylist), None)

    def test_parse_yang(self):
        parser = ShowVersion(device=Mock(), context='yang')
        output = parser.parse()

        keylist = ['cmp.module.1.bios_compile_time',
                   'cmp.module.1.bios_version',
                   'cmp.module.1.image_compile_time',
                   'cmp.module.1.image_version',
                   'cmp.module.1.status']
        self.assertEqual(keynames_exist(output, keylist), None)

    def test_tracer(self):
        TraceableDict.tracer = {}
        # before init
        self.assertEqual(MetaParser.tracer, {})
        parser = ShowVersion(device=Mock())
        output = parser.parse()
        output['hardware']['chassis']
        self.assertEqual(MetaParser.tracer, {})

        # init tracing
        MetaParser.key_traceable = True
        parser = ShowVersion(device=Mock())
        output = parser.parse()

        self.assertEqual(list(MetaParser.tracer.values())[0], set())

        # access keys
        output['hardware']['chassis']
        self.assertEqual(list(MetaParser.tracer.values())[0], {('hardware', 'chassis')})

        # creat new parser obj from same parser
        parser_xml = ShowVersion(device=Mock(), context='xml',
                                 key_traceable=True)
        output = parser_xml.parse()
        output['hardware']['cpu']

        self.assertEqual(list(MetaParser.tracer.values())[0],
                         {('hardware', 'chassis'), ('hardware', 'cpu')})

    def test_parser_output_type(self):
        context='cli'
        parser = ShowAnything(device=Mock(),
                              context=context)

        with self.assertRaises(TypeError):
            parser.parse()

    def test_parser_context_string_missing_keys(self):
        context='yang'
        parser = ShowIpOspfNeighborDetailSchema(device=Mock(),
                                                context=context)
        with self.assertRaises(SchemaMissingKeyError):
            parsed_output = parser.parse()

    def test_parser_different_context_retry_parse_merge_list(self):
        context=['cli','xml']
        parser = ShowIpOspfNeighborDetailSchema(device=Mock(),
                                                context=context)
        parsed_output = parser.parse()
        golden_output = {'intf':
                            {'GigabitEthernet3':
                                {'access_map_sequence':
                                    {'yes_we_can':
                                        {'area': '0',
                                         'bdr': '192.0.0.1',
                                         'dr': '192.0.0.2',
                                         'interface_address': '192.0.0.2',
                                         'neigh_priority': '1',
                                         'neighbor': '192.0.0.2',
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
                                         'state': 'FULL',
                                         'state_changes': '6',
                                         'uptime': '05:07:51'}}}}}

        self.maxDiff = None
        self.assertEqual(parsed_output, golden_output)

    def test_parser_different_context_retry_merge_multiple_cntxts(self):
        context=['cli','xml','yang']
        parser = ShowIpOspfNeighborDetailSchema(device=Mock(),
                                                context=context)
        parsed_output = parser.parse()
        golden_output = {'intf':
                            {'GigabitEthernet3':
                                {'access_map_sequence':
                                    {'yes_we_can':
                                        {'area': '0',
                                         'bdr': '192.0.0.1',
                                         'dr': '192.0.0.2',
                                         'interface_address': '192.0.0.2',
                                         'neigh_priority': '1',
                                         'neighbor': '192.0.0.2',
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
                                         'state': 'FULL',
                                         'state_changes': '6',
                                         'uptime': '05:07:51'}}}}}

        self.maxDiff = None
        self.assertEqual(parsed_output, golden_output)

    def test_parser_different_context_retry_merge_multiple_cntxts_two(self):
        context=['cli','yang','xml', 'cli']
        parser = ShowIpOspfNeighborDetailSchema(device=Mock(),
                                                context=context)
        parsed_output = parser.parse()
        golden_output = {'intf':
                            {'GigabitEthernet3':
                                {'access_map_sequence':
                                    {'yes_we_can':
                                        {'area': '0',
                                         'bdr': '192.0.0.1',
                                         'dr': '192.0.0.2',
                                         'interface_address': '192.0.0.2',
                                         'neigh_priority': '1',
                                         'neighbor': '192.0.0.2',
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
                                         'state': 'FULL',
                                         'state_changes': '6',
                                         'uptime': '05:07:51'}}}}}

        self.maxDiff = None
        self.assertEqual(parsed_output, golden_output)

    def test_parser_different_context_retry_merge_multiple_cntxts_three(self):
        # Both cli and yang are incomplete structures compared to the schema
        context=['cli','yang']
        parser = ShowIpOspfNeighborDetailSchema(device=Mock(),
                                                context=context)

        with self.assertRaises(SchemaMissingKeyError):
            parsed_output = parser.parse()

    def test_parser_different_context_merge_multiple_cntxts_ignore_update(self):
        '''
            Test the case where the two contexts have the same key with
            different values and we want to ignore the key value of the
            latest context output.
        '''

        context=['cli','xml']
        parser = ShowIpBgpNeighborDetailSchema(device=Mock(),
                                               context=context)
        parsed_output = parser.parse()
        golden_output = {'intf':
                            {'GigabitEthernet3':
                                {'access_map_sequence':
                                    {'yes_we_can':
                                        {'area': '0',
                                         'bdr': '192.0.0.1',
                                         'dr': '192.0.0.2',
                                         'interface_address': '192.0.0.2',
                                         'neigh_priority': '1',
                                         'neighbor': '192.0.0.2',
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
                                         'state': 'FULL',
                                         'state_changes': '6',
                                         'uptime': '05:07:51'}}}}}

        self.assertEqual(parsed_output, golden_output)

    def test_parser_argument_passing_to_the_parser(self):
        ''' Parser accepts argument banana'''
        context=['cli']
        parser = ShowVersionCopy(device=Mock(),
                                 context=context)

        parsed_output = parser.parse(banana=5)

    def test_parser_missing_argument_passing_to_the_parser(self):
        ''' Parser is missing argument banana'''
        context=['cli']
        parser = ShowVersionCopy(device=Mock(),
                                 context=context)

        with self.assertRaises(TypeError):
            parsed_output = parser.parse()

    def test_parser_having_extra_key_under_optional_branch(self):
        ''' Parser contains an extra key under an Optional branch'''
        parser = ShowVersionInvalidSchema(device=Mock(), arg='')

        with self.assertRaises(SchemaUnsupportedKeyError):
            parsed_output = parser.parse()


class ShowVersion(MetaParser):
    schema = {'cmp': {
                        'module': {
                                 Any(): {
                                         'bios_compile_time': str,
                                         'bios_version': str,
                                         'image_compile_time': str,
                                         'image_version': str,
                                         'status': str},}},
              Any(): Any(),}

    def cli(self, **kwargs):
        result = {'cmp': {'module':
                          {'1':
                                {'bios_compile_time': '8/ 4/2008 19:39:40',
                                'bios_version': '02.01.05',
                                'image_compile_time': '9/25/2011 2:00:00',
                                'image_version': '6.0(1) [build 6.0(0.66)]',
                                'status': 'ok'},
                            '2':
                                {'bios_compile_time': '8/ 4/2008 19:39:40',
                                'bios_version': '02.01.05',
                                'image_compile_time': '9/25/2011 2:00:00',
                                'image_version': '6.0(1) [build 6.0(0.66)]',
                                'status': 'ok'}}},
                 'hardware': {'bootflash': '2048256',
                              'chassis': 'Supervisor Module-1X',
                              'cpu': 'Intel(R) Xeon(R)',
                              'device_name': 'PE1',
                              'memory': '8260604',
                              'model': 'Nexus7000 C7009',
                              'processor_board_id': 'JAF1608ADKR',
                              'slot0': '2093273',
                              'slots': '9'},}

        return result

    def xml(self, **kwargs):
        result = {'hardware': {'bootflash': '2048256',
                              'chassis': 'Supervisor Module-1X',
                              'cpu': 'Intel(R) Xeon(R)',
                              'device_name': 'PE1',
                              'memory': '8260604',
                              'model': 'Nexus7000 C7009',
                              'processor_board_id': 'JAF1608ADKR',
                              'slot0': '2093273',
                              'slots': '9'},}


        # transform the parser output to compliance with CLI version
        result.update({'cmp':{'module':{'*':{'bios_compile_time':'',
                                             'bios_version':'',
                                             'image_compile_time':'',
                                             'image_version':'',
                                             'status':'',}}}})
        return result

    def yang(self, **kwargs):
        ncout = '<?xml version="1.0" encoding="UTF-8"?>\n<rpc-reply '\
        'xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" '\
        'message-id="101"><data><native xmlns="urn:ios">'\
        '<version>6.0.(x)</version></native></data></rpc-reply>'

        filtered_result = xmltodict.parse(ncout,
                                          process_namespaces=True,
                                          namespaces={
                                'urn:ietf:params:xml:ns:netconf:base:1.0':None,
                                'urn:ios':None,})

        partial_result = dict(
                            filtered_result['rpc-reply']['data'].get('native'))

        # to fullfill the schema, need to complet the dict by meging cli output
        cli_result = self.cli()
        result = copy.copy(cli_result)
        result.update(partial_result)
        return result

class ShowVersionCopy(MetaParser):
    schema = {'cmp': {
                        'module': {
                                 Any(): {
                                         'bios_compile_time': str,
                                         'bios_version': str,
                                         'image_compile_time': str,
                                         'image_version': str,
                                         'status': str},}},
              Any(): Any(),}

    def cli(self, banana, **kwargs):
        result = {'cmp': {'module':
                          {'1':
                                {'bios_compile_time': '8/ 4/2008 19:39:40',
                                'bios_version': '02.01.05',
                                'image_compile_time': '9/25/2011 2:00:00',
                                'image_version': '6.0(1) [build 6.0(0.66)]',
                                'status': 'ok'},
                            '2':
                                {'bios_compile_time': '8/ 4/2008 19:39:40',
                                'bios_version': '02.01.05',
                                'image_compile_time': '9/25/2011 2:00:00',
                                'image_version': '6.0(1) [build 6.0(0.66)]',
                                'status': 'ok'}}},
                 'hardware': {'bootflash': '2048256',
                              'chassis': 'Supervisor Module-1X',
                              'cpu': 'Intel(R) Xeon(R)',
                              'device_name': 'PE1',
                              'memory': '8260604',
                              'model': 'Nexus7000 C7009',
                              'processor_board_id': 'JAF1608ADKR',
                              'slot0': '2093273',
                              'slots': '9'},}

        return result


class ShowVersion_NoCli(MetaParser):
    pass

class ShowVersion_InvalidCommand(MetaParser):

    def cli(self, **kwargs):
        raise unicon.core.errors.SubCommandFailure

class ShowAnything(MetaParser):

    def cli(self, **kwargs):
        return 'hey'

class ShowIpOspfNeighborDetailSchema(MetaParser):
    schema = {Optional('intf_list'): list,
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
            }

    def cli(self, **kwargs):

        result = {'intf':
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
                                 # 'neighbor': '192.0.0.9',
                                 'state': 'FULL',
                                 # 'state_changes': '6',
                                 'uptime': '05:07:51'}}}}}

        return result

    def yang(self, **kwargs):

        result = {'intf':
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
                                 # 'neighbor': '192.0.0.9',
                                 'state': 'FULL',
                                 # 'state_changes': '6',
                                 'uptime': '05:07:51'}}}}}

        return result

    def xml(self, **kwargs):

        result = {'intf':
                    {'GigabitEthernet3':
                        {'access_map_sequence':
                            {'yes_we_can':
                                {'area': '0',
                                 'bdr': '192.0.0.1',
                                 'dr': '192.0.0.2',
                                 'interface_address': '192.0.0.2',
                                 'neigh_priority': '1',
                                 'neighbor': '192.0.0.2',
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
                                 'state': 'FULL',
                                 'state_changes': '6',
                                 'uptime': '05:07:51'}}}}}

        return result


class ShowIpBgpNeighborDetailSchema(MetaParser):
    schema = {Optional('intf_list'): list,
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
            }

    def cli(self, **kwargs):

        result = {'intf':
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
                                 # 'neighbor': '192.0.0.9',
                                 'state': 'FULL',
                                 # 'state_changes': '6',
                                 'uptime': '05:07:51'}}}}}

        return result

    def xml(self, **kwargs):

        result = {'intf':
                    {'GigabitEthernet3':
                        {'access_map_sequence':
                            {'yes_we_can':
                                {'area': '1',
                                 'bdr': '192.0.0.1',
                                 'dr': '192.0.0.2',
                                 'interface_address': '192.0.0.2',
                                 'neigh_priority': '1',
                                 'neighbor': '192.0.0.2',
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
                                 'state': 'FULL',
                                 'state_changes': '6',
                                 'uptime': '05:07:51'}}}}}

        return result


class ShowVersionInvalidSchema(MetaParser):
    schema = {'cmp':
                {'module':
                    {Any():
                        {'bios_compile_time': str,
                         'bios_version': str,
                         'image_compile_time': str,
                         'image_version': str,
                         'status': str}
                    }},
            Optional('new_module'):
                {Optional(Any()):
                    {'new_key':str}}}

    def cli(self, **kwargs):
        result = {'cmp':
                    {'module':
                        {'1':
                            {'bios_compile_time': '8/ 4/2008 19:39:40',
                            'bios_version': '02.01.05',
                            'image_compile_time': '9/25/2011 2:00:00',
                            'image_version': '6.0(1) [build 6.0(0.66)]',
                            'status': 'ok'}
                        }
                    },
                'new_module':
                    {'10':
                        {'new_key': 'no',
                         'unknown_key': 'yes'}}
                }

        return result

class ShowRawData(MetaParser):
    def cli(self, **kwargs):
        self.device.execute('some command')
        return {'a': 'b'}
