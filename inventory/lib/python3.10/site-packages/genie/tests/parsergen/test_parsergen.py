#!/bin/env python

import os
import sys
import shlex
import inspect
import unittest

from textwrap import dedent
import subprocess

python3 = sys.version_info >= (3,0)

if python3:
    from unittest.mock import Mock
    from unittest.mock import patch
else:
    from mock import Mock
    from mock import patch

ats_mock = Mock()
with patch.dict('sys.modules',
        {'pyats' : ats_mock}, autospec=True):
    from genie import parsergen
    from genie.parsergen import oper_fill
    from genie.parsergen import oper_check
    from genie.parsergen import oper_fill_tabular
    from genie.tests.parsergen.scripts import parsergen_demo_mkpg


class TestNonTabularParser(unittest.TestCase):

    def setUp(self):
        self.showCommandOutput1  = '''\
        show interface MgmtEth0/0/CPU0/0
        Wed Mar 11 18:19:28.909 EDT
        MgmtEth0/0/CPU0/0 is up, line protocol is up 
          Interface state transitions: 1
          Hardware is Management Ethernet, address is 5254.00d6.36c9 (bia 5254.00d6.36c9)
          Internet address is 10.30.108.132/23
          MTU 1514 bytes, BW 0 Kbit
             reliability 255/255, txload Unknown, rxload Unknown
          Encapsulation ARPA,
          Duplex unknown, 0Kb/s, unknown, link type is autonegotiation
          output flow control is off, input flow control is off
          Carrier delay (up) is 10 msec
          loopback not set,
          ARP type ARPA, ARP timeout 04:00:00
          Last input 00:00:00, output 00:00:36
          Last clearing of "show interface" counters never
          5 minute input rate 84000 bits/sec, 33 packets/sec
          5 minute output rate 0 bits/sec, 0 packets/sec
             17890219 packets input, 5613119704 bytes, 0 total input drops
             0 drops for unrecognized upper-level protocol
             Received 16015275 broadcast packets, 1792005 multicast packets
                      0 runts, 0 giants, 0 throttles, 0 parity
             0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored, 0 abort
             15398 packets output, 1027241 bytes, 0 total output drops
             Output 4 broadcast packets, 0 multicast packets
             0 output errors, 0 underruns, 0 applique, 0 resets
             0 output buffer failures, 0 output buffers swapped out
             1 carrier transitions
        '''

        self.outputString1 = '''\
            Interface Gi0/0/0/0:
              Policy (internal, version=0, size=40)
                ether_if_type: PHY
                interface_ready: 1
                is_l2: 0
                not provisioned
                l2pt: off
                mac_addr: 02fe:08cb:26c5
                trunk.native_vlan: 0
                trunk.native_is_svlan: 0
                trunk.qinq_tunneling_etype: 0x8100
                trunk.mac_acc_ingress: 0
                trunk.mac_acc_egress: 0
                trunk.filter_dot1q: 0
                trunk.filter_dot1ad: 0
                trunk.filter_mac_relay: 0
              Unicast MAC Addresses: 0
        '''

        self.outputString2='''\
            Interface Gi0/0/0/0.0:
              Policy (internal, version=0, size=60)
                ether_if_type: PHY_L3_SUB
                interface_ready: 1
                is_l2: 0
                sub.parent: 0x00000100
                sub.admin_up: 0
                EFP MATCH: (none)
                EFP REWRITE: (none)
              Unicast MAC Addresses: 0
        '''


        self.outputDict1= {
             'show.intf.abort': '0',
             'show.intf.admin_state': 'up',
             'show.intf.arp_timeout': '04:00:00',
             'show.intf.broadcasts': '16015275',
             'show.intf.bw': '0',
             'show.intf.carrier_delay_up': '10',
             'show.intf.carrier_trans': '1',
             'show.intf.crc': '0',
             'show.intf.drops_unrec_upper_level_proto': '0',
             'show.intf.encap': 'ARPA',
             'show.intf.frame': '0',
             'show.intf.giants': '0',
             'show.intf.hardware': 'Management Ethernet',
             'show.intf.if_name': 'MgmtEth0/0/CPU0/0',
             'show.intf.ignored': '0',
             'show.intf.input_bytes': '5613119704',
             'show.intf.input_errors': '0',
             'show.intf.input_flowcontrol': 'off',
             'show.intf.input_pkts': '17890219',
             'show.intf.input_rate': '33',
             'show.intf.input_rate_bits': '84000',
             'show.intf.input_total_drops': '0',
             'show.intf.intf_trans': '1',
             'show.intf.ip_address': '10.30.108.132',
             'show.intf.last_clear_counter': 'never',
             'show.intf.last_input': '00:00:00',
             'show.intf.last_output': '00:00:36',
             'show.intf.line_protocol': 'up',
             'show.intf.link_type': 'autonegotiation',
             'show.intf.loopback_status': 'not set',
             'show.intf.mac_address': '5254.00d6.36c9',
             'show.intf.mtu': '1514',
             'show.intf.multicasts': '1792005',
             'show.intf.output_applique': '0',
             'show.intf.output_broadcast': '4',
             'show.intf.output_buf_failures': '0',
             'show.intf.output_buf_swapped': '0',
             'show.intf.output_bytes': '1027241',
             'show.intf.output_errors': '0',
             'show.intf.output_flowcontrol': 'off',
             'show.intf.output_multicast': '0',
             'show.intf.output_pkts': '15398',
             'show.intf.output_rate': '0',
             'show.intf.output_rate_bits': '0',
             'show.intf.output_resets': '0',
             'show.intf.output_total_drops': '0',
             'show.intf.output_underruns': '0',
             'show.intf.overrun': '0',
             'show.intf.parity': '0',
             'show.intf.runts': '0',
             'show.intf.throttles': '0'
        }

        self.outputDict2={
             'show.intf.admin_state': 'up',
             'show.intf.if_name': 'MgmtEth0/0/CPU0/0',
             'show.intf.ip_address': '10.30.108.132',
             'show.intf.line_protocol': 'up',
             'show.intf.mtu': '1514'
        }

        self.outputDict3={
             'show.ethdrvr.ether_if_type': 'PHY',
             'show.ethdrvr.if_name': 'Gi0/0/0/0',
             'show.ethdrvr.if_ready': '1',
             'show.ethdrvr.is_l2': '0',
             'show.ethdrvr.l2pt': 'off',
             'show.ethdrvr.mac_addr': '02fe:08cb:26c5',
             'show.ethdrvr.policy_size': '40',
             'show.ethdrvr.provisioned': 'not',
             'show.ethdrvr.trunk.filter_dot1ad': '0',
             'show.ethdrvr.trunk.filter_dot1q': '0',
             'show.ethdrvr.trunk.filter_mac_relay': '0',
             'show.ethdrvr.trunk.mac_acc_egress': '0',
             'show.ethdrvr.trunk.mac_acc_ingress': '0',
             'show.ethdrvr.trunk.native_is_svlan': '0',
             'show.ethdrvr.trunk.native_vlan': '0',
             'show.ethdrvr.trunk.qinq_tunneling_etype': '0x8100',
             'show.ethdrvr.unicast_mac_addr': '0'
        }



        self.outputDict4={
             'show.ethdrvr.ether_if_type': 'PHY_L3_SUB',
             'show.ethdrvr.if_name': 'Gi0/0/0/0.0',
             'show.ethdrvr.if_ready': '1',
             'show.ethdrvr.is_l2': '0',
             'show.ethdrvr.policy_size': '60',
             'show.ethdrvr.sub.admin_up': '0',
             'show.ethdrvr.sub.efp_match': '(none)',
             'show.ethdrvr.sub.efp_rewrite': '(none)',
             'show.ethdrvr.sub.parent': '0x00000100',
             'show.ethdrvr.unicast_mac_addr': '0'
        }



    def test_non_tabular_parser_1(self):
        self.maxDiff = None

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput1),
                'os':'iosxr'}
        dev1 = Mock(**device_kwargs)
        dev1.name='router1'

        attrValPairsToParse = [
            ('show.intf.if_name',                       'MgmtEth0/0/CPU0/0'),
        ]

        # Mock the call to determine the device's platform type
        ats_mock.tcl.eval.return_value = 'iosxr'

        #
        # Parse all tags matching a pattern
        #
        pgfill = oper_fill (
            dev1,
            ('show_interface_<WORD>', [], {'ifname':'MgmtEth0/0/CPU0/0'}),
            attrValPairsToParse,
            refresh_cache=True, regex_tag_fill_pattern='show\.intf')
        result = pgfill.parse()
        self.assertTrue(result, msg='Parse did not pass as expected.')
        self.assertEqual(parsergen.ext_dictio[dev1.name], self.outputDict1)

        args, kwargs = dev1.execute.call_args
        self.assertTrue('show interface MgmtEth0/0/CPU0/0' in args)


    def test_non_tabular_parser_2(self):
        ''' Parse and compare against selected tags.
        '''
        self.maxDiff = None

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput1),
                'os':'iosxr'}
        dev1 = Mock(**device_kwargs)
        dev1.name='router1'

        attrValPairsToCheck = [
            ('show.intf.if_name',                       'MgmtEth0/0/CPU0/0'),
            ('show.intf.line_protocol',                 'up'),
            ('show.intf.ip_address',                    '10.30.108.132'),
            ('show.intf.mtu',                           1514),
            ('show.intf.admin_state',                   'up'),
        ]

        # Clear our the mock device's call_args.
        dev1.execute.reset_mock()

        pgcheck = oper_check (
            dev1,
            ('show_interface_<WORD>', [], {'ifname':'MgmtEth0/0/CPU0/0'}),
            attrValPairsToCheck,
            refresh_cache=True)
        result = pgcheck.parse()
        self.assertTrue(result)
        self.assertEqual(parsergen.ext_dictio[dev1.name], self.outputDict2)

        args, kwargs = dev1.execute.call_args
        self.assertTrue('show interface MgmtEth0/0/CPU0/0' in args)


    def test_non_tabular_parser_3(self):
        ''' Test negation mode.
        '''
        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput1),
                'os':'iosxr'}
        dev1 = Mock(**device_kwargs)
        dev1.name='router1'

        attrValPairsToCheck = [
            ('show.intf.if_name',                       'MgmtEth0/0/CPU0/0'),
            ('show.intf.line_protocol',                 'up'),
            ('show.intf.ip_address',                    '10.30.108.132'),
            ('show.intf.mtu',                           1514),
            ('show.intf.admin_state',                   'up'),
        ]


        # Clear our the mock device's call_args.
        dev1.execute.reset_mock()

        pgcheck = oper_check (
            dev1,
            ('show_interface_<WORD>', [], {'ifname':'MgmtEth0/0/CPU0/0'}),
            attrValPairsToCheck,
            refresh_cache=True, negate=True)
        result = pgcheck.parse()
        self.assertFalse(result)
        self.assertEqual(parsergen.ext_dictio[dev1.name], self.outputDict2)

        args, kwargs = dev1.execute.call_args
        self.assertTrue('show interface MgmtEth0/0/CPU0/0' in args)


    def test_non_tabular_parser_4(self):
        ''' Parse and compare against selected tags, mix up the order
        '''
        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput1),
                'os':'iosxr'}
        dev1 = Mock(**device_kwargs)
        dev1.name='router1'

        attrValPairsToCheck = [
            ('show.intf.line_protocol',                 'up'),
            ('show.intf.mtu',                           1514),
            ('show.intf.ip_address',                    '10.30.108.132'),
            ('show.intf.admin_state',                   'up'),
            ('show.intf.if_name',                       'MgmtEth0/0/CPU0/0'),
        ]

        # Clear our the mock device's call_args.
        dev1.execute.reset_mock()

        pgcheck = oper_check (
            dev1,
            ('show_interface_<WORD>', [], {'ifname':'MgmtEth0/0/CPU0/0'}),
            attrValPairsToCheck,
            refresh_cache=True)
        result = pgcheck.parse()
        self.assertTrue(result)
        self.assertEqual(parsergen.ext_dictio[dev1.name], self.outputDict2)

        args, kwargs = dev1.execute.call_args
        self.assertTrue('show interface MgmtEth0/0/CPU0/0' in args)


    def test_non_tabular_parser_5(self):
        ''' Parse and compare against selected tags, mix up the order
        '''
        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput1),
                'os':'iosxr'}
        dev1 = Mock(**device_kwargs)
        dev1.name='router1'


        #
        # Parse and compare against selected tags, but don't run the
        # show command again against the router.
        #
        attrValPairsToCheck = [
            ('show.intf.line_protocol',                 'up'),
            ('show.intf.mtu',                           1514),
            ('show.intf.ip_address',                    '10.30.108.132'),
            ('show.intf.admin_state',                   'up'),
            ('show.intf.if_name',                       'MgmtEth0/0/CPU0/0'),
        ]

        # Clear our the mock device's call_args.
        dev1.execute.reset_mock()

        pgcheck = oper_check (
            dev1,
            ('show_interface_<WORD>', [], {'ifname':'MgmtEth0/0/CPU0/0'}),
            attrValPairsToCheck,
            refresh_cache=False)
        result = pgcheck.parse()
        self.assertTrue(result, msg='Parse did not pass as expected.')
        self.assertEqual(parsergen.ext_dictio[dev1.name], self.outputDict2)

        self.assertEqual(dev1.execute.call_args, None)


    def test_non_tabular_parser_6(self):
        ''' Parse and compare against selected tags, but introduce a bogus
            regex tag.
        '''
        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput1),
                'os':'iosxr'}
        dev1 = Mock(**device_kwargs)
        dev1.name='router1'

        attrValPairsToCheck = [
            ('show.intf.line_protocol',                 'up'),
            ('show.intf.mtu',                           1514),
            ('show.intf.ip_address',                    '10.30.108.132'),
            ('show.intf.admin_state',                   'up'),
            ('show.intf.if_name',                       'MgmtEth0/0/CPU0/0'),
            ('my.bogus.regex.tag',                      'bogus value'),
        ]

        # Clear our the mock device's call_args.
        dev1.execute.reset_mock()

        pgcheck = oper_check (
            dev1,
            ('show_interface_<WORD>', [], {'ifname':'MgmtEth0/0/CPU0/0'}),
            attrValPairsToCheck,
            refresh_cache=False)
        result = pgcheck.parse()
        self.assertFalse(result, msg='Parse did not fail as expected.')
        self.assertEqual(parsergen.ext_dictio[dev1.name], self.outputDict2)

        self.assertEqual(dev1.execute.call_args, None)


    def test_non_tabular_parser_7(self):
        ''' Parse and compare against selected tags, but force the comparison
            to fail.
        '''
        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput1),
                'os':'iosxr'}
        dev1 = Mock(**device_kwargs)
        dev1.name='router1'


        attrValPairsToCheck = [
            ('show.intf.line_protocol',                 'up'),
            ('show.intf.mtu',                           1514),
            ('show.intf.ip_address',                    '10.30.108.132'),
            ('show.intf.admin_state',                   'down'),
            ('show.intf.if_name',                       'MgmtEth0/0/CPU0/0'),
        ]

        # Clear our the mock device's call_args.
        dev1.execute.reset_mock()

        pgcheck = oper_check (
            dev1,
            ('show_interface_<WORD>', [], {'ifname':'MgmtEth0/0/CPU0/0'}),
            attrValPairsToCheck,
            refresh_cache=False)
        result = pgcheck.parse()
        self.assertFalse(result, msg='Parse did not fail as expected.')
        self.assertTrue(
          "Attribute show.intf.admin_state has value 'up' (expected 'down')"
          in str(pgcheck),
          msg='Parser did not report mismatched value as expected')


    def test_non_tabular_parser_8(self):
        ''' Parse and compare against selected tags, don't run the
            show command again against the router, but change the router's
            name (this will force the show command to be run but will generate
            a warning).
        '''
        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput1),
                'os':'iosxr'}
        dev1 = Mock(**device_kwargs)

        attrValPairsToCheck = [
            ('show.intf.line_protocol',                 'up'),
            ('show.intf.mtu',                           1514),
            ('show.intf.ip_address',                    '10.30.108.132'),
            ('show.intf.admin_state',                   'up'),
            ('show.intf.if_name',                       'MgmtEth0/0/CPU0/0'),
        ]

        # Clear our the mock device's call_args.
        dev1.execute.reset_mock()
        dev1.name='router2'

        pgcheck = oper_check (
            dev1,
            ('show_interface_<WORD>', [], {'ifname':'MgmtEth0/0/CPU0/0'}),
            attrValPairsToCheck,
            refresh_cache=False)
        result = pgcheck.parse()
        self.assertTrue(result, msg='Parse did not pass as expected.')
        self.assertEqual(parsergen.ext_dictio[dev1.name], self.outputDict2)

        args, kwargs = dev1.execute.call_args
        self.assertTrue('show interface MgmtEth0/0/CPU0/0' in args)


    def test_non_tabular_parser_9(self):
        ''' Parse output (variant 1) that contains optional regex tags.
        '''
        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput1),
                'os':'iosxr'}
        dev1 = Mock(**device_kwargs)
        dev1.execute.reset_mock()
        dev1.name='router5'

        attrValPairsToParse = [
            ('show.ethdrvr.if_name',   'Gi0/0/0/0'),
        ]

        dev1.execute.return_value = dedent(self.outputString1)
        pgfill = oper_fill (
            dev1,
            ('show_eth_driver_interface_<WORD>', [], {'ifname':'Gi0/0/0/0'}),
            attrValPairsToParse,
            refresh_cache=True, regex_tag_fill_pattern='show\.ethdrvr',
            skip=True)
        result = pgfill.parse()
        self.assertTrue(result, msg='Parse did not pass as expected.')
        self.assertEqual(parsergen.ext_dictio[dev1.name], self.outputDict3)

        args, kwargs = dev1.execute.call_args
        self.assertTrue('show eth-drvr interface Gi0/0/0/0' in args)



    def test_non_tabular_parser_10(self):
        ''' Parse output (variant 2) that contains optional regex tags.
        '''
        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput1),
                'os':'iosxr'}
        dev1 = Mock(**device_kwargs)
        dev1.name='router1'



        dev1.execute.reset_mock()

        attrValPairsToParse = [
            ('show.ethdrvr.if_name',   'Gi0/0/0/0.0'),
        ]

        dev1.execute.return_value = dedent(self.outputString2)
        pgfill = oper_fill (
            dev1,
            ('show_eth_driver_interface_<WORD>', [], {'ifname':'Gi0/0/0/0.0'}),
            attrValPairsToParse,
            refresh_cache=True, regex_tag_fill_pattern='show\.ethdrvr',
            skip=True)
        result = pgfill.parse()
        self.assertTrue(result, msg='Parse did not pass as expected.')
        self.assertEqual(parsergen.ext_dictio[dev1.name], self.outputDict4)

        args, kwargs = dev1.execute.call_args
        self.assertTrue('show eth-drvr interface Gi0/0/0/0.0' in args)



    def test_non_tabular_parser_11(self):
        ''' Now validate that if we run the previous parse in non-skip mode
            the parse succeeds (because some of the tags were matched) but the
            outputs do not match (because the parser gave up on the first
            tag for which no match could be found).
        '''
        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput1),
                'os':'iosxr'}
        dev1 = Mock(**device_kwargs)
        dev1.name='router1'

        dev1.execute.reset_mock()

        attrValPairsToParse = [
            ('show.ethdrvr.if_name',   'Gi0/0/0/0.0'),
        ]

        dev1.execute.return_value = dedent(self.outputString2)
        pgfill = oper_fill (
            dev1,
            ('show_eth_driver_interface_<WORD>', [], {'ifname':'Gi0/0/0/0.0'}),
            attrValPairsToParse,
            refresh_cache=True, regex_tag_fill_pattern='show\.ethdrvr',
            skip=False)
        result = pgfill.parse()
        self.assertTrue(result, msg='Parse did not pass as expected.')
        self.assertNotEqual(parsergen.ext_dictio[dev1.name], self.outputDict4)


    def test_non_tabular_parser_12(self):
        ''' Parse and compare against selected tags, mix up the order.
            Test oper_fill mode.
        '''
        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput1),
                'os':'iosxr'}
        dev1 = Mock(**device_kwargs)
        dev1.name='router1'


        #
        # Parse and compare against selected tags, but don't run the
        # show command again against the router.
        #
        attrValPairsToCheck = [
            ('show.intf.if_name',                       'MgmtEth0/0/CPU0/0'),
            ('show.intf.mtu',                           None),
            ('show.intf.line_protocol',                 None),
            ('show.intf.admin_state',                   None),
            ('show.intf.ip_address',                    None),
        ]

        # Clear our the mock device's call_args.
        dev1.execute.reset_mock()

        pgcheck = oper_fill (
            dev1,
            ('show_interface_<WORD>', [], {'ifname':'MgmtEth0/0/CPU0/0'}),
            attrValPairsToCheck,
            refresh_cache=True)
        result = pgcheck.parse()
        self.assertTrue(result, msg='Parse did not pass as expected.')
        self.assertEqual(parsergen.ext_dictio[dev1.name], self.outputDict2)

        args, kwargs = dev1.execute.call_args
        self.assertTrue('show interface MgmtEth0/0/CPU0/0' in args)


    def test_non_tabular_parser_13(self):
        """ Test support for unicon integration """
        self.maxDiff = None

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput1)}
        dev1 = Mock(**device_kwargs)
        dev1.name='router1'

        # Simulate a unicon connection, which does not have a Csccon handle.
        del dev1.handle

        attrValPairsToParse = [
            ('show.intf.if_name',                       'MgmtEth0/0/CPU0/0'),
        ]

        # Mock the call to determine the device's platform type
        dev1.os = 'iosxr'

        #
        # Parse all tags matching a pattern
        #
        pgfill = oper_fill (
            dev1,
            ('show_interface_<WORD>', [], {'ifname':'MgmtEth0/0/CPU0/0'}),
            attrValPairsToParse,
            refresh_cache=True, regex_tag_fill_pattern='show\.intf')
        result = pgfill.parse()
        self.assertTrue(result, msg='Parse did not pass as expected.')
        self.assertEqual(parsergen.ext_dictio[dev1.name], self.outputDict1)

        args, kwargs = dev1.execute.call_args
        self.assertTrue('show interface MgmtEth0/0/CPU0/0' in args)


    def test_non_tabular_parser_14(self):
        """ Test sunny-day Csccon scenario when conn alias requested by user """
        self.maxDiff = None

        # Define how device stub will behave when accessed by production parser.
        dev1 = Mock()
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput1)}
        dev1.myalias = Mock(**device_kwargs)
        dev1.name='router1'

        attrValPairsToParse = [
            ('show.intf.if_name',                       'MgmtEth0/0/CPU0/0'),
        ]

        # Mock the call to determine the device's platform type
        dev1.os = 'iosxr'

        #
        # Parse all tags matching a pattern
        #
        pgfill = oper_fill (
            device=dev1,
            device_conn_alias='myalias',
            show_command=\
                ('show_interface_<WORD>', [], {'ifname':'MgmtEth0/0/CPU0/0'}),
            attrvalpairs=attrValPairsToParse,
            refresh_cache=True, regex_tag_fill_pattern='show\.intf')
        result = pgfill.parse()
        self.assertTrue(result, msg='Parse did not pass as expected.')
        self.assertEqual(parsergen.ext_dictio[dev1.name], self.outputDict1)

        args, kwargs = dev1.myalias.execute.call_args
        self.assertTrue('show interface MgmtEth0/0/CPU0/0' in args)


    def test_non_tabular_parser_15(self):
        """ Test unicon integration with user-requested connection alias"""
        self.maxDiff = None

        # Define how device stub will behave when accessed by production parser.
        dev1 = Mock()
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput1)}
        dev1.myalias = Mock(**device_kwargs)
        dev1.name='router1'

        # Simulate a unicon connection, which does not have a Csccon handle.
        del dev1.handle

        attrValPairsToParse = [
            ('show.intf.if_name',                       'MgmtEth0/0/CPU0/0'),
        ]

        # Mock the call to determine the device's platform type
        dev1.os = 'iosxr'

        #
        # Parse all tags matching a pattern
        #
        pgfill = oper_fill (
            device = dev1,
            device_conn_alias = 'myalias',
            show_command = \
                ('show_interface_<WORD>', [], {'ifname':'MgmtEth0/0/CPU0/0'}),
            attrvalpairs = attrValPairsToParse,
            refresh_cache=True, regex_tag_fill_pattern='show\.intf')
        result = pgfill.parse()
        self.assertTrue(result, msg='Parse did not pass as expected.')
        self.assertEqual(parsergen.ext_dictio[dev1.name], self.outputDict1)

        args, kwargs = dev1.myalias.execute.call_args
        self.assertTrue('show interface MgmtEth0/0/CPU0/0' in args)

    def test_non_tabular_parser_16(self):

        """
            Test non tabular parser when passing a device output
            and device os only.
        """

        pure_cli = dedent(self.showCommandOutput1)

        attrValPairsToParse = [
            ('show.intf.if_name',                       'MgmtEth0/0/CPU0/0'),
        ]

        device_os = 'iosxr'

        pgfill = oper_fill (
                            show_command = ('show_interface_<WORD>', [], {'ifname':'MgmtEth0/0/CPU0/0'}),
                            attrvalpairs = attrValPairsToParse,
                            refresh_cache=False,
                            regex_tag_fill_pattern='show\.intf',
                            device_output = pure_cli,
                            device_os = device_os)

        result = pgfill.parse()
        self.assertEqual(parsergen.ext_dictio['device_name'], self.outputDict1)

    def test_non_tabular_parser_17(self):

        """
            Test non tabular parser when passing a device output
            and device os only and compare against selected tags.
        """

        pure_cli = dedent(self.showCommandOutput1)

        attrValPairsToCheck = [
            ('show.intf.if_name',                       'MgmtEth0/0/CPU0/0'),
            ('show.intf.line_protocol',                 'up'),
            ('show.intf.ip_address',                    '10.30.108.132'),
            ('show.intf.mtu',                           1514),
            ('show.intf.admin_state',                   'up'),
        ]

        device_os = 'iosxr'

        pgcheck = oper_check (
                    attrvalpairs = attrValPairsToCheck,
                    show_command = \
                        ('show_interface_<WORD>', [], {'ifname':'MgmtEth0/0/CPU0/0'}),
                    refresh_cache=True,
                    device_output = pure_cli,
                    device_os = device_os)

        result = pgcheck.parse()
        self.assertTrue(result)
        self.assertEqual(parsergen.ext_dictio['device_name'], self.outputDict2)


class TestTabularParser(unittest.TestCase):

    def setUp(self):
        self.showCommandOutput1='''
            RP/0/0/CPU0:iox#show isis database
            Wed Dec 16 09:48:55.017 EST

            IS-IS ring (Level-1) Link State Database
            LSPID                 LSP Seq Num  LSP Checksum  LSP Holdtime  ATT/P/OL
            iox.00-00           * 0x00000008   0xf9fd        1003            0/0/0
            ioxbfd.00-00          0x00000004   0x8f36        862             0/0/0

            Total Level-1 LSP count: 4     Local Level-1 LSP count: 1

            IS-IS ring (Level-2) Link State Database
            LSPID                 LSP Seq Num  LSP Checksum  LSP Holdtime  ATT/P/OL
            iox.00-00           * 0x00000009   0x351a        1003            0/0/0
            iox.01-00             0x00000002   0x0ead        922             0/0/0

            Total Level-2 LSP count: 4     Local Level-2 LSP count: 1
            '''

        self.showCommandOutput2='''
            show arp

            Thu Mar 12 16:48:09.689 EDT

            -------------------------------------------------------------------------------
            0/0/CPU0
            -------------------------------------------------------------------------------
            Address         Age        Hardware Addr   State      Type  Interface
            10.30.97.64     00:33:09   0050.568e.6227  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            10.30.97.68     00:00:00   0050.568e.3711  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            10.30.108.1     01:26:25   0007.b400.6c01  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            10.30.108.2     00:00:27   18ef.63e6.a841  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            10.30.108.3     00:01:36   18ef.63e6.9bc1  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            10.30.108.4     00:27:43   0050.568e.0e98  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            10.30.108.95    00:06:17   5254.0053.ff84  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            10.30.108.96    02:49:00   5254.00a2.e74f  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            10.30.108.97    03:00:30   5254.0072.3362  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            10.30.108.98    03:46:02   5254.00bb.61f0  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            10.30.108.115   01:38:01   5254.00eb.87cf  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            10.30.108.132   -          5254.00d6.36c9  Interface  ARPA  MgmtEth0/0/CPU0/0
            10.30.108.241   01:47:43   5254.0045.f1b4  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            10.30.109.93    00:00:34   5254.0094.c1fe  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            10.30.109.94    02:58:23   5254.0045.ae0f  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            10.30.109.96    -          5254.00f7.b674  Probe      ARPA  MgmtEth0/0/CPU0/0
            10.30.109.114   01:41:44   5254.0008.0373  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            10.30.109.131   02:08:28   5254.00df.80f5  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            10.30.109.132   01:35:21   5254.0060.6195  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            10.30.109.239   01:46:50   5254.007f.b191  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            10.30.109.240   00:27:43   5254.00e3.308d  Dynamic    ARPA  MgmtEth0/0/CPU0/0
            RP/0/0/CPU0:VM-2#
            '''

        self.showCommandOutput3='''
            show arp

            Thu Mar 12 16:48:09.689 EDT

            -------------------------------------------------------------------------------
            0/0/CPU0
            -------------------------------------------------------------------------------
            Address       |  Age       | Hardware Addr  | State    |  Type | Interface
            10.30.97.64   |  00:33:09  | 0050.568e.6227 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.97.68   |  00:00:00  | 0050.568e.3711 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.1   |  01:26:25  | 0007.b400.6c01 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.2   |  00:00:27  | 18ef.63e6.a841 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.3   |  00:01:36  | 18ef.63e6.9bc1 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.4   |  00:27:43  | 0050.568e.0e98 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.95  |  00:06:17  | 5254.0053.ff84 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.96  |  02:49:00  | 5254.00a2.e74f | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.97  |  03:00:30  | 5254.0072.3362 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.98  |  03:46:02  | 5254.00bb.61f0 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.115 |  01:38:01  | 5254.00eb.87cf | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.132 |  -         | 5254.00d6.36c9 | Interface|  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.241 |  01:47:43  | 5254.0045.f1b4 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.109.93  |  00:00:34  | 5254.0094.c1fe | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.109.94  |  02:58:23  | 5254.0045.ae0f | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.109.96  |  -         | 5254.00f7.b674 | Probe    |  ARPA | MgmtEth0/0/CPU0/0
            10.30.109.114 |  01:41:44  | 5254.0008.0373 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.109.131 |  02:08:28  | 5254.00df.80f5 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.109.132 |  01:35:21  | 5254.0060.6195 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.109.239 |  01:46:50  | 5254.007f.b191 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.109.240 |  00:27:43  | 5254.00e3.308d | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            RP/0/0/CPU0:VM-2#
            '''

        self.showCommandOutput4='''
            show arp

            Thu Mar 12 16:48:09.689 EDT

            -------------------------------------------------------------------------------
            0/0/CPU0
            -------------------------------------------------------------------------------
            Address         Age        Hardware Addr   State      Type  Interface
            10.30.97.64   |  00:33:09  | 0050.568e.6227 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.97.68   |  00:00:00  | 0050.568e.3711 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.1   |  01:26:25  | 0007.b400.6c01 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.2   |  00:00:27  | 18ef.63e6.a841 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.3   |  00:01:36  | 18ef.63e6.9bc1 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.4   |  00:27:43  | 0050.568e.0e98 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.95  |  00:06:17  | 5254.0053.ff84 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.96  |  02:49:00  | 5254.00a2.e74f | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.97  |  03:00:30  | 5254.0072.3362 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.98  |  03:46:02  | 5254.00bb.61f0 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.115 |  01:38:01  | 5254.00eb.87cf | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.132 |  -         | 5254.00d6.36c9 | Interface|  ARPA | MgmtEth0/0/CPU0/0
            10.30.108.241 |  01:47:43  | 5254.0045.f1b4 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.109.93  |  00:00:34  | 5254.0094.c1fe | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.109.94  |  02:58:23  | 5254.0045.ae0f | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.109.96  |  -         | 5254.00f7.b674 | Probe    |  ARPA | MgmtEth0/0/CPU0/0
            10.30.109.114 |  01:41:44  | 5254.0008.0373 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.109.131 |  02:08:28  | 5254.00df.80f5 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.109.132 |  01:35:21  | 5254.0060.6195 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.109.239 |  01:46:50  | 5254.007f.b191 | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            10.30.109.240 |  00:27:43  | 5254.00e3.308d | Dynamic  |  ARPA | MgmtEth0/0/CPU0/0
            RP/0/0/CPU0:VM-2#
            '''

        self.showCommandOutput5='''
            +-----------------------------------------------------------------------------------+
            |Asic inst. |card |HP |Asic |Asic   |Admin |plane |Fgid |Asic State |DC|Last  |PON |HR |
            |(R/S/A)    |pwrd |   |type |class  |/Oper |/grp  |DL   |           |  |init  |(#) |(#)|
            +-----------------------------------------------------------------------------------+
            |0/FC0/0    |UP   |1  |s13  |FE1600 |UP/UP |0/0   |DONE |NRML       |0 |PON   |1   |0  |
            |0/FC0/1    |UP   |1  |s13  |FE1600 |UP/UP |0/1   |DONE |NRML       |0 |PON   |1   |0  |
            |0/FC0/2    |UP   |1  |s13  |FE1600 |UP/UP |0/2   |DONE |NRML       |0 |PON   |1   |0  |
            |0/FC0/3    |UP   |1  |s13  |FE1600 |UP/UP |0/3   |DONE |NRML       |0 |PON   |1   |0  |
            +-----------------------------------------------------------------------------------+
            '''

        self.showCommandOutput6='''
            +-----------------------------------------------------------------------------------+
            | Asic inst.|card|HP|Asic| Asic  | Admin|plane| Fgid| Asic State |DC| Last  |PON|HR |
            |  (R/S/A)  |pwrd|  |type| class | /Oper|/grp | DL  |            |  | init  |(#)|(#)|
            +-----------------------------------------------------------------------------------+
            | 0/FC0/0   | UP | 1| s13|  FE1600| UP/UP| 0/0 | DONE| NRML       | 0| PON   |  1|  0|
            | 0/FC0/1   | UP | 1| s13|  FE1600| UP/UP| 0/1 | DONE| NRML       | 0| PON   |  1|  0|
            | 0/FC0/2   | UP | 1| s13|  FE1600| UP/UP| 0/2 | DONE| NRML       | 0| PON   |  1|  0|
            | 0/FC0/3   | UP | 1| s13|  FE1600| UP/UP| 0/3 | DONE| NRML       | 0| PON   |  1|  0|
            +-----------------------------------------------------------------------------------+
            '''

        self.showCommandOutput7='''
            +-----------------------------------------------------------------------------------+
            | Asic inst.|card|HP|Asic| Asic  | Admin|plane| Fgid| Asic State |DC| Last  |PON|HR |
            |  (R/S/A)  |pwrd|  |type| class | /Oper|/grp | DL  |            |  | init  |(#)|(#)|
            +-----------------------------------------------------------------------------------+
            |   0/FC0/0     | UP    | 1| s13|  FE1600| UP/UP| 0/0 | DONE| NRML       | 0| PON   |  1|  0|
            |  0/FC0/1   | UP  | 1| s13|  FE1600|  UP/UP| 0/1 | DONE| NRML       | 0| PON   |  1|  0|
            |    0/FC0/2    | UP | 1| s13|  FE1600| UP/UP| 0/2 | DONE| NRML       | 0| PON   |  1|  0|
            | 0/FC0/3   | UP   | 1| s13|  FE1600| UP/UP| 0/3 | DONE| NRML       | 0| PON   |  1|  0|
            +-----------------------------------------------------------------------------------+
            '''

        self.showCommandOutput8='''
            admin show controller ccc bootflash info location F0/FC0
            Sun Apr 23 21:58:35.328 PDT

            CCC Bootflash information for: F0/FC0
              HW Info:
                  Manufacturer ID: Micron (0x20)
                  Device Size    : 16 MB

              Programmed Content:
                                                                          Secure
                                                                 Size     Boot
                     Image Name          Version   Build Date   (bytes)   Enabled   Note
              ========================  =========  ==========  =========  =======  ======
              CCC Power-On                1.39     11/21/2014     11789     N/A    Active
              CCC FPGA                    1.28.0   12/24/2014   2453207     N/A    Active
              Secure Boot Certificates    1.00     06/13/2013      1047     N/A
              CCC FPGA (Backup)           1.23.0   02/26/2014   2453207     N/A
              CCC Power-On (Backup)       1.32     02/14/2014      9048     N/A
            '''

        self.showCommandOutput9='''
            Cards OIR History of rack: 0

            OIR Events as seen by Master (0/RP1)-
              DATE   TIME (UTC)     EVENT        LOC     CARD TYPE            SERIAL NO
              -----  ------------   ----------   -----   ------------------   -----------
              04/22  02:27:57.002   INSERTED     0/7     NC6-10X100G-M-K      SAL1929K8RJ
              04/22  02:22:17.765   REMOVED      0/7     NC6-20X100GE-M-C     SAL211004A5
              04/22  00:45:54.471   DISCOVERED   0/RP0   NC6-RP               SAL1923GBM1
              04/22  00:45:54.426   DISCOVERED   0/FC5   NC6-FC2-U            SAL210304H4
              04/22  00:45:54.331   DISCOVERED   0/FC4   NC6-FC2-U            SAL210304GG
            '''

        self.showCommandOutput10='''
            Cards OIR History of rack: 0

            OIR Events as seen by Master (0/RP1)-
              DATE   TIME (PDT)     EVENT        LOC     CARD TYPE            SERIAL NO
              -----  ------------   ----------   -----   ------------------   -----------
              04/22  02:27:57.002   INSERTED     0/7     NC6-10X100G-M-K      SAL1929K8RJ
              04/22  02:22:17.765   REMOVED      0/7     NC6-20X100GE-M-C     SAL211004A5
              04/22  00:45:54.471   DISCOVERED   0/RP0   NC6-RP               SAL1923GBM1
              04/22  00:45:54.426   DISCOVERED   0/FC5   NC6-FC2-U            SAL210304H4
              04/22  00:45:54.331   DISCOVERED   0/FC4   NC6-FC2-U            SAL210304GG
            '''

        self.showCommandOutput11='''
            +------------------------------------------------------------------------------+
            |  Channel |   Channel  |     Signal .     |Optical Power|     Optical Light   |
            |  Number. |   Status   |    Strength      |    Alarm    |         Input       |
            +------------------------------------------------------------------------------+
            | Rx Ch 0: | Enabled    | Signal Detected  |   off       | 0.95mW  -0.2182dBm  |
            | Rx Ch 1: | Enabled    | Signal Detected  |   off       | 1.09mW  0.3782dBm   |
            | Rx Ch 2: | Enabled    | Signal Detected  |   off       | 1.09mW  0.3822dBm   |
            | Rx Ch 3: | Enabled    | Signal Detected  |   off       | 1.07mW  0.2857dBm   |
            | Rx Ch 4: | Enabled    | Signal Detected  |   off       | 1.17mW  0.6819dBm   |
            | Rx Ch 5: | Enabled    | Signal Detected  |   off       | 1.25mW  0.9864dBm   |
            | Rx Ch 6: | Enabled    | Signal Detected  |   off       | 1.15mW  0.6070dBm   |
            | Rx Ch 7: | Enabled    | Signal Detected  |   off       | 1.09mW  0.3822dBm   |
            | Rx Ch 8: | Enabled    | Signal Detected  |   off       | 1.19mW  0.7518dBm   |
            | Rx Ch 9: | Enabled    | Signal Detected  |   off       | 1.15mW  0.6258dBm   |
            | Rx Ch 10:| Enabled    | Signal Detected  |   off       | 0.99mW  -0.0524dBm  |
            | Rx Ch 11:| Enabled    | Signal Detected  |   off       | 1.13mW  0.5346dBm   |
            +------------------------------------------------------------------------------+
            '''

        self.showCommandOutput12='''
            admin show environment temp location F0/FC0
            Sun Apr 23 22:22:48.044 PDT
            ================================================================================
            Location  TEMPERATURE                 Value   Crit Major Minor Minor Major  Crit
                      Sensor                    (deg C)   (Lo) (Lo)  (Lo)  (Hi)  (Hi)   (Hi)
            --------------------------------------------------------------------------------
            F0/FC0
                      Inlet                          34    -10    -5     0    55    65    75
                      HotSpot                        40    -10    -5     0    95   100   105
                      Outlet                         45    -10    -5     0    65    75    85
                      PCIe Die                       46    -10    -5     0   105   115   125
                      FE_0 Die                       46    -10    -5     0   105   115   120
                      FE_1 Die                       45    -10    -5     0   105   115   120
                      FE_2 Die                       49    -10    -5     0   105   115   120
            '''

        self.showCommandOutput13='''
            RP/0/RP0/CPU0:f10#show processes all
            Sun Apr 23 22:54:39.581 PDT
            JID    LAST STARTED            STATE    RE-     PLACE-  MANDA-  MAINT- NAME(IID) ARGS
                                                    START   MENT    TORY    MODE
            -------------------------------------------------------------------------------
            118    04/14/2017 15:37:31.166 Run      1                      Y      devc-conaux-aux(1) -a -h -d librs232.dll -b -m libconaux.dll -a -u libslinux.dll -a -p /dev/hvc1
            117    04/14/2017 15:37:31.242 Run      1                      Y      devc-conaux-con(1) -c -h -d librs232.dll -b -m libconaux.dll -c -u libslinux.dll -c -p /dev/hvc0
            53     04/14/2017 15:37:30.517 Run      1               M      Y      dsr(1)
            119    04/14/2017 15:37:31.311 Run      1                      Y      shmwin_svr(1)
            212    04/14/2017 15:37:31.377 Run      1               M      Y      sdr_invmgr(1)
            '''

        self.showCommandOutput14='''
            sysadmin-vm:0_RP0# show environment power location F0/FC0
            Sun Apr  23 22:27:38.178 UTC-07:00

            ================================================================================
               Location     Card Type            Power       Power       Status
                                                 Allocated   Used
                                                 Watts       Watts
            ================================================================================
               F0/FC0       NCS-F-FC               440         291       ON
            '''

        self.showCommandOutput15='''
            show service state
            NAME       POWER   STATE     
            ==========================
            mini       on      deployed  
            mini2      on      deployed'''

        self.outputDict1={1: {'iox.00-00           *': {'ATT/P/OL': '0/0/0', 'LSP Holdtime': '1003', 'LSPID': 'iox.00-00           *', 'LSP Checksum': 63997, 'LSP Seq Num': 8}, 'ioxbfd.00-00': {'ATT/P/OL': '0/0/0', 'LSP Holdtime': '862', 'LSPID': 'ioxbfd.00-00', 'LSP Checksum': 36662, 'LSP Seq Num': 4}}, 2: {'iox.00-00           *': {'ATT/P/OL': '0/0/0', 'LSP Holdtime': '1003', 'LSPID': 'iox.00-00           *', 'LSP Checksum': 13594, 'LSP Seq Num': 9}, 'iox.01-00': {'ATT/P/OL': '0/0/0', 'LSP Holdtime': '922', 'LSPID': 'iox.01-00', 'LSP Checksum': 3757, 'LSP Seq Num': 2}}}
        self.outputDict2={'0/0/CPU0': {'10.30.108.1': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.1',
                                                    'Age': '01:26:25',
                                                    'Hardware Addr': '0007.b400.6c01',
                                                    'Interface': 'MgmtEth0/0/CPU0/0',
                                                    'State': 'Dynamic',
                                                    'Type': 'ARPA'}},
              '10.30.108.115': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.115',
                                                      'Age': '01:38:01',
                                                      'Hardware Addr': '5254.00eb.87cf',
                                                      'Interface': 'MgmtEth0/0/CPU0/0',
                                                      'State': 'Dynamic',
                                                      'Type': 'ARPA'}},
              '10.30.108.132': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.132',
                                                      'Age': '-',
                                                      'Hardware Addr': '5254.00d6.36c9',
                                                      'Interface': 'MgmtEth0/0/CPU0/0',
                                                      'State': 'Interface',
                                                      'Type': 'ARPA'}},
              '10.30.108.2': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.2',
                                                    'Age': '00:00:27',
                                                    'Hardware Addr': '18ef.63e6.a841',
                                                    'Interface': 'MgmtEth0/0/CPU0/0',
                                                    'State': 'Dynamic',
                                                    'Type': 'ARPA'}},
              '10.30.108.241': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.241',
                                                      'Age': '01:47:43',
                                                      'Hardware Addr': '5254.0045.f1b4',
                                                      'Interface': 'MgmtEth0/0/CPU0/0',
                                                      'State': 'Dynamic',
                                                      'Type': 'ARPA'}},
              '10.30.108.3': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.3',
                                                    'Age': '00:01:36',
                                                    'Hardware Addr': '18ef.63e6.9bc1',
                                                    'Interface': 'MgmtEth0/0/CPU0/0',
                                                    'State': 'Dynamic',
                                                    'Type': 'ARPA'}},
              '10.30.108.4': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.4',
                                                    'Age': '00:27:43',
                                                    'Hardware Addr': '0050.568e.0e98',
                                                    'Interface': 'MgmtEth0/0/CPU0/0',
                                                    'State': 'Dynamic',
                                                    'Type': 'ARPA'}},
              '10.30.108.95': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.95',
                                                     'Age': '00:06:17',
                                                     'Hardware Addr': '5254.0053.ff84',
                                                     'Interface': 'MgmtEth0/0/CPU0/0',
                                                     'State': 'Dynamic',
                                                     'Type': 'ARPA'}},
              '10.30.108.96': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.96',
                                                     'Age': '02:49:00',
                                                     'Hardware Addr': '5254.00a2.e74f',
                                                     'Interface': 'MgmtEth0/0/CPU0/0',
                                                     'State': 'Dynamic',
                                                     'Type': 'ARPA'}},
              '10.30.108.97': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.97',
                                                     'Age': '03:00:30',
                                                     'Hardware Addr': '5254.0072.3362',
                                                     'Interface': 'MgmtEth0/0/CPU0/0',
                                                     'State': 'Dynamic',
                                                     'Type': 'ARPA'}},
              '10.30.108.98': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.98',
                                                     'Age': '03:46:02',
                                                     'Hardware Addr': '5254.00bb.61f0',
                                                     'Interface': 'MgmtEth0/0/CPU0/0',
                                                     'State': 'Dynamic',
                                                     'Type': 'ARPA'}},
              '10.30.109.114': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.109.114',
                                                      'Age': '01:41:44',
                                                      'Hardware Addr': '5254.0008.0373',
                                                      'Interface': 'MgmtEth0/0/CPU0/0',
                                                      'State': 'Dynamic',
                                                      'Type': 'ARPA'}},
              '10.30.109.131': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.109.131',
                                                      'Age': '02:08:28',
                                                      'Hardware Addr': '5254.00df.80f5',
                                                      'Interface': 'MgmtEth0/0/CPU0/0',
                                                      'State': 'Dynamic',
                                                      'Type': 'ARPA'}},
              '10.30.109.132': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.109.132',
                                                      'Age': '01:35:21',
                                                      'Hardware Addr': '5254.0060.6195',
                                                      'Interface': 'MgmtEth0/0/CPU0/0',
                                                      'State': 'Dynamic',
                                                      'Type': 'ARPA'}},
              '10.30.109.239': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.109.239',
                                                      'Age': '01:46:50',
                                                      'Hardware Addr': '5254.007f.b191',
                                                      'Interface': 'MgmtEth0/0/CPU0/0',
                                                      'State': 'Dynamic',
                                                      'Type': 'ARPA'}},
              '10.30.109.240': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.109.240',
                                                      'Age': '00:27:43',
                                                      'Hardware Addr': '5254.00e3.308d',
                                                      'Interface': 'MgmtEth0/0/CPU0/0',
                                                      'State': 'Dynamic',
                                                      'Type': 'ARPA'}},
              '10.30.109.93': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.109.93',
                                                     'Age': '00:00:34',
                                                     'Hardware Addr': '5254.0094.c1fe',
                                                     'Interface': 'MgmtEth0/0/CPU0/0',
                                                     'State': 'Dynamic',
                                                     'Type': 'ARPA'}},
              '10.30.109.94': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.109.94',
                                                     'Age': '02:58:23',
                                                     'Hardware Addr': '5254.0045.ae0f',
                                                     'Interface': 'MgmtEth0/0/CPU0/0',
                                                     'State': 'Dynamic',
                                                     'Type': 'ARPA'}},
              '10.30.109.96': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.109.96',
                                                     'Age': '-',
                                                     'Hardware Addr': '5254.00f7.b674',
                                                     'Interface': 'MgmtEth0/0/CPU0/0',
                                                     'State': 'Probe',
                                                     'Type': 'ARPA'}},
              '10.30.97.64': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.97.64',
                                                    'Age': '00:33:09',
                                                    'Hardware Addr': '0050.568e.6227',
                                                    'Interface': 'MgmtEth0/0/CPU0/0',
                                                    'State': 'Dynamic',
                                                    'Type': 'ARPA'}},
              '10.30.97.68': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.97.68',
                                                    'Age': '00:00:00',
                                                    'Hardware Addr': '0050.568e.3711',
                                                    'Interface': 'MgmtEth0/0/CPU0/0',
                                                    'State': 'Dynamic',
                                                    'Type': 'ARPA'}}}}

        self.outputDict3= {'0/FC0/0': {'0': {'Admin /Oper': 'UP/UP',
                                   'Asic State': 'NRML',
                                   'Asic class': 'FE1600',
                                   'Asic inst. (R/S/A) ': '0/FC0/0',
                                   'Asic type': 's13',
                                   'DC': '0',
                                   'Fgid DL': 'DONE',
                                   'HP': '1',
                                   'HR (#)': '0',
                                   'Last init': 'PON',
                                   'PON State (#)': '1',
                                   'card pwrd': 'UP',
                                   'plane /grp': '0/0'}},
                 '0/FC0/1': {'0': {'Admin /Oper': 'UP/UP',
                                   'Asic State': 'NRML',
                                   'Asic class': 'FE1600',
                                   'Asic inst. (R/S/A) ': '0/FC0/1',
                                   'Asic type': 's13',
                                   'DC': '0',
                                   'Fgid DL': 'DONE',
                                   'HP': '1',
                                   'HR (#)': '0',
                                   'Last init': 'PON',
                                   'PON State (#)': '1',
                                   'card pwrd': 'UP',
                                   'plane /grp': '0/1'}},
                 '0/FC0/2': {'0': {'Admin /Oper': 'UP/UP',
                                   'Asic State': 'NRML',
                                   'Asic class': 'FE1600',
                                   'Asic inst. (R/S/A) ': '0/FC0/2',
                                   'Asic type': 's13',
                                   'DC': '0',
                                   'Fgid DL': 'DONE',
                                   'HP': '1',
                                   'HR (#)': '0',
                                   'Last init': 'PON',
                                   'PON State (#)': '1',
                                   'card pwrd': 'UP',
                                   'plane /grp': '0/2'}},
                 '0/FC0/3': {'0': {'Admin /Oper': 'UP/UP',
                                   'Asic State': 'NRML',
                                   'Asic class': 'FE1600',
                                   'Asic inst. (R/S/A) ': '0/FC0/3',
                                   'Asic type': 's13',
                                   'DC': '0',
                                   'Fgid DL': 'DONE',
                                   'HP': '1',
                                   'HR (#)': '0',
                                   'Last init': 'PON',
                                   'PON State (#)': '1',
                                   'card pwrd': 'UP',
                                   'plane /grp': '0/3'}}}

        self.outputDict4 = {
            'GigabitEthernet0/0':
                {'up':
                    {'IP-Address': '10.1.10.20',
                     'Interface': 'GigabitEthernet0/0',
                     'Method': 'NVRAM',
                     'OK?': 'YES',
                     'Protocol': 'up',
                     'Status': 'up'}},
            'GigabitEthernet1/0/1':
                {'up':
                    {'IP-Address': 'unassigned',
                     'Interface': 'GigabitEthernet1/0/1',
                     'Method': 'unset',
                     'OK?': 'YES',
                     'Protocol': 'up',
                     'Status': 'up'}},
            'GigabitEthernet1/0/10':
                {'down':
                    {'IP-Address': 'unassigned',
                     'Interface': 'GigabitEthernet1/0/10',
                     'Method': 'unset',
                     'OK?': 'YES',
                     'Protocol': 'down',
                     'Status': 'down'}}}

        self.outputDict5={'0/0/CPU0': {'10.30.108.1': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.1',
                                                    'Age': '01:26:25',
                                                    'Hardware Addr': '0007.b400.6c01',
                                                    'Interface': 'MgmtEth0/0/CPU0/0',
                                                    'State': 'Dynamic',
                                                    'Type': 'ARPA'}},
              '10.30.108.115': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.115',
                                                      'Age': '01:38:01',
                                                      'Hardware Addr': '5254.00eb.87cf',
                                                      'Interface': 'MgmtEth0/0/CPU0/0',
                                                      'State': 'Dynamic',
                                                      'Type': 'ARPA'}},
              '10.30.108.132': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.132',
                                                      'Age': '-',
                                                      'Hardware Addr': '5254.00d6.36c9',
                                                      'Interface': 'MgmtEth0/0/CPU0/0',
                                                      'State': 'Interface',
                                                      'Type': 'ARPA'}},
              '10.30.108.2': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.2',
                                                    'Age': '00:00:27',
                                                    'Hardware Addr': '18ef.63e6.a841',
                                                    'Interface': 'MgmtEth0/0/CPU0/0',
                                                    'State': 'Dynamic',
                                                    'Type': 'ARPA'}},
              '10.30.108.241': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.241',
                                                      'Age': '01:47:43',
                                                      'Hardware Addr': '5254.0045.f1b4',
                                                      'Interface': 'MgmtEth0/0/CPU0/0',
                                                      'State': 'Dynamic',
                                                      'Type': 'ARPA'}},
              '10.30.108.3': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.3',
                                                    'Age': '00:01:36',
                                                    'Hardware Addr': '18ef.63e6.9bc1',
                                                    'Interface': 'MgmtEth0/0/CPU0/0',
                                                    'State': 'Dynamic',
                                                    'Type': 'ARPA'}},
              '10.30.108.4': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.4',
                                                    'Age': '00:27:43',
                                                    'Hardware Addr': '0050.568e.0e98',
                                                    'Interface': 'MgmtEth0/0/CPU0/0',
                                                    'State': 'Dynamic',
                                                    'Type': 'ARPA'}},
              '10.30.108.95': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.95',
                                                     'Age': '00:06:17',
                                                     'Hardware Addr': '5254.0053.ff84',
                                                     'Interface': 'MgmtEth0/0/CPU0/0',
                                                     'State': 'Dynamic',
                                                     'Type': 'ARPA'}},
              '10.30.108.96': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.96',
                                                     'Age': '02:49:00',
                                                     'Hardware Addr': '5254.00a2.e74f',
                                                     'Interface': 'MgmtEth0/0/CPU0/0',
                                                     'State': 'Dynamic',
                                                     'Type': 'ARPA'}},
              '10.30.108.97': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.97',
                                                     'Age': '03:00:30',
                                                     'Hardware Addr': '5254.0072.3362',
                                                     'Interface': 'MgmtEth0/0/CPU0/0',
                                                     'State': 'Dynamic',
                                                     'Type': 'ARPA'}},
              '10.30.108.98': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.108.98',
                                                     'Age': '03:46:02',
                                                     'Hardware Addr': '5254.00bb.61f0',
                                                     'Interface': 'MgmtEth0/0/CPU0/0',
                                                     'State': 'Dynamic',
                                                     'Type': 'ARPA'}},
              '10.30.109.114': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.109.114',
                                                      'Age': '01:41:44',
                                                      'Hardware Addr': '5254.0008.0373',
                                                      'Interface': 'MgmtEth0/0/CPU0/0',
                                                      'State': 'Dynamic',
                                                      'Type': 'ARPA'}},
              '10.30.109.131': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.109.131',
                                                      'Age': '02:08:28',
                                                      'Hardware Addr': '5254.00df.80f5',
                                                      'Interface': 'MgmtEth0/0/CPU0/0',
                                                      'State': 'Dynamic',
                                                      'Type': 'ARPA'}},
              '10.30.109.132': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.109.132',
                                                      'Age': '01:35:21',
                                                      'Hardware Addr': '5254.0060.6195',
                                                      'Interface': 'MgmtEth0/0/CPU0/0',
                                                      'State': 'Dynamic',
                                                      'Type': 'ARPA'}},
              '10.30.109.239': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.109.239',
                                                      'Age': '01:46:50',
                                                      'Hardware Addr': '5254.007f.b191',
                                                      'Interface': 'MgmtEth0/0/CPU0/0',
                                                      'State': 'Dynamic',
                                                      'Type': 'ARPA'}},
              '10.30.109.240': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.109.240',
                                                      'Age': '00:27:43',
                                                      'Hardware Addr': '5254.00e3.308d',
                                                      'Interface': 'MgmtEth0/0/CPU0/0',
                                                      'State': 'Dynamic',
                                                      'Type': 'ARPA'}},
              '10.30.109.93': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.109.93',
                                                     'Age': '00:00:34',
                                                     'Hardware Addr': '5254.0094.c1fe',
                                                     'Interface': 'MgmtEth0/0/CPU0/0',
                                                     'State': 'Dynamic',
                                                     'Type': 'ARPA'}},
              '10.30.109.94': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.109.94',
                                                     'Age': '02:58:23',
                                                     'Hardware Addr': '5254.0045.ae0f',
                                                     'Interface': 'MgmtEth0/0/CPU0/0',
                                                     'State': 'Dynamic',
                                                     'Type': 'ARPA'}},
              '10.30.109.96': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.109.96',
                                                     'Age': '-',
                                                     'Hardware Addr': '5254.00f7.b674',
                                                     'Interface': 'MgmtEth0/0/CPU0/0',
                                                     'State': 'Probe',
                                                     'Type': 'ARPA'}},
              '10.30.97.64': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.97.64',
                                                    'Age': '00:33:09',
                                                    'Hardware Addr': '0050.568e.6227',
                                                    'Interface': 'MgmtEth0/0/CPU0/0',
                                                    'State': 'Dynamic',
                                                    'Type': 'ARPA'}},
              '10.30.97.68': {'MgmtEth0/0/CPU0/0': {'Address': '10.30.97.68',
                                                    'Age': '00:00:00',
                                                    'Hardware Addr': '0050.568e.3711',
                                                    'Interface': 'MgmtEth0/0/CPU0/0',
                                                    'State': 'Dynamic',
                                                    'Type': 'ARPA'}}}}

        self.outputDict6={'CCC FPGA (Backup)':
                            {'Enabled': 'N/A', 'Build Date': '02/26/2014', 'Note': '', 'Version': '1.23.0', 'Image Name': 'CCC FPGA (Backup)', 'bytes': '2453207'},
                          'CCC Power-On (Backup)':
                            {'Enabled': 'N/A', 'Build Date': '02/14/2014', 'Note': '', 'Version': '1.32', 'Image Name': 'CCC Power-On (Backup)', 'bytes': '9048'},
                          'CCC Power-On':
                            {'Enabled': 'N/A    A', 'Build Date': '11/21/2014', 'Note': 'ctive', 'Version': '1.39', 'Image Name': 'CCC Power-On', 'bytes': '11789'},
                          'Secure Boot Certificates':
                            {'Enabled': 'N/A', 'Build Date': '06/13/2013', 'Note': '', 'Version': '1.00', 'Image Name': 'Secure Boot Certificates', 'bytes': '1047'},
                          'CCC FPGA':
                            {'Enabled': 'N/A    A', 'Build Date': '12/24/2014', 'Note': 'ctive', 'Version': '1.28.0', 'Image Name': 'CCC FPGA', 'bytes': '2453207'}}

        self.outputDict7={'02:27:57.002':
                            {'':
                                {'LOC': '0/7', 'TIME': '02:27:57.002', 'EVENT': 'INSERTED', 'CARD TYPE': 'NC6-10X100G-M-K', 'SERIAL NO': 'SAL1929K8RJ', 'DATE': '04/22'}},
                          '02:22:17.765':
                            {'':
                                {'LOC': '0/7', 'TIME': '02:22:17.765', 'EVENT': 'REMOVED', 'CARD TYPE': 'NC6-20X100GE-M-C', 'SERIAL NO': 'SAL211004A5', 'DATE': '04/22'}},
                          '00:45:54.331':
                            {'':
                                {'LOC': '0/FC4', 'TIME': '00:45:54.331', 'EVENT': 'DISCOVERED', 'CARD TYPE': 'NC6-FC2-U', 'SERIAL NO': 'SAL210304GG', 'DATE': '04/22'}},
                          '00:45:54.426':
                            {'':
                                {'LOC': '0/FC5', 'TIME': '00:45:54.426', 'EVENT': 'DISCOVERED', 'CARD TYPE': 'NC6-FC2-U', 'SERIAL NO': 'SAL210304H4', 'DATE': '04/22'}},
                          '00:45:54.471':
                            {'':
                                {'LOC': '0/RP0', 'TIME': '00:45:54.471', 'EVENT': 'DISCOVERED', 'CARD TYPE': 'NC6-RP', 'SERIAL NO': 'SAL1923GBM1', 'DATE': '04/22'}}}

        self.outputDict8={'Rx Ch 10:':
                            {'0.99mW  -0.0524dBm':
                                {'Channel Status': 'Enabled', 'Optical Power Alarm': 'off', 'Optical Power Input': '0.99mW  -0.0524dBm', 'Signal Strength': 'Signal Detected', 'Channel Number': 'Rx Ch 10:'}},
                          'Rx Ch 11:':
                            {'1.13mW  0.5346dBm':
                                {'Channel Status': 'Enabled', 'Optical Power Alarm': 'off', 'Optical Power Input': '1.13mW  0.5346dBm', 'Signal Strength': 'Signal Detected', 'Channel Number': 'Rx Ch 11:'}},
                          'Rx Ch 0:':
                            {'0.95mW  -0.2182dBm':
                                {'Channel Status': 'Enabled', 'Optical Power Alarm': 'off', 'Optical Power Input': '0.95mW  -0.2182dBm', 'Signal Strength': 'Signal Detected', 'Channel Number': 'Rx Ch 0:'}},
                          'Rx Ch 6:':
                            {'1.15mW  0.6070dBm':
                                {'Channel Status': 'Enabled', 'Optical Power Alarm': 'off', 'Optical Power Input': '1.15mW  0.6070dBm', 'Signal Strength': 'Signal Detected', 'Channel Number': 'Rx Ch 6:'}},
                          'Rx Ch 2:':
                            {'1.09mW  0.3822dBm':
                                {'Channel Status': 'Enabled', 'Optical Power Alarm': 'off', 'Optical Power Input': '1.09mW  0.3822dBm', 'Signal Strength': 'Signal Detected', 'Channel Number': 'Rx Ch 2:'}},
                          'Rx Ch 8:':
                            {'1.19mW  0.7518dBm':
                                {'Channel Status': 'Enabled', 'Optical Power Alarm': 'off', 'Optical Power Input': '1.19mW  0.7518dBm', 'Signal Strength': 'Signal Detected', 'Channel Number': 'Rx Ch 8:'}},
                          'Rx Ch 1:':
                            {'1.09mW  0.3782dBm':
                                {'Channel Status': 'Enabled', 'Optical Power Alarm': 'off', 'Optical Power Input': '1.09mW  0.3782dBm', 'Signal Strength': 'Signal Detected', 'Channel Number': 'Rx Ch 1:'}},
                          'Rx Ch 5:':
                            {'1.25mW  0.9864dBm':
                                {'Channel Status': 'Enabled', 'Optical Power Alarm': 'off', 'Optical Power Input': '1.25mW  0.9864dBm', 'Signal Strength': 'Signal Detected', 'Channel Number': 'Rx Ch 5:'}},
                          'Rx Ch 9:':
                            {'1.15mW  0.6258dBm':
                                {'Channel Status': 'Enabled', 'Optical Power Alarm': 'off', 'Optical Power Input': '1.15mW  0.6258dBm', 'Signal Strength': 'Signal Detected', 'Channel Number': 'Rx Ch 9:'}},
                          'Rx Ch 4:':
                            {'1.17mW  0.6819dBm':
                                {'Channel Status': 'Enabled', 'Optical Power Alarm': 'off', 'Optical Power Input': '1.17mW  0.6819dBm', 'Signal Strength': 'Signal Detected', 'Channel Number': 'Rx Ch 4:'}},
                          'Rx Ch 7:':
                            {'1.09mW  0.3822dBm':
                                {'Channel Status': 'Enabled', 'Optical Power Alarm': 'off', 'Optical Power Input': '1.09mW  0.3822dBm', 'Signal Strength': 'Signal Detected', 'Channel Number': 'Rx Ch 7:'}},
                          'Rx Ch 3:':
                            {'1.07mW  0.2857dBm':
                                {'Channel Status': 'Enabled', 'Optical Power Alarm': 'off', 'Optical Power Input': '1.07mW  0.2857dBm', 'Signal Strength': 'Signal Detected', 'Channel Number': 'Rx Ch 3:'}}}

        self.outputDict9={
            '':
                {'':
                    {'Crit (Hi)': '',
                     'Crit (Lo)': '',
                     'Location': 'F0/FC0',
                     'Major (Hi)': '',
                     'Major (Lo)': '',
                     'Minor (Hi)': '',
                     'Minor (Lo)': '',
                     'TEMPERATURE Sensor': '',
                     'Value (deg C)': ''}},
            'FE_0 Die':
                {'120':
                    {'Crit (Hi)': '120',
                     'Crit (Lo)': '-10',
                     'Location': '',
                     'Major (Hi)': '115',
                     'Major (Lo)': '-5',
                     'Minor (Hi)': '105',
                     'Minor (Lo)': '0',
                     'TEMPERATURE Sensor': 'FE_0 Die',
                     'Value (deg C)': '46'}},
            'FE_1 Die':
                {'120':
                    {'Crit (Hi)': '120',
                     'Crit (Lo)': '-10',
                     'Location': '',
                     'Major (Hi)': '115',
                     'Major (Lo)': '-5',
                     'Minor (Hi)': '105',
                     'Minor (Lo)': '0',
                     'TEMPERATURE Sensor': 'FE_1 Die',
                     'Value (deg C)': '45'}},
            'FE_2 Die':
                {'120':
                    {'Crit (Hi)': '120',
                     'Crit (Lo)': '-10',
                     'Location': '',
                     'Major (Hi)': '115',
                     'Major (Lo)': '-5',
                     'Minor (Hi)': '105',
                     'Minor (Lo)': '0',
                     'TEMPERATURE Sensor': 'FE_2 Die',
                     'Value (deg C)': '49'}},
            'HotSpot':
                {'105':
                    {'Crit (Hi)': '105',
                     'Crit (Lo)': '-10',
                     'Location': '',
                     'Major (Hi)': '100',
                     'Major (Lo)': '-5',
                     'Minor (Hi)': '95',
                     'Minor (Lo)': '0',
                     'TEMPERATURE Sensor': 'HotSpot',
                     'Value (deg C)': '40'}},
            'Inlet':
                {'75':
                    {'Crit (Hi)': '75',
                     'Crit (Lo)': '-10',
                     'Location': '',
                     'Major (Hi)': '65',
                     'Major (Lo)': '-5',
                     'Minor (Hi)': '55',
                     'Minor (Lo)': '0',
                     'TEMPERATURE Sensor': 'Inlet',
                     'Value (deg C)': '34'}},
            'Outlet':
                {'85':  
                    {'Crit (Hi)': '85',
                     'Crit (Lo)': '-10',
                     'Location': '',
                     'Major (Hi)': '75',
                     'Major (Lo)': '-5',
                     'Minor (Hi)': '65',
                     'Minor (Lo)': '0',
                     'TEMPERATURE Sensor': 'Outlet',
                     'Value (deg C)': '45'}},
            'PCIe Die':
                {'125':
                    {'Crit (Hi)': '125',
                     'Crit (Lo)': '-10',
                     'Location': '',
                     'Major (Hi)': '115',
                     'Major (Lo)': '-5',
                     'Minor (Hi)': '105',
                     'Minor (Lo)': '0',
                     'TEMPERATURE Sensor': 'PCIe Die',
                     'Value (deg C)': '46'}}}

        self.outputDict10={
            '117':
                {'':
                    {'JID': '117',
                     'LAST STARTED': '04/14/2017 15:37:31.242',
                     'MAINT-MODE': '',
                     'MANDATORY': 'Y',
                     'NAME (IID) ARGS': 'devc-conaux-con(1) -c -h -d librs232.dll '
                                        '-b -m libconaux.dll -c -u libslinux.dll '
                                        '-c -p /dev/hvc0',
                     'PLACEMENT': '',
                     'RESTART': '1',
                     'STATE': 'Run'}},
             '118':
                {'':
                    {'JID': '118',
                     'LAST STARTED': '04/14/2017 15:37:31.166',
                     'MAINT-MODE': '',
                     'MANDATORY': 'Y',
                     'NAME (IID) ARGS': 'devc-conaux-aux(1) -a -h -d librs232.dll '
                                        '-b -m libconaux.dll -a -u libslinux.dll '
                                        '-a -p /dev/hvc1',
                     'PLACEMENT': '',
                     'RESTART': '1',
                     'STATE': 'Run'}},
             '119':
                {'':
                    {'JID': '119',
                     'LAST STARTED': '04/14/2017 15:37:31.311',
                     'MAINT-MODE': '',
                     'MANDATORY': 'Y',
                     'NAME (IID) ARGS': 'shmwin_svr(1)',
                     'PLACEMENT': '',
                     'RESTART': '1',
                     'STATE': 'Run'}},
             '212':
                {'':
                    {'JID': '212',
                     'LAST STARTED': '04/14/2017 15:37:31.377',
                     'MAINT-MODE': '',
                     'MANDATORY': 'M      Y',
                     'NAME (IID) ARGS': 'sdr_invmgr(1)',
                     'PLACEMENT': '',
                     'RESTART': '1',
                     'STATE': 'Run'}},
             '53':
                {'':
                    {'JID': '53',
                     'LAST STARTED': '04/14/2017 15:37:30.517',
                     'MAINT-MODE': '',
                     'MANDATORY': 'M      Y',
                     'NAME (IID) ARGS': 'dsr(1)',
                     'PLACEMENT': '',
                     'RESTART': '1',
                     'STATE': 'Run'}}}

        self.outputDict11={
            'F0/FC0': 
                {'Card Type': 'NCS-F-FC',
                 'Location': 'F0/FC0',
                 'Power Allocated Watts': '440',
                 'Power Used Watts': '291',
                 'Status': 'ON'}
                }

        self.outputDict12={
            'mini':
                {'NAME': 'mini', 'POWER': 'on', 'STATE': 'deployed'},
            'mini2':
                {'NAME': 'mini2', 'POWER': 'on', 'STATE': 'deployed'}}

    def test_subclassed_tabular_parser(self):

        def _hexint (val):
            return int(val, 16)

        def cleanupLspId (field):
            return field


        class my_isis_database_column_parser_t (oper_fill_tabular):
            field_mapping = {
                'LSPID'       :   str,
                'LSP Seq Num' :   _hexint,
                'LSP Checksum':   _hexint,
                'LSP Holdtime':   None,
                }

            table_title_mapping = [ int ]

            def __init__ (self, device, show_command):
                headers = ["LSPID", "LSP Seq Num", "LSP Checksum",
                "LSP Holdtime",  "ATT/P/OL"]
                labels = headers

                super(my_isis_database_column_parser_t, self).__init__(
                 device,
                 show_command,
                 header_fields=headers,
                 table_terminal_pattern="Total Level-[12] LSP count:",
                 table_title_pattern =
                 r"IS-IS (?:[-\w]+ )?\(?Level-([12])\)? Link State Database:?",
                 label_fields = labels)

            def cleanup_entry_field (self, header, field):
                if header == "LSPID":
                    # Strip the "*" off the LSPID for the router's own LSPID.
                    return cleanupLspId(field)
                else:
                    return field


        self.maxDiff = None

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput1)}
        dev1 = Mock(**device_kwargs)
        dev1.name='router1'

        result = my_isis_database_column_parser_t(dev1, "show isis database")
        self.assertEqual(result.entries, self.outputDict1)


    def test_tabular_parser_1(self):
        self.maxDiff = None

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput2)}
        dev1 = Mock(**device_kwargs)
        dev1.name='router3'

        result = oper_fill_tabular(device=dev1,
                                    show_command="show arp",
                                    refresh_cache=True,
                                    header_fields=
                                    [ "Address",
                                      "Age",
                                      "Hardware Addr",
                                      "State",
                                      "Type",
                                      "Interface" ],
                                    index = [ 0, 5 ],
                                    table_title_pattern = r"^(\d+/\d+/CPU\d+)" )
        self.assertEqual(result.entries, self.outputDict2)
        args, kwargs = dev1.execute.call_args
        self.assertTrue('show arp' in args,
            msg='The expected command was not sent to the router')


    def test_tabular_parser_2(self):
        """ Testing tabular parsing with delimiters in the whole table"""
        self.maxDiff = None

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput3)}
        dev1 = Mock(**device_kwargs)
        dev1.name='router3'

        result = oper_fill_tabular(device=dev1,
                                    show_command="show arp",
                                    refresh_cache=True,
                                    header_fields=
                                    [ "Address",
                                      "Age",
                                      "Hardware Addr",
                                      "State",
                                      "Type",
                                      "Interface" ],
                                    label_fields=
                                    [ "Address",
                                      "Age",
                                      "Hardware Addr",
                                      "State",
                                      "Type",
                                      "Interface" ],
                                    index = [ 0, 5 ],
                                    table_title_pattern = r"^(\d+/\d+/CPU\d+)",
                                    delimiter = '|')

        self.assertEqual(result.entries, self.outputDict5)
        args, kwargs = dev1.execute.call_args
        self.assertTrue('show arp' in args,
            msg='The expected command was not sent to the router')

    def test_tabular_parser_3(self):
        """ Testing tabular parsing with delimiters in table body (only) """
        self.maxDiff = None

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput4)}
        dev1 = Mock(**device_kwargs)
        dev1.name='router3'

        result = oper_fill_tabular(device=dev1,
                                    show_command="show arp",
                                    refresh_cache=True,
                                    header_fields=
                                    [ "Address",
                                      "Age",
                                      "Hardware Addr",
                                      "State",
                                      "Type",
                                      "Interface" ],
                                    label_fields=
                                    [ "Address",
                                      "Age",
                                      "Hardware Addr",
                                      "State",
                                      "Type",
                                      "Interface" ],
                                    index = [ 0, 5 ],
                                    table_title_pattern = r"^(\d+/\d+/CPU\d+)",
                                    delimiter = '|')

        self.assertEqual(result.entries, self.outputDict2)
        args, kwargs = dev1.execute.call_args
        self.assertTrue('show arp' in args,
            msg='The expected command was not sent to the router')

    def test_tabular_parser_4(self):
        """ Testing the multiline header support in tabular parsing """
        self.maxDiff = None

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput5)}
        dev1 = Mock(**device_kwargs)
        dev1.name='router3'

        result = oper_fill_tabular(device=dev1,
                                    show_command="show arp",
                                    refresh_cache=True,
                                    header_fields=
                                    [['Asic inst\.',
                                      'card',
                                      'HP',
                                      'Asic',
                                      'Asic',
                                      'Admin',
                                      'plane',
                                      'Fgid',
                                      'Asic State',
                                      'DC',
                                      'Last',
                                      'PON',
                                      'HR'],
                                    ['\(R/S/A\)',
                                     'pwrd',
                                     '',
                                     'type',
                                     'class',
                                     '/Oper',
                                     '/grp',
                                     'DL',
                                     '',
                                     '',
                                     'init',
                                     '\(#\)',
                                     '\(#\)']],
                                    label_fields=
                                    [ "Asic inst. (R/S/A) ",
                                      "card pwrd",
                                      "HP",
                                      "Asic type",
                                      "Asic class",
                                      "Admin /Oper",
                                      "plane /grp",
                                      "Fgid DL",
                                      "Asic State",
                                      "DC",
                                      "Last init",
                                      "PON State (#)",
                                      "HR (#)" ],
                                    index = [ 0, 12 ],
                                    delimiter = '|')

        self.assertEqual(result.entries, self.outputDict3)
        args, kwargs = dev1.execute.call_args
        self.assertTrue('show arp' in args,
            msg='The expected command was not sent to the router')

    def test_tabular_parser_5(self):
        """ Using regex in the header_fields to support dynamic headers """
        self.maxDiff = None

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput2)}
        dev1 = Mock(**device_kwargs)
        dev1.name='router3'

        result = oper_fill_tabular(device=dev1,
                                    show_command="show arp",
                                    refresh_cache=True,
                                    header_fields=
                                    [ "Add[a-z]+",
                                      "Age",
                                      "Hardware Addr",
                                      "State",
                                      "Type",
                                      "Interface" ],
                                    label_fields=
                                    [ "Address",
                                      "Age",
                                      "Hardware Addr",
                                      "State",
                                      "Type",
                                      "Interface" ],
                                    index = [ 0, 5 ],
                                    table_title_pattern = r"^(\d+/\d+/CPU\d+)" )
        self.assertEqual(result.entries, self.outputDict2)
        args, kwargs = dev1.execute.call_args
        self.assertTrue('show arp' in args,
            msg='The expected command was not sent to the router')

    def test_tabular_parser_6(self):
        """ No regex in the header_fields and no label_fields defined """
        self.maxDiff = None

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput2)}
        dev1 = Mock(**device_kwargs)
        # Clear our the mock device's call_args.
        dev1.execute.reset_mock()
        dev1.name='router4'

        result = oper_fill_tabular(device=dev1,
                                    show_command="show arp",
                                    refresh_cache=False,
                                    header_fields=
                                    [ "Address",
                                      "Age",
                                      "Hardware Addr",
                                      "State",
                                      "Type",
                                      "Interface" ],
                                    index = [ 0, 5 ],
                                    table_title_pattern = r"^(\d+/\d+/CPU\d+)" )
        self.assertEqual(result.entries, self.outputDict2)
        args, kwargs = dev1.execute.call_args
        self.assertTrue('show arp' in args,
            msg='The expected command was not sent to the router')

    def test_tabular_parser_7(self):
        self.maxDiff = None

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput2)}
        dev1 = Mock(**device_kwargs)

        # Clear our the mock device's call_args.
        dev1.execute.reset_mock()
        dev1.name='router3'

        result = oper_fill_tabular(device=dev1,
                                    show_command="show arp",
                                    refresh_cache=False,
                                    header_fields=
                                    [ "Address",
                                      "Age",
                                      "Hardware Addr",
                                      "State",
                                      "Type",
                                      "Interface" ],
                                    index = [ 0, 5 ],
                                    table_title_pattern = r"^(\d+/\d+/CPU\d+)" )
        self.assertEqual(result.entries, self.outputDict2)
        self.assertEqual(dev1.execute.call_args, None)

        self.assertRaises(ValueError, oper_fill_tabular,
                                    device=dev1,
                                    show_command="show arp",
                                    refresh_cache=False,
                                    header_fields=
                                    [ "Address",
                                      "Age",
                                      "Hardware Addr",
                                      "State",
                                      "Type",
                                      "Interface" ],
                                    index = '[ 0, 5 ]',
                                    table_title_pattern = r"^(\d+/\d+/CPU\d+)" )

    def test_tabular_parser_8(self):
        """ Sunny day test with user-specified connection alias. """
        self.maxDiff = None

        # Define how device stub will behave when accessed by production parser.
        dev1 = Mock()
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput2)}
        dev1.myalias = Mock(**device_kwargs)
        dev1.name='router3'

        result = oper_fill_tabular(device=dev1,
                                    device_conn_alias='myalias',
                                    show_command="show arp",
                                    refresh_cache=True,
                                    header_fields=
                                    [ "Address",
                                      "Age",
                                      "Hardware Addr",
                                      "State",
                                      "Type",
                                      "Interface" ],
                                    index = [ 0, 5 ],
                                    table_title_pattern = r"^(\d+/\d+/CPU\d+)" )
        self.assertEqual(result.entries, self.outputDict2)
        args, kwargs = dev1.myalias.execute.call_args
        self.assertTrue('show arp' in args,
            msg='The expected command was not sent to the router')

    def test_tabular_parser_9(self):

        """
            Test tabular parser when passing a device output
            and device os only.
        """

        self.maxDiff = None
        pure_cli='''
            Interface              IP-Address      OK? Method Status                Protocol
            GigabitEthernet0/0     10.1.10.20      YES NVRAM  up                    up
            GigabitEthernet1/0/1   unassigned      YES unset  up                    up
            GigabitEthernet1/0/10  unassigned      YES unset  down                  down
        '''
        device_os = 'iosxe'

        res = parsergen.oper_fill_tabular(header_fields=
                                            [ "Interface",
                                              "IP-Address",
                                              "OK\?",
                                              "Method",
                                              "Status",
                                              "Protocol" ],
                                          label_fields=
                                            [ "Interface",
                                              "IP-Address",
                                              "OK?",
                                              "Method",
                                              "Status",
                                              "Protocol" ],
                                          index=[ 0, 5 ],
                                          device_output = pure_cli,
                                          device_os = device_os)

        self.assertEqual(res.entries, self.outputDict4)

    def test_tabular_parser_10(self):

        """
            Testing the attribute error raise when passing neither device
            nor device output.
        """
        with self.assertRaises(AttributeError):
            res = parsergen.oper_fill_tabular(header_fields=
                                                [ "Interface",
                                                  "IP-Address",
                                                  "OK\?",
                                                  "Method",
                                                  "Status",
                                                  "Protocol" ],
                                              label_fields=
                                                [ "Interface",
                                                  "IP-Address",
                                                  "OK?",
                                                  "Method",
                                                  "Status",
                                                  "Protocol" ],
                                              index=[0])

    def test_mkpgen(self):
        """ Test that the mkpgen tool is generating output. """
        original_basedir = os.path.dirname(os.path.abspath(__file__))
        basedir = original_basedir
        while not os.path.exists('{basedir}/scripts'.format(basedir=basedir))\
                and basedir != '/':
            basedir = os.path.dirname(basedir)

        # If unit tests are running in a user environment, the mkpgen tool
        # has already been installed.
        if basedir == '/':
            cmd = "mkpgen "\
                "{basedir}/scripts/parsergen_demo_mkpg.py".\
                format(basedir=original_basedir)
        else:
            cmd = "{basedir}/scripts/mkpgen "\
                "{basedir}/scripts/parsergen_demo_mkpg.py".\
                format(basedir=basedir)

        mkpgen_output = \
            subprocess.check_output(shlex.split(cmd)).decode('ascii')
        self.assertRegex(mkpgen_output, r"aireos")
        self.assertRegex(mkpgen_output, r"ios")
        self.assertRegex(mkpgen_output, r"iosxe")
        self.assertRegex(mkpgen_output, r"iosxr")
        self.assertRegex(mkpgen_output, r"nxos")

        # Ensure that the mkpgen output is itself valid Python code.
        exec(mkpgen_output)

    def test_tabular_parser_11(self):
        """
            Testing the multiline header support in misalligned (per column)
            tabular parsing.
        """

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput6)}
        dev1 = Mock(**device_kwargs)
        dev1.name='router3'

        result = oper_fill_tabular(device=dev1,
                                    show_command="show arp",
                                    refresh_cache=True,
                                    header_fields=
                                    [['Asic inst\.',
                                      'card',
                                      'HP',
                                      'Asic',
                                      'Asic',
                                      'Admin',
                                      'plane',
                                      'Fgid',
                                      'Asic State',
                                      'DC',
                                      'Last',
                                      'PON',
                                      'HR'],
                                    ['\(R/S/A\)',
                                     'pwrd',
                                     '',
                                     'type',
                                     'class',
                                     '/Oper',
                                     '/grp',
                                     'DL',
                                     '',
                                     '',
                                     'init',
                                     '\(#\)',
                                     '\(#\)']],
                                    label_fields=
                                    [ "Asic inst. (R/S/A) ",
                                      "card pwrd",
                                      "HP",
                                      "Asic type",
                                      "Asic class",
                                      "Admin /Oper",
                                      "plane /grp",
                                      "Fgid DL",
                                      "Asic State",
                                      "DC",
                                      "Last init",
                                      "PON State (#)",
                                      "HR (#)" ],
                                    index = [ 0, 12 ],
                                    delimiter = '|')
        self.assertEqual(result.entries, self.outputDict3)
        args, kwargs = dev1.execute.call_args
        self.assertTrue('show arp' in args,
            msg='The expected command was not sent to the router')

    def test_tabular_parser_12(self):
        """
            Testing the multiline header support in misalligned
            tabular parsing.
        """

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput7)}
        dev1 = Mock(**device_kwargs)
        dev1.name='router3'

        result = oper_fill_tabular(device=dev1,
                                    show_command="show controller sfe driver rack 0",
                                    refresh_cache=True,
                                    header_fields=
                                    [['Asic inst\.',
                                      'card',
                                      'HP',
                                      'Asic',
                                      'Asic',
                                      'Admin',
                                      'plane',
                                      'Fgid',
                                      'Asic State',
                                      'DC',
                                      'Last',
                                      'PON',
                                      'HR'],
                                    ['\(R/S/A\)',
                                     'pwrd',
                                     '',
                                     'type',
                                     'class',
                                     '/Oper',
                                     '/grp',
                                     'DL',
                                     '',
                                     '',
                                     'init',
                                     '\(#\)',
                                     '\(#\)']],
                                    label_fields=
                                    [ "Asic inst. (R/S/A) ",
                                      "card pwrd",
                                      "HP",
                                      "Asic type",
                                      "Asic class",
                                      "Admin /Oper",
                                      "plane /grp",
                                      "Fgid DL",
                                      "Asic State",
                                      "DC",
                                      "Last init",
                                      "PON State (#)",
                                      "HR (#)" ],
                                    index = [ 0, 12 ],
                                    delimiter = '|')
        self.assertEqual(result.entries, self.outputDict3)
        args, kwargs = dev1.execute.call_args
        self.assertTrue('show controller sfe driver rack 0' in args,
            msg='The expected command was not sent to the router')

    def test_tabular_parser_13(self):
        """
            Testing the multiline header support with no index defined.
        """

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput8)}
        dev1 = Mock(**device_kwargs)
        dev1.name='router3'

        result = oper_fill_tabular(device=dev1,
                                   show_command='admin show controller ccc bootflash info location F0/FC0',
                                   header_fields= ['Image Name','Version','Build Date', '\(bytes\)','Enabled','Note'],
                                   label_fields= ['Image Name','Version','Build Date', 'bytes','Enabled','Note'])

        self.assertEqual(result.entries, self.outputDict6)
        args, kwargs = dev1.execute.call_args
        self.assertTrue('admin show controller ccc bootflash info location F0/FC0' in args,
            msg='The expected command was not sent to the router')

    def test_tabular_parser_14(self):
        """
            Testing the dynamic key support in the header field.
        """

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput9)}
        dev1 = Mock(**device_kwargs)
        dev1.name='router3'

        result = oper_fill_tabular(device=dev1,
                                   show_command='admin show controller ccc oir-history rack 0',
                                   header_fields= ['DATE','TIME \([A-Z]+\)','EVENT', 'LOC','CARD TYPE','SERIAL NO'],
                                   label_fields= ['DATE','TIME','EVENT', 'LOC','CARD TYPE','SERIAL NO'],
                                   index=[ 1 , 6 ])

        self.assertEqual(result.entries, self.outputDict7)
        args, kwargs = dev1.execute.call_args
        self.assertTrue('admin show controller ccc oir-history rack 0' in args,
            msg='The expected command was not sent to the router')

        # -------- Testing same table with different header field-----------

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput10)}
        dev1 = Mock(**device_kwargs)
        dev1.name='router3'

        result = oper_fill_tabular(device=dev1,
                                   show_command='admin show controller ccc oir-history rack 0',
                                   header_fields= ['DATE','TIME \([A-Z]+\)','EVENT', 'LOC','CARD TYPE','SERIAL NO'],
                                   label_fields= ['DATE','TIME','EVENT', 'LOC','CARD TYPE','SERIAL NO'],
                                   index=[ 1 , 6 ])

        self.assertEqual(result.entries, self.outputDict7)
        args, kwargs = dev1.execute.call_args
        self.assertTrue('admin show controller ccc oir-history rack 0' in args,
            msg='The expected command was not sent to the router')

    def test_tabular_parser_15(self):
        """
            Testing the multiline header support in misalligned
            tabular parsing with multiple values per field.
        """

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput11)}
        dev1 = Mock(**device_kwargs)
        dev1.name='router3'

        result = oper_fill_tabular(device=dev1,
                                    show_command="show controller fabric cxp dom location F0/FC0 port 0",
                                    refresh_cache=True,
                                    header_fields=
                                    [['Channel',
                                      'Channel',
                                      'Signal \.',
                                      'Optical Power',
                                      'Optical Light'],
                                    ['Number\.',
                                     'Status',
                                     'Strength',
                                     'Alarm',
                                     'Input']],
                                    label_fields=
                                    [ "Channel Number",
                                      "Channel Status",
                                      "Signal Strength",
                                      "Optical Power Alarm",
                                      "Optical Power Input"],
                                    index = [ 0, 4 ],
                                    delimiter = '|')

        self.assertEqual(result.entries, self.outputDict8)
        args, kwargs = dev1.execute.call_args
        self.assertTrue('show controller fabric cxp dom location F0/FC0 port 0' in args,
            msg='The expected command was not sent to the router')

    def test_tabular_parser_16(self):
        """
            Testing the multiline header support in misalligned
            tabular parsing with some table missing fields.
        """

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput12)}
        dev1 = Mock(**device_kwargs)
        dev1.name='router3'

        result = oper_fill_tabular(device=dev1,
                                    show_command="admin show environment temp location F0/FC0",
                                    refresh_cache=True,
                                    header_fields=
                                    [['Location',
                                      'TEMPERATURE',
                                      'Value',
                                      'Crit',
                                      'Major',
                                      'Minor',
                                      'Minor',
                                      'Major',
                                      'Crit'],
                                    ['',
                                      'Sensor',
                                      '\(deg C\)',
                                      '\(Lo\)',
                                      '\(Lo\)',
                                      '\(Lo\)',
                                      '\(Hi\)',
                                      '\(Hi\)',
                                      '\(Hi\)']],
                                    label_fields=
                                    ["Location",
                                      "TEMPERATURE Sensor",
                                      "Value (deg C)",
                                      "Crit (Lo)",
                                      "Major (Lo)",
                                      "Minor (Lo)",
                                      "Minor (Hi)",
                                      "Major (Hi)",
                                      "Crit (Hi)"],
                                    index = [ 1, 8 ],
                                    delimiter = '\s')

        self.assertEqual(result.entries, self.outputDict9)
        args, kwargs = dev1.execute.call_args
        self.assertTrue('admin show environment temp location F0/FC0' in args,
            msg='The expected command was not sent to the router')

    def test_tabular_parser_17(self):
        """
            Testing the multiline header support in misalligned
            header fields.
        """

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput13)}
        dev1 = Mock(**device_kwargs)
        dev1.name='router3'

        result = oper_fill_tabular(device=dev1,
                                    show_command="show processes all",
                                    refresh_cache=True,
                                    header_fields=
                                    [['JID',
                                      'LAST STARTED',
                                      'STATE',
                                      'RE-',
                                      'PLACE-',
                                      'MANDA-',
                                      'MAINT-',
                                      ' NAME\(IID\) ARGS'],
                                    ['',
                                      '',
                                      '',
                                      'START',
                                      'MENT',
                                      'TORY',
                                      'MODE',
                                      '']],
                                    label_fields=
                                    ["JID",
                                      "LAST STARTED",
                                      "STATE",
                                      "RESTART",
                                      "PLACEMENT",
                                      "MANDATORY",
                                      "MAINT-MODE",
                                      "NAME (IID) ARGS"],
                                    index = [0,6],
                                    delimiter = '\s')

        self.assertEqual(result.entries, self.outputDict10)
        args, kwargs = dev1.execute.call_args
        self.assertTrue('show processes all' in args,
            msg='The expected command was not sent to the router')

    def test_tabular_parser_18(self):
        """
            Testing the multiline header support in misalligned
            tabular parsing.
        """

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput14)}
        dev1 = Mock(**device_kwargs)
        dev1.name='router3'

        result = oper_fill_tabular(device=dev1,
                                    show_command="show environment power location F0/FC0",
                                    refresh_cache=True,
                                    header_fields=
                                    [['Location',
                                      'Card Type',
                                      'Power',
                                      'Power',
                                      'Status'],
                                    ['',
                                      '',
                                      'Allocated',
                                      'Used',
                                      ''],
                                    ['',
                                      '',
                                      'Watts',
                                      'Watts',
                                      '']],
                                    label_fields=
                                    ["Location",
                                      "Card Type",
                                      "Power Allocated Watts",
                                      "Power Used Watts",
                                      "Status"],
                                    index = [0],
                                    delimiter = '\s')

        self.assertEqual(result.entries, self.outputDict11)
        args, kwargs = dev1.execute.call_args
        self.assertTrue('show environment power location F0/FC0' in args,
            msg='The expected command was not sent to the router')

    def test_tabular_parser_19(self):
        """
            Testing the tabular output when ending with one of the entries.
        """

        # Define how device stub will behave when accessed by production parser.
        device_kwargs = {'is_connected.return_value':True,
                'execute.return_value':dedent(self.showCommandOutput15)}
        dev1 = Mock(**device_kwargs)
        dev1.name='router3'

        result = parsergen.oper_fill_tabular(device=dev1,
                                             show_command="show service state",
                                             header_fields=['NAME',
                                                            'POWER',
                                                            'STATE'],
                                             index= [0])

        self.assertEqual(result.entries, self.outputDict12)
