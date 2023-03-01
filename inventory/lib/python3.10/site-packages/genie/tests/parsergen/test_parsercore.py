#!/bin/env python

import unittest, inspect, sys

# core
from genie.parsergen import core
from genie.parsergen.core import _mk_parser_gen_t, _parser_gen_t,\
                                 extend_markup, column_table_result_core_t

from textwrap import dedent
import re
import copy

python3 = sys.version_info >= (3,0)

def mkpg(marked_up_input, auto_key_join_char='-',generate_regex_tags=False ):
    mkpg = _mk_parser_gen_t()
    mkpg.process_marked_up_input (iter(marked_up_input.splitlines()), auto_key_join_char)
    return mkpg.generate_output(generate_regex_tags=generate_regex_tags)

showCommandOutput1 = '''\
    BGP router identifier 192.168.0.12, local AS number 100
    BGP generic scan interval 60 secs
    BGP table state: Active
    Table ID: 0xe0000000   RD version: 8
    BGP main routing table version 8
    BGP scan interval 60 secs

    BGP is operating in STANDALONE mode.

    Process       RcvTblVer   bRIB/RIB   LabelVer  ImportVer  SendTblVer  StandbyVer
    Speaker               8          8          8          8           8           8

    Neighbor        Spk    AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down  St/PfxRcd
    50.1.0.2          0   100      63      55        8    0    0 00:51:24        100
    50.1.0.3          0   200      63      55        8    0    0 00:40:16        200
'''


class TestNonTabularParser(unittest.TestCase):

    def setUp(self):
        core._glb_regex = { }
        core._glb_show_commands = {}
        core._glb_regex_tags = {}

        self.markupString1 = '''\
            OS: IOX

            CMD: SHOW_MRIB_ROUTE
            SHOWCMD: show mrib route
            PREFIX: mrib-route

            ACTUAL:

            (*,224.0.1.39) Flags: S P
              Up: 00:07:16

            (192.168.0.1,224.0.1.39) RPF nbr: 192.168.0.1 Flags:
              Up: 00:07:16
              Incoming Interface List
                Loopback0 Flags: F A, Up: 00:07:16
              Outgoing Interface List
                Loopback0 Flags: F A, Up: 00:07:16
                GigabitEthernet0/2/0/0 Flags: F, Up: 00:07:16
                GigabitEthernet0/2/0/2 Flags: F, Up: 00:07:16

            (*,224.0.1.40) Flags: S P
              Up: 00:07:16
              Outgoing Interface List
                Loopback0 Flags: II LI, Up: 00:07:16
                GigabitEthernet0/2/0/0 Flags: II LI, Up: 00:06:15

            MARKUP:

            (XP<source>X192.168.0.1,XP<group>X224.0.1.39) RPF nbr: Xa<rpf>X192.168.0.1 Flags:
            (Xp<source>X192.168.0.1,Xp<group>X224.0.1.39) RPF nbr: Xa<rpf>X192.168.0.1 Flags:XR<flags>XS P
              Up: XT<uptime>X00:07:16
              Incoming Interface List
                XI<ingress-intf>XLoopback0 Flags: XC<ingress-flags>XF A, Up: XT<ingress-uptime>X00:07:16
              Outgoing Interface List
                XI<egress-intf>XLoopback0 Flags: XC<egress-flags>XF A, Up: XT<egress-uptime>00:07:16

            OS: NXOS

            CMD: SHOW_MRIB_ROUTE
            SHOWCMD: show ip mroute
            PREFIX: mrib-route
            ACTUAL:

            (13.13.13.4/32, 232.0.0.1/32), uptime: 00:00:43, igmp pim ip
              Incoming interface: Ethernet2/1, RPF nbr: 11.11.11.2^M
              Outgoing interface list: (count: 1)^M
                Ethernet2/2, uptime: 00:00:43, igmp^M

            MARKUP:
            (XP<source>X13.13.13.4/32, XP<group>X232.0.0.1/32)
            (Xp<source>X13.13.13.4/32, Xp<group>X232.0.0.1/32), uptime: XT<uptime>X00:00:43
            (Xp<source>X13.13.13.4/32, Xp<group>X232.0.0.1/32), uptime: Xt<uptime>X00:00:43, XR<protos>Xigmp pim ip
              Incoming interface: XI<ingress-intf>XEthernet2/1, RPF nbr: Xa<rpf>X11.11.11.2
              Outgoing interface list: (count: XN<egress-count>X1)
                XI<egress-intf>XEthernet2/2, uptime: XT<egress-uptime>X00:00:43, XR<egress-protos>Xigmp
        '''
        self.showCommandsForMarkupString1 = {
            'iox': {
                'SHOW_MRIB_ROUTE': 'show mrib route',
            },
            'nxos': {
                'SHOW_MRIB_ROUTE': 'show ip mroute',
            },
        }


        self.outputString1 = '''\
            from genie.parsergen import core as pcore
            show_commands = {
                'iox': {
                    'SHOW_MRIB_ROUTE': 'show mrib route',
                },
                'nxos': {
                    'SHOW_MRIB_ROUTE': 'show ip mroute',
                },
            }
            regex = {
                'iox': {
                    #
                    # SHOW_MRIB_ROUTE ('show mrib route')
                    #
                    'mrib-route.source'         : r'\(([A-Fa-f0-9/:\.]+),[A-Fa-f0-9/:\.]+\) RPF nbr:\s+[A-Fa-f0-9:\.]+ Flags:',
                    'mrib-route.group'          : r'\([A-Fa-f0-9/:\.]+,([A-Fa-f0-9/:\.]+)\) RPF nbr:\s+[A-Fa-f0-9:\.]+ Flags:',
                    'mrib-route.flags'          : r'\([A-Fa-f0-9/:\.]+,[A-Fa-f0-9/:\.]+\) RPF nbr:\s+[A-Fa-f0-9:\.]+ Flags:([^\\r\\n]+)',
                    'mrib-route.uptime'         : r'\s+Up:\s+(\d{2}:\d{2}:\d{2})',
                    'mrib-route.ingress-intf'   : r'\s+([-A-Za-z0-9\._/:]+) Flags:\s+[^,]+, Up:\s+\d{2}:\d{2}:\d{2}',
                    'mrib-route.ingress-flags'  : r'\s+[-A-Za-z0-9\._/:]+ Flags:\s+([^,]+), Up:\s+\d{2}:\d{2}:\d{2}',
                    'mrib-route.ingress-uptime' : r'\s+[-A-Za-z0-9\._/:]+ Flags:\s+[^,]+, Up:\s+(\d{2}:\d{2}:\d{2})',
                    'mrib-route.egress-intf'    : r'\s+([-A-Za-z0-9\._/:]+) Flags:\s+[^,]+, Up:\s+XT<egress-uptime>00:07:16',
                    'mrib-route.egress-flags'   : r'\s+[-A-Za-z0-9\._/:]+ Flags:\s+([^,]+), Up:\s+XT<egress-uptime>00:07:16',

                },
                'nxos': {
                    #
                    # SHOW_MRIB_ROUTE ('show ip mroute')
                    #
                    'mrib-route.source'        : r'\(([A-Fa-f0-9/:\.]+),\s+[A-Fa-f0-9/:\.]+\)',
                    'mrib-route.group'         : r'\([A-Fa-f0-9/:\.]+,\s+([A-Fa-f0-9/:\.]+)\)',
                    'mrib-route.uptime'        : r'\([A-Fa-f0-9/:\.]+,\s+[A-Fa-f0-9/:\.]+\), uptime:\s+(\d{2}:\d{2}:\d{2})',
                    'mrib-route.protos'        : r'\([A-Fa-f0-9/:\.]+,\s+[A-Fa-f0-9/:\.]+\), uptime:\s+\d{2}:\d{2}:\d{2},\s+([^\\r\\n]+)',
                    'mrib-route.ingress-intf'  : r'\s+Incoming interface:\s+([-A-Za-z0-9\._/:]+), RPF nbr:\s+[A-Fa-f0-9:\.]+',
                    'mrib-route.egress-count'  : r'\s+Outgoing interface list:\s+\(count:\s+(\d+)\)',
                    'mrib-route.egress-intf'   : r'\s+([-A-Za-z0-9\._/:]+), uptime:\s+\d{2}:\d{2}:\d{2},\s+[^\\r\\n]+',
                    'mrib-route.egress-uptime' : r'\s+[-A-Za-z0-9\._/:]+, uptime:\s+(\d{2}:\d{2}:\d{2}),\s+[^\\r\\n]+',
                    'mrib-route.egress-protos' : r'\s+[-A-Za-z0-9\._/:]+, uptime:\s+\d{2}:\d{2}:\d{2},\s+([^\\r\\n]+)',

                },
            }
            pcore.extend (regex, show_commands)
        '''


        self.noOsExtendString1 = '''\
            from genie.parsergen import core as pcore
            show_commands = {
                'SHOW_MRIB_ROUTE': 'show mrib route',
            }
            regex = {
                #
                # SHOW_MRIB_ROUTE ('show mrib route')
                #
                'mrib-route.source'         : r'\(([A-Fa-f0-9/:\.]+),[A-Fa-f0-9/:\.]+\) RPF nbr:\s+[A-Fa-f0-9:\.]+ Flags:',
                'mrib-route.group'          : r'\([A-Fa-f0-9/:\.]+,([A-Fa-f0-9/:\.]+)\) RPF nbr:\s+[A-Fa-f0-9:\.]+ Flags:',
                'mrib-route.flags'          : r'\([A-Fa-f0-9/:\.]+,[A-Fa-f0-9/:\.]+\) RPF nbr:\s+[A-Fa-f0-9:\.]+ Flags:([^\\r\\n]+)',
                'mrib-route.uptime'         : r'\s+Up:\s+(\d{2}:\d{2}:\d{2})',
                'mrib-route.ingress-intf'   : r'\s+([-A-Za-z0-9\._/:]+) Flags:\s+[^,]+, Up:\s+\d{2}:\d{2}:\d{2}',
                'mrib-route.ingress-flags'  : r'\s+[-A-Za-z0-9\._/:]+ Flags:\s+([^,]+), Up:\s+\d{2}:\d{2}:\d{2}',
                'mrib-route.ingress-uptime' : r'\s+[-A-Za-z0-9\._/:]+ Flags:\s+[^,]+, Up:\s+(\d{2}:\d{2}:\d{2})',
                'mrib-route.egress-intf'    : r'\s+([-A-Za-z0-9\._/:]+) Flags:\s+[^,]+, Up:\s+XT<egress-uptime>00:07:16',
                'mrib-route.egress-flags'   : r'\s+[-A-Za-z0-9\._/:]+ Flags:\s+([^,]+), Up:\s+XT<egress-uptime>00:07:16',

            }
            pcore.extend (regex, show_commands)
        '''


        self.markupString2 = '''\
            SHOWCMD: show bgp summary
            PREFIX: bgp
            OS: IOX

            MARKUP:

            BGP router identifier XA<router-id>X192.168.0.12, local AS number XN<local-as>X100
            BGP generic scan interval XN<gen-scan-interval>X60 secs
            BGP table state: XW<table-state>XActive
            First crazy random line that optionally appears in the output : XN<optional1>X1
            Table ID: XHX0xe0000000   RD version: XXX<\d+><rd-ver>XXX8
            BGP main routing table version XXX<\d+>XXX8
            BGP scan interval XN<scan-interval>X60 secs

            BGP is operating in XW<oper-mode>XSTANDALONE mode.

            Process       RcvTblVer   bRIB/RIB   LabelVer  ImportVer  SendTblVer  StandbyVer
            Speaker               8          8          8          8           8           8

            Neighbor        Spk    AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down  St/PfxRcd
            50.1.0.2          0   100      63      55        8    0    0 00:51:24        100
            50.1.0.3          0   200      63      55        8    0    0 00:40:16        200
        '''

        self.outputString2 = '''\
            from genie.parsergen import core as pcore
            show_commands = {
                'iox': {
                    'SHOW_BGP_SUMMARY': 'show bgp summary',
                },
            }
            regex = {
                'iox': {
                    #
                    # SHOW_BGP_SUMMARY ('show bgp summary')
                    #
                    'bgp.router-id'                      : r'BGP router identifier\s+([A-Fa-f0-9:\.]+), local AS number\s+\d+',
                    'bgp.local-as'                       : r'BGP router identifier\s+[A-Fa-f0-9:\.]+, local AS number\s+(\d+)',
                    'bgp.gen-scan-interval'              : r'BGP generic scan interval\s+(\d+) secs',
                    'bgp.table-state'                    : r'BGP table state:\s+(\w+)',
                    'bgp.optional1'                      : r'First crazy random line that optionally appears in the output\s+:\s+(\d+)',
                    'bgp.table-id'                       : r'Table ID:\s+((?:0x)?[a-fA-F0-9]+)   RD version:\s+\d+',
                    'bgp.rd-ver'                         : r'Table ID:\s+(?:0x)?[a-fA-F0-9]+   RD version:\s+(\d+)',
                    'bgp.bgp-main-routing-table-version' : r'BGP main routing table version\s+(\d+)',
                    'bgp.scan-interval'                  : r'BGP scan interval\s+(\d+) secs',
                    'bgp.oper-mode'                      : r'BGP is operating in\s+(\w+) mode.',

                },
            }
            pcore.extend (regex, show_commands)
        '''

        self.markupString3 = '''\
            OS: IOX

            CMD: show_interface_<WORD>

            PREFIX: show.intf

            SHOWCMD: show interface {ifname}

            ACTUAL:
            show interface MgmtEth0/0/CPU0/0
            Fri Mar  6 12:03:11.409 EST
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
              Last input 00:00:00, output 00:00:48
              Last clearing of "show interface" counters never
              5 minute input rate 79000 bits/sec, 32 packets/sec
              5 minute output rate 0 bits/sec, 0 packets/sec
                 2459211 packets input, 774707935 bytes, 0 total input drops
                 0 drops for unrecognized upper-level protocol
                 Received 2216135 broadcast packets, 233738 multicast packets
                          0 runts, 0 giants, 0 throttles, 0 parity
                 0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored, 0 abort
                 349 packets output, 58930 bytes, 0 total output drops
                 Output 4 broadcast packets, 0 multicast packets
                 0 output errors, 0 underruns, 0 applique, 0 resets
                 0 output buffer failures, 0 output buffers swapped out
                 1 carrier transitions


            MARKUP:
            show interface MgmtEth0/0/CPU0/0
            Fri Mar  6 12:03:11.409 EST
            MgmtEth0/0/CPU0/0 is XW<admin_state>Xup, line protocol is XW<line_protocol>Xup 
              Interface state transitions: 1
              Hardware is XXX<[^,]+>XXXManagement Ethernet, address is XA<mac_address>X5254.00d6.36c9 (bia 5254.00d6.36c9)
              Internet address is XA<ip_address>X10.30.108.132/23
              MTU XNX1514 bytes, BW XNX0 Kbit
                 reliability 255/255, txload Unknown, rxload Unknown
              Encapsulation XW<encap>ARPA,
              Duplex unknown, 0Kb/s, unknown, link type is XW<link_type>Xautonegotiation
              output flow control is XW<output_flowcontrol>Xoff, input flow control is XW<input_flowcontrol>Xoff
              Carrier delay (up) is XN<carrier_delay_up>X10 msec
              loopback XXX<[^,]+><loopback_status>XXXnot set,
              ARP type ARPA, ARP timeout 04:00:00
              Last input 00:00:00, output 00:00:48
              Last clearing of "show interface" counters XR<last_clear_counter>Xnever
              5 minute input rate XN<input_rate_bits>X79000 bits/sec, XN<input_rate>X32 packets/sec
              5 minute output rate XN<output_rate_bits>X0 bits/sec, XN<output_rate>X0 packets/sec
                 XN<input_pkts>X2459211 packets input, XN<input_bytes>X774707935 bytes, XN<input_total_drops>X0 total input drops
                 XN<drops_unrec_upper_level_proto>X0 drops for unrecognized upper-level protocol
                 Received XN<broadcasts>X2216135 broadcast packets, XN<multicasts>X233738 multicast packets
                          XNX0 runts, XNX0 giants, XNX0 throttles, XNX0 parity
                 XNX0 input errors, XNX0 CRC, XNX0 frame, XNX0 overrun, XNX0 ignored, XNX0 abort
                 XN<output_pkts>X349 packets output, XN<output_bytes>X58930 bytes, XN<output_total_drops>X0 total output drops
                 Output XN<output_broadcast>X4 broadcast packets, XN<output_multicast>X0 multicast packets
                 XNX0 output errors, XN<output_underruns>X0 underruns, XN<output_applique>X0 applique, XN<output_resets>X0 resets
                 XN<output_buf_failures>X0 output buffer failures, XN<output_buf_swapped>X0 output buffers swapped out
                 XN<carrier_trans>X1 carrier transitions
        '''

        self.outputString3 = '''\
            from genie.parsergen import core as pcore
            show_commands = {
                'iox': {
                    'show_interface_<WORD>': 'show interface {ifname}',
                },
            }
            regex = {
                'iox': {
                    #
                    # show_interface_<WORD> ('show interface {ifname}')
                    #
                    'show.intf.admin_state'                   : r'MgmtEth0/0/CPU0/0 is\s+(\w+), line protocol is\s+\w+\s+',
                    'show.intf.line_protocol'                 : r'MgmtEth0/0/CPU0/0 is\s+\w+, line protocol is\s+(\w+)\s+',
                    'show.intf.hardware'                      : r'\s+Hardware is\s+([^,]+), address is\s+[A-Fa-f0-9:\.]+ \(bia 5254.00d6.36c9\)',
                    'show.intf.mac_address'                   : r'\s+Hardware is\s+[^,]+, address is\s+([A-Fa-f0-9:\.]+) \(bia 5254.00d6.36c9\)',
                    'show.intf.ip_address'                    : r'\s+Internet address is\s+([A-Fa-f0-9:\.]+)/23',
                    'show.intf.mtu'                           : r'\s+MTU\s+(\d+) bytes, BW\s+\d+ Kbit',
                    'show.intf.bw'                            : r'\s+MTU\s+\d+ bytes, BW\s+(\d+) Kbit',
                    'show.intf.link_type'                     : r'\s+Duplex unknown, 0Kb/s, unknown, link type is\s+(\w+)',
                    'show.intf.output_flowcontrol'            : r'\s+output flow control is\s+(\w+), input flow control is\s+\w+',
                    'show.intf.input_flowcontrol'             : r'\s+output flow control is\s+\w+, input flow control is\s+(\w+)',
                    'show.intf.carrier_delay_up'              : r'\s+Carrier delay \(up\) is\s+(\d+) msec',
                    'show.intf.loopback_status'               : r'\s+loopback\s+([^,]+),',
                    'show.intf.last_clear_counter'            : r'\s+Last clearing of "show interface" counters\s+([^\\r\\n]+)',
                    'show.intf.input_rate_bits'               : r'\s+5 minute input rate\s+(\d+) bits/sec,\s+\d+ packets/sec',
                    'show.intf.input_rate'                    : r'\s+5 minute input rate\s+\d+ bits/sec,\s+(\d+) packets/sec',
                    'show.intf.output_rate_bits'              : r'\s+5 minute output rate\s+(\d+) bits/sec,\s+\d+ packets/sec',
                    'show.intf.output_rate'                   : r'\s+5 minute output rate\s+\d+ bits/sec,\s+(\d+) packets/sec',
                    'show.intf.input_pkts'                    : r'\s+(\d+) packets input,\s+\d+ bytes,\s+\d+ total input drops',
                    'show.intf.input_bytes'                   : r'\s+\d+ packets input,\s+(\d+) bytes,\s+\d+ total input drops',
                    'show.intf.input_total_drops'             : r'\s+\d+ packets input,\s+\d+ bytes,\s+(\d+) total input drops',
                    'show.intf.drops_unrec_upper_level_proto' : r'\s+(\d+) drops for unrecognized upper-level protocol',
                    'show.intf.broadcasts'                    : r'\s+Received\s+(\d+) broadcast packets,\s+\d+ multicast packets',
                    'show.intf.multicasts'                    : r'\s+Received\s+\d+ broadcast packets,\s+(\d+) multicast packets',
                    'show.intf.runts'                         : r'\s+(\d+) runts,\s+\d+ giants,\s+\d+ throttles,\s+\d+ parity',
                    'show.intf.giants'                        : r'\s+\d+ runts,\s+(\d+) giants,\s+\d+ throttles,\s+\d+ parity',
                    'show.intf.throttles'                     : r'\s+\d+ runts,\s+\d+ giants,\s+(\d+) throttles,\s+\d+ parity',
                    'show.intf.parity'                        : r'\s+\d+ runts,\s+\d+ giants,\s+\d+ throttles,\s+(\d+) parity',
                    'show.intf.input_errors'                  : r'\s+(\d+) input errors,\s+\d+ CRC,\s+\d+ frame,\s+\d+ overrun,\s+\d+ ignored,\s+\d+ abort',
                    'show.intf.crc'                           : r'\s+\d+ input errors,\s+(\d+) CRC,\s+\d+ frame,\s+\d+ overrun,\s+\d+ ignored,\s+\d+ abort',
                    'show.intf.frame'                         : r'\s+\d+ input errors,\s+\d+ CRC,\s+(\d+) frame,\s+\d+ overrun,\s+\d+ ignored,\s+\d+ abort',
                    'show.intf.overrun'                       : r'\s+\d+ input errors,\s+\d+ CRC,\s+\d+ frame,\s+(\d+) overrun,\s+\d+ ignored,\s+\d+ abort',
                    'show.intf.ignored'                       : r'\s+\d+ input errors,\s+\d+ CRC,\s+\d+ frame,\s+\d+ overrun,\s+(\d+) ignored,\s+\d+ abort',
                    'show.intf.abort'                         : r'\s+\d+ input errors,\s+\d+ CRC,\s+\d+ frame,\s+\d+ overrun,\s+\d+ ignored,\s+(\d+) abort',
                    'show.intf.output_pkts'                   : r'\s+(\d+) packets output,\s+\d+ bytes,\s+\d+ total output drops',
                    'show.intf.output_bytes'                  : r'\s+\d+ packets output,\s+(\d+) bytes,\s+\d+ total output drops',
                    'show.intf.output_total_drops'            : r'\s+\d+ packets output,\s+\d+ bytes,\s+(\d+) total output drops',
                    'show.intf.output_broadcast'              : r'\s+Output\s+(\d+) broadcast packets,\s+\d+ multicast packets',
                    'show.intf.output_multicast'              : r'\s+Output\s+\d+ broadcast packets,\s+(\d+) multicast packets',
                    'show.intf.output_errors'                 : r'\s+(\d+) output errors,\s+\d+ underruns,\s+\d+ applique,\s+\d+ resets',
                    'show.intf.output_underruns'              : r'\s+\d+ output errors,\s+(\d+) underruns,\s+\d+ applique,\s+\d+ resets',
                    'show.intf.output_applique'               : r'\s+\d+ output errors,\s+\d+ underruns,\s+(\d+) applique,\s+\d+ resets',
                    'show.intf.output_resets'                 : r'\s+\d+ output errors,\s+\d+ underruns,\s+\d+ applique,\s+(\d+) resets',
                    'show.intf.output_buf_failures'           : r'\s+(\d+) output buffer failures,\s+\d+ output buffers swapped out',
                    'show.intf.output_buf_swapped'            : r'\s+\d+ output buffer failures,\s+(\d+) output buffers swapped out',
                    'show.intf.carrier_trans'                 : r'\s+(\d+) carrier transitions',

                },
            }
            pcore.extend (regex, show_commands)
        '''

        self.outputString4 = '''\
            regex_tags = {
                'iox': [
                    #
                    # SHOW_MRIB_ROUTE ('show mrib route')
                    #
                    'mrib-route.source'         ,
                    'mrib-route.group'          ,
                    'mrib-route.flags'          ,
                    'mrib-route.uptime'         ,
                    'mrib-route.ingress-intf'   ,
                    'mrib-route.ingress-flags'  ,
                    'mrib-route.ingress-uptime' ,
                    'mrib-route.egress-intf'    ,
                    'mrib-route.egress-flags'   ,

                ],
                'nxos': [
                    #
                    # SHOW_MRIB_ROUTE ('show ip mroute')
                    #
                    'mrib-route.source'        ,
                    'mrib-route.group'         ,
                    'mrib-route.uptime'        ,
                    'mrib-route.protos'        ,
                    'mrib-route.ingress-intf'  ,
                    'mrib-route.egress-count'  ,
                    'mrib-route.egress-intf'   ,
                    'mrib-route.egress-uptime' ,
                    'mrib-route.egress-protos' ,

                ],
            }
            pcore.extend (regex, show_commands, regex_tags)'''


        self.showCommandOutput2 = '''\
            (*,224.0.1.39) Flags: S P
              Up: 00:07:16

            (192.168.0.a,224.0.1.39) RPF nbr: 192.168.0.1 Flags:
              Up: 00:07:16
              Incoming Interface List
                Loopback0 Flags: F A, Up: 00:07:16
              Outgoing Interface List
                Loopback0 Flags: F A, Up: 00:07:16
                GigabitEthernet0/2/0/0 Flags: F, Up: 00:07:16
                GigabitEthernet0/2/0/2 Flags: F, Up: 00:07:16

            (*,224.0.1.40) Flags: S P
              Up: 00:07:16
              Outgoing Interface List
                Loopback0 Flags: II LI, Up: 00:07:16
                GigabitEthernet0/2/0/0 Flags: II LI, Up: 00:06:15
        '''


        self.outputTuple1 = (True, {'bgp.rd-ver': True, 'bgp.router-id': True, 'bgp.scan-interval': True, 'bgp.oper-mode': True, 'bgp.local-as': True, 'bgp.table-state': True, 'bgp.bgp-main-routing-table-version': True, 'bgp.gen-scan-interval': True, 'bgp.table-id': True}, ''        )

        self.outputTuple2 = (False, {'bgp.scan-interval': {'line': 5, 'value': '60'}, 'bgp.table-state': True, 'bgp.rd-ver': True, 'bgp.router-id': True, 'bgp.gen-scan-interval': True, 'bgp.table-id': True, 'bgp.bgp-main-routing-table-version': True, 'bgp.local-as': True}, '')

        self.outputDict1 = {'bgp.table-state': 'Active', 'bgp.router-id': '192.168.0.12', 'bgp.oper-mode': 'STANDALONE', 'bgp.local-as': '100', 'bgp.table-id': '0xe0000000', 'bgp.scan-interval': '60', 'bgp.bgp-main-routing-table-version': '8', 'bgp.gen-scan-interval': '60', 'bgp.rd-ver': '8'}

        self.outputDict2 = {'bgp.table-state': 'Active', 'bgp.router-id': '192.168.0.12', 'bgp.local-as': '100', 'bgp.table-id': '0xe0000000', 'bgp.scan-interval': '60', 'bgp.bgp-main-routing-table-version': '8', 'bgp.gen-scan-interval': '60', 'bgp.rd-ver': '8'}

        self.outputDict3 = {'mrib-route.source': '192.168.0.a', 'mrib-route.group': '224.0.1.39'}

        self.subText1 = "                    'mrib-route.source'         : [r'\\(([0-9/:\\.]+),[0-9/:\\.]+\\) RPF nbr: +[A-Fa-f0-9:\\.]+ Flags:', r'\\(([A-Fa-f0-9/:\\.]+),[A-Fa-f0-9/:\\.]+\\) RPF nbr: +[A-Fa-f0-9:\\.]+ Flags:'],"

        self.subText2 = "                    'mrib-route.source'         : [r'\\(([0-9/:\\.]+),[0-9/:\\.]+\\) RPF nbr: +[A-Fa-f0-9:\\.]+ Flags:', r'\\(([A-Fb-f0-9/:\\.]+),[A-Fa-f0-9/:\\.]+\\) RPF nbr: +[A-Fa-f0-9:\\.]+ Flags:'],"

    def mkpg_section_order_helper(self, cmd_to_move):
        '''Test various markup subcommands as a way to exit from markup mode.
           The subcommand is repeated in the altered command string, this is OK
        '''
        anchor_phrase = 'OS: NXOS'
        cmd=re.sub(anchor_phrase, cmd_to_move+
            '\n            '+anchor_phrase , self.markupString1)
        generated_text = mkpg(dedent(cmd))
        expected_text = dedent(self.outputString1)
        self.assertEqual(generated_text, expected_text)

    def test_mk_parsergen_output1 (self):
        ''' Test the auto-generation of show command and regular expression
            content from marked-up input text.
            This content serves as the input to the parsergen.extend API.
        '''

        self.maxDiff = None
        generated_text = mkpg(dedent(self.markupString1))
        expected_text = dedent(self.outputString1)
        self.assertEqual(generated_text, expected_text)


    def test_mk_parsergen_output2 (self):
        ''' Test mkpg while mixing around the order of the sections.
        '''

        self.maxDiff = None

        #
        # Mix around the order of the sections terminating a MARKUP
        # section, ensure consistent output is seen.
        #
        self.mkpg_section_order_helper('CMD: SHOW_MRIB_ROUTE')
        self.mkpg_section_order_helper('SHOWCMD: show ip mroute')
        self.mkpg_section_order_helper('PREFIX: mrib-route')


    def test_mk_parsergen_output3 (self):
        ''' Test mkpg while generating regex tags ordered list.
        '''
        generated_text = mkpg(dedent(self.markupString1),
            generate_regex_tags=True)
        expected_text = dedent(
            re.sub('.*pcore\.extend.*', self.outputString4,
                self.outputString1))
        self.assertEqual(generated_text, expected_text)


    def test_mk_parsergen_output4 (self):
        ''' Test mkpg against "show bgp summary".
        '''

        generated_text = mkpg(dedent(self.markupString2))
        expected_text = dedent(self.outputString2)
        self.assertEqual(generated_text, expected_text)


    def test_mk_parsergen_output5 (self):
        ''' Test mkpg autogeneration of unspecified regex keys based on
            forward search of text after the matching block.
        '''
        generated_text = \
            mkpg(dedent(self.markupString3), auto_key_join_char='_')
        expected_text = dedent(self.outputString3)
        self.assertEqual(generated_text, expected_text)


    def test_mk_parsergen_output6 (self):
        ''' Test that the leading text "address is" is auto-formed into the
            regex tag "address".
        '''
        generated_text = mkpg(dedent(
            re.sub('<mac_address>', '', self.markupString3)),
                auto_key_join_char='_')
        expected_text = re.sub("mac_address'", "address'    ",
            dedent(self.outputString3))
        self.assertEqual(generated_text, expected_text)


    def test_mk_parsergen_output6 (self):
        ''' Test that the leading text "input flow control is" and
            "output flow control is" are auto-formed into the
            expected regex tags when they are not specified in the marked-up
            input text.
        '''
        markup_text = re.sub('<output_flowcontrol>', '',
                self.markupString3)
        markup_text = re.sub('<input_flowcontrol>', '', markup_text)
        generated_text = mkpg(dedent(markup_text), auto_key_join_char='_')
        expected_text = re.sub("output_flowcontrol' ", "output_flow_control'",
            dedent(self.outputString3))
        expected_text = re.sub("input_flowcontrol' ", "input_flow_control'",
            expected_text)
        self.assertEqual(generated_text, expected_text)


    def test_parser_gen_1(self):
        ''' Test the parsing of non-tabular "show" command output.
        '''

        parse_key = 'rtr1'
        extend_markup(dedent(self.markupString2))
        core.text_to_parse[parse_key] = dedent(showCommandOutput1)

        tags_to_parse =     [
                             'bgp.local-as',                       (100,101),
                             'bgp.router-id',                      None,
                             'bgp.gen-scan-interval',              None,
                             'bgp.table-state',                    None,
                             'bgp.table-id',                       None,
                             'bgp.rd-ver',                         None,
                             'bgp.bgp-main-routing-table-version', None,
                             'bgp.scan-interval',                  None,
                             'bgp.oper-mode',                      None]

        pg = _parser_gen_t('IOX', tags_to_parse[::2], tags_to_parse[1::2],
                            fill = True, parse_key=parse_key)
        self.assertEqual(self.outputTuple1, pg._parser_validate())
        self.assertEqual(self.outputDict1, core.ext_dictio[parse_key])


    def test_parser_gen_1_with_leading_spaces(self):
        ''' Test the parsing of non-tabular "show" command output.
            Test the parse fails when extra spaces are inserted at the
            start of the router's output.
        '''

        parse_key = 'rtr1'
        extend_markup(dedent(self.markupString2))
        core.text_to_parse[parse_key] = "  " + dedent(showCommandOutput1)

        tags_to_parse =     [
                             'bgp.local-as',                       (100,101),
                             'bgp.router-id',                      None,
                             'bgp.gen-scan-interval',              None,
                             'bgp.table-state',                    None,
                             'bgp.table-id',                       None,
                             'bgp.rd-ver',                         None,
                             'bgp.bgp-main-routing-table-version', None,
                             'bgp.scan-interval',                  None,
                             'bgp.oper-mode',                      None]

        pg = _parser_gen_t('IOX', tags_to_parse[::2], tags_to_parse[1::2],
                            fill = True, parse_key=parse_key)
        (validate, dictio, msg) = pg._parser_validate()
        self.assertFalse(validate, "Parse did not fail as expected.")


    def test_parser_gen_2(self):
        ''' Ensure parser succeeds if output does not contain optional regex
            key, but the "skip" option is on.
        '''
        parse_key = 'rtr1'
        extend_markup(dedent(self.markupString2))
        core.text_to_parse[parse_key] = dedent(showCommandOutput1)
        tags_to_parse =     [
                             'bgp.local-as',                       (100,101),
                             'bgp.router-id',                      None,
                             'bgp.gen-scan-interval',              None,
                             'bgp.table-state',                    None,
                             'bgp.optional1',                      None,
                             'bgp.table-id',                       None,
                             'bgp.rd-ver',                         None,
                             'bgp.bgp-main-routing-table-version', None,
                             'bgp.scan-interval',                  None,
                             'bgp.oper-mode',                      None]

        pg = _parser_gen_t('IOX', tags_to_parse[::2], tags_to_parse[1::2],
                            fill = True, parse_key=parse_key, skip=True)
        self.assertEqual(self.outputTuple1, pg._parser_validate())
        self.assertEqual(self.outputDict1, core.ext_dictio[parse_key])

    def test_parser_gen_3(self):
        ''' Ensure parser does not modify attributes and values input lists.
            This is to preserve legacy functionality where separate
            lists are used.
        '''
        parse_key = 'rtr1'
        extend_markup(dedent(self.markupString2))
        core.text_to_parse[parse_key] = dedent(showCommandOutput1)
        tags_to_parse =     [
                             'bgp.local-as',                       (100,101),
                             'bgp.router-id',                      None,
                             'bgp.gen-scan-interval',              None,
                             'bgp.table-state',                    None,
                             'bgp.optional1',                      None,
                             'bgp.table-id',                       None,
                             'bgp.rd-ver',                         None,
                             'bgp.bgp-main-routing-table-version', None,
                             'bgp.scan-interval',                  None,
                             'bgp.oper-mode',                      None]
        attributes = tags_to_parse[::2]
        values = tags_to_parse[1::2]
        original_attributes = attributes[:]
        original_values = values[:]
        pg = _parser_gen_t('IOX', attributes, values,
                            fill = True, parse_key=parse_key, skip=True)
        self.assertEqual(attributes, original_attributes)
        self.assertEqual(values, original_values)


    def test_parser_gen_4(self):
        ''' Ensure parser succeeds if output contains optional regex
            key, but the "skip" option is on.
        '''
        parse_key = 'rtr1'
        extend_markup(dedent(self.markupString2))
        core.text_to_parse[parse_key] = dedent(showCommandOutput1)
        tags_to_parse =     [
                             'bgp.local-as',                       (100,101),
                             'bgp.router-id',                      None,
                             'bgp.gen-scan-interval',              None,
                             'bgp.table-state',                    None,
                             'bgp.optional1',                      None,
                             'bgp.table-id',                       None,
                             'bgp.rd-ver',                         None,
                             'bgp.bgp-main-routing-table-version', None,
                             'bgp.scan-interval',                  None,
                             'bgp.oper-mode',                      None]

        attributes = tags_to_parse[::2]
        values = tags_to_parse[1::2]
        original_attributes = attributes[:]
        original_values = values[:]

        core.text_to_parse[parse_key] = re.sub(
            'Table ID:',
            'First crazy random line that optionally appears in the output : 8675309\nTable ID:',
            core.text_to_parse[parse_key])

        pg = _parser_gen_t('IOX', attributes, values,
                            fill = True, parse_key=parse_key, skip=True)

        expectedValidateDict = copy.deepcopy(self.outputTuple1)
        expectedValidateDict[1]['bgp.optional1'] = True
        expectedOutputDict   = copy.deepcopy(self.outputDict1)
        expectedOutputDict['bgp.optional1'] = '8675309'

        self.assertEqual(expectedValidateDict, pg._parser_validate())
        self.assertEqual(expectedOutputDict, core.ext_dictio[parse_key])

        self.assertEqual(attributes, original_attributes)
        self.assertEqual(values, original_values)


    def test_parser_gen_5(self):
        ''' Test that a fill operation aborts if the first tag is not filled.
        '''
        parse_key = 'rtr1'
        core.text_to_parse[parse_key] = dedent(showCommandOutput1)

        tags_to_parse =     [
                             'bgp.local-as',                       None,
                            'bgp.router-id',                      '192.168.0.12',
                             'bgp.gen-scan-interval',              None,
                             'bgp.table-state',                    None,
                             'bgp.table-id',                       None,
                             'bgp.rd-ver',                         None,
                             'bgp.bgp-main-routing-table-version', None,
                             'bgp.scan-interval',                  None,
                             'bgp.oper-mode',                      None]
        self.assertRaises(AssertionError,
            _parser_gen_t, 'IOX', tags_to_parse[::2], tags_to_parse[1::2],
                            fill = True, parse_key=parse_key)


    def test_parser_gen_6(self):
        ''' Test that ParserGen stops parsing when a comparison fails,
            ensure the BGP operational mode is not parsed.
        '''
        parse_key = 'rtr1'
        extend_markup(dedent(self.markupString2))
        core.text_to_parse[parse_key] = dedent(showCommandOutput1)
        tags_to_compare =   [
                         'bgp.local-as',                       (102,101,100),
                         'bgp.router-id',                      '192.168.0.12',
                         'bgp.gen-scan-interval',              60,
                         'bgp.table-state',                    'Active',
                         'bgp.table-id',                       '0xe0000000',
                         'bgp.rd-ver',                         '8',
                         'bgp.bgp-main-routing-table-version', '8',
                         'bgp.scan-interval',                  50,
                         'bgp.oper-mode',                      'STANDALONE']

        pg = _parser_gen_t('IOX', tags_to_compare[::2], tags_to_compare[1::2],
                            fill = False, parse_key=parse_key)
        self.assertEqual(self.outputTuple2, pg._parser_validate())
        self.assertEqual(self.outputDict2, core.ext_dictio[parse_key])


    def test_parser_gen_7(self):
        '''
        '''
        core._glb_regex={}
        core._glb_regex_tags={}
        core._glb_show_commands={}
        tags_to_parse =     [
                             'mrib-route.source',     '192.168.0.a',
                             'mrib-route.group',      None,
                            ]
        parse_key = 'rtr2'
        core.text_to_parse[parse_key] = dedent(self.showCommandOutput2)
        extend_markup(dedent(self.markupString1))
        pg = _parser_gen_t('IOX', tags_to_parse[::2], tags_to_parse[1::2],
                            fill = True, parse_key=parse_key)
        self.assertEqual(self.outputDict3, core.ext_dictio[parse_key])


    def test_parser_gen_8(self):
        ''' Test that we can register show commands without needing to
            register regexes (the tabular parser may also wanto to take
            advantage of the show command formatting logic offered by
            core._get_show_command).
        '''
        core._glb_regex={}
        core._glb_regex_tags={}
        core._glb_show_commands={}

        core.extend(None, self.showCommandsForMarkupString1)

        #
        # Given generic tag, pull out appropriate command.
        #
        self.assertEqual(core._get_show_command('iox', \
            'SHOW_MRIB_ROUTE'), 'show mrib route')

        self.assertEqual(core._get_show_command('nxos', \
            'SHOW_MRIB_ROUTE'), 'show ip mroute')

        self.assertEqual(core._get_show_command('iox', \
            'show mrib route'), 'show mrib route')

        if python3:
            self.assertRaises(TypeError,
                core._get_show_command, 'iox', 1)
        else:
            self.assertRaises(AttributeError,
                core._get_show_command, 'iox', 1)

    def test_parser_gen_9(self):
        ''' Test legacy mode where the regexes are not indexed by OS type.
        '''
        tags_to_parse =     [
                             'mrib-route.source',     '192.168.0.a',
                             'mrib-route.group',      None,
                            ]

        core._glb_regex={}
        core._glb_regex_tags={}
        core._glb_show_commands={}
        parse_key = 'rtr3'
        core.text_to_parse[parse_key] = dedent(self.showCommandOutput2)
        exec(dedent(self.noOsExtendString1))
        pg = _parser_gen_t('IOX', tags_to_parse[::2], tags_to_parse[1::2],
                            fill = True, parse_key=parse_key)
        self.assertEqual(self.outputDict3, core.ext_dictio[parse_key])

        #
        # Given generic tag, pull out appropriate command.
        #
        self.assertEqual(core._get_show_command('iox', \
            'SHOW_MRIB_ROUTE'), 'show mrib route')

        self.assertEqual(core._get_show_command('iox', \
            'show mrib route'), 'show mrib route')

        if python3:
            self.assertRaises(TypeError,
                core._get_show_command, 'iox', 1)
        else:
            self.assertRaises(AttributeError,
                core._get_show_command, 'iox', 1)


    def test_parser_gen_10(self):
        ''' Test legacy indexing mode (where CLI commands are indexed by
            an integer instead of a string).
        '''
        parse_key = 'rtr4'
        cmd=re.sub('CMD: SHOW_MRIB_ROUTE', 'CMD: 1', self.markupString1)
        core._glb_regex={}
        core._glb_regex_tags={}
        core._glb_show_commands={}
        extend_markup(dedent(cmd))
        core._glb_show_commands['iox'] = {1: 'show mrib route'}
        self.assertEqual(core._get_show_command('iox', 1),
                         'show mrib route')

    def test_parser_gen_11(self):
        ''' Test passing positional argument to show command format string.
        '''
        parse_key = 'rtr4'
        cmd=re.sub(
          'SHOWCMD: show mrib route','SHOWCMD: blart command {=default} stuff',
          self.markupString1)
        core._glb_regex={}
        core._glb_regex_tags={}
        core._glb_show_commands={}
        extend_markup(dedent(cmd))
        self.assertEqual(
            core._get_show_command('iox', ('SHOW_MRIB_ROUTE', 'blort')),
                         'blart command blort stuff')
        self.assertEqual(
            core._get_show_command('iox', 'SHOW_MRIB_ROUTE'),
                         'blart command default stuff')

    def test_parser_gen_12(self):
        ''' Test passing keyword argument to show command format string.
        '''
        cmd=re.sub(
          'SHOWCMD: show mrib route',
          'SHOWCMD: blart command {myfield=default} stuff',
          self.markupString1)
        core._glb_regex={}
        core._glb_regex_tags={}
        core._glb_show_commands={}
        extend_markup(dedent(cmd))
        self.assertEqual(
            core._get_show_command('iox', ('SHOW_MRIB_ROUTE', 'blort')),
                         'blart command default stuff')
        self.assertEqual(
            core._get_show_command('iox',
                ('SHOW_MRIB_ROUTE', [], {'myfield':'blort'})),
                         'blart command blort stuff')
        self.assertEqual(
            core._get_show_command('iox', 'SHOW_MRIB_ROUTE'),
                         'blart command default stuff')


    def test_parser_gen_13(self):
        ''' Exercise the mode that allows more than one regular expression
            for a given regex tag, this is intended to allow support for
            multiple releases.  In this example, check first for an IPv4
            address, and then for an IPv6 address

            NOTE: _mk_parser_gen_t does not support multi-regex output.
        '''
        parse_key = 'rtr5'
        tags_to_parse =   [
                           'mrib-route.source',('192.168.0.1', '192.168.0.a'),
                           'mrib-route.group', None,
                          ]
        core._glb_regex={}
        core._glb_regex_tags={}
        core._glb_show_commands={}
        core.text_to_parse[parse_key] = dedent(self.showCommandOutput2)
        cmd = re.sub(r'.*mrib-route.source.*RPF.*', self.subText1,
                     self.outputString1)
        exec(dedent(cmd))
        pg = _parser_gen_t('IOX', tags_to_parse[::2], tags_to_parse[1::2],
                            fill = True, parse_key=parse_key)
        self.assertEqual(self.outputDict3, core.ext_dictio[parse_key])

    def test_parser_gen_14(self):
        ''' Verify that no match is found when neither of the regular
            expressions associated with the tag match the pattern.
        '''
        parse_key = 'rtr5'
        core._glb_regex={}
        core._glb_regex_tags={}
        core._glb_show_commands={}
        tags_to_parse =   [
                           'mrib-route.source',('192.168.0.1', '192.168.0.a'),
                           'mrib-route.group', None,
                          ]
        core.text_to_parse[parse_key] = dedent(self.showCommandOutput2)
        cmd = re.sub(r'.*mrib-route.source.*RPF.*', self.subText2,
                     self.outputString1)
        exec(dedent(cmd))
        pg = _parser_gen_t('IOX', tags_to_parse[::2], tags_to_parse[1::2],
                            fill = True, parse_key=parse_key)
        self.assertEqual({}, core.ext_dictio[parse_key])



class TestTabularParser(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.outputDict1 = \
            {'50.1.0.2': {'100': {'as': '100',
                                  'in_q': '0',
                                  'msg_rcvd': '63',
                                  'msg_sent': '55',
                                  'neighbor': '50.1.0.2',
                                  'out_q': '0',
                                  'prefixes': '100',
                                  'spk': '0',
                                  'tbl_ver': '8',
                                  'time': '00:51:24'}},
             '50.1.0.3': {'200': {'as': '200',
                                  'in_q': '0',
                                  'msg_rcvd': '63',
                                  'msg_sent': '55',
                                  'neighbor': '50.1.0.3',
                                  'out_q': '0',
                                  'prefixes': '200',
                                  'spk': '0',
                                  'tbl_ver': '8',
                                  'time': '00:40:16'}}}

        self.outputDict2 = \
            {1: {'iox.00-00': {'ATT/P/OL': [0, 0, 0],
                               'LSP Checksum': 63997,
                               'LSP Holdtime': '1003',
                               'LSP Seq Num': 8,
                               'LSPID': 'iox.00-00'},
                 'ioxbfd.00-00': {'ATT/P/OL': [0, 0, 0],
                                  'LSP Checksum': 36662,
                                  'LSP Holdtime': '862',
                                  'LSP Seq Num': 4,
                                  'LSPID': 'ioxbfd.00-00'}},
             2: {'iox.00-00': {'ATT/P/OL': [0, 0, 0],
                               'LSP Checksum': 13594,
                               'LSP Holdtime': '1003',
                               'LSP Seq Num': 9,
                               'LSPID': 'iox.00-00'},
                 'iox.01-00': {'ATT/P/OL': [0, 0, 0],
                               'LSP Checksum': 3757,
                               'LSP Holdtime': '922',
                               'LSP Seq Num': 2,
                               'LSPID': 'iox.01-00'}}}


        self.outputDict3 = \
            {'asav951-201.tar.gz': {
                'NAME': 'asav951-201.tar.gz'},
             'isrv-universalk9.16.03.01.tar.gz': {
                'NAME': 'isrv-universalk9.16.03.01.tar.gz'},
             'ubuntu-14.04.3-server-amd64-disk1.tar.gz': {
                'NAME': 'ubuntu-14.04.3-server-amd64-disk1.tar.gz'}}

        self.outputDict4= \
          {'F0/FC0': {'Card Type': 'NCS-F-FC',
            'Location': 'F0/FC0',
            'Power Allocated Watts': '440',
            'Power Used Watts': '291',
            'Status': 'ON'}}

        self.outputDict5={'0/FC0/0': {'0': {'Admin /Oper': 'UP/UP',
                             'Asic State ': 'NRML',
                             'Asic class': 'FE1600',
                             'Asic inst. (R/S/A)': '0/FC0/0',
                             'Asic type': 's13',
                             'DC ': '0',
                             'Fgid DL': 'DONE',
                             'HP ': '1',
                             'HR (#)': '0',
                             'Last init': 'PON',
                             'PON (#)': '1',
                             'card pwrd': 'UP',
                             'plane /grp': '0/0'}},
           '0/FC0/1': {'0': {'Admin /Oper': 'UP/UP',
                             'Asic State ': 'NRML',
                             'Asic class': 'FE1600',
                             'Asic inst. (R/S/A)': '0/FC0/1',
                             'Asic type': 's13',
                             'DC ': '0',
                             'Fgid DL': 'DONE',
                             'HP ': '1',
                             'HR (#)': '0',
                             'Last init': 'PON',
                             'PON (#)': '1',
                             'card pwrd': 'UP',
                             'plane /grp': '0/1'}},
           '0/FC0/2': {'0': {'Admin /Oper': 'UP/UP',
                             'Asic State ': 'NRML',
                             'Asic class': 'FE1600',
                             'Asic inst. (R/S/A)': '0/FC0/2',
                             'Asic type': 's13',
                             'DC ': '0',
                             'Fgid DL': 'DONE',
                             'HP ': '1',
                             'HR (#)': '0',
                             'Last init': 'PON',
                             'PON (#)': '1',
                             'card pwrd': 'UP',
                             'plane /grp': '0/2'}},
           '0/FC0/3': {'0': {'Admin /Oper': 'UP/UP',
                             'Asic State ': 'NRML',
                             'Asic class': 'FE1600',
                             'Asic inst. (R/S/A)': '0/FC0/3',
                             'Asic type': 's13',
                             'DC ': '0',
                             'Fgid DL': 'DONE',
                             'HP ': '1',
                             'HR (#)': '0',
                             'Last init': 'PON',
                             'PON (#)': '1',
                             'card pwrd': 'UP',
                             'plane /grp': '0/3'}}}

        self.outputDict6={'Rx Ch 10:':
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

        self.outputDict8={'Rx Ch 0:': {'Channel Number.': 'Rx Ch 0:'},
                         'Rx Ch 10:': {'Channel Number.': 'Rx Ch 10:'},
                         'Rx Ch 11:': {'Channel Number.': 'Rx Ch 11:'},
                         'Rx Ch 1:': {'Channel Number.': 'Rx Ch 1:'},
                         'Rx Ch 2:': {'Channel Number.': 'Rx Ch 2:'},
                         'Rx Ch 3:': {'Channel Number.': 'Rx Ch 3:'},
                         'Rx Ch 4:': {'Channel Number.': 'Rx Ch 4:'},
                         'Rx Ch 5:': {'Channel Number.': 'Rx Ch 5:'},
                         'Rx Ch 6:': {'Channel Number.': 'Rx Ch 6:'},
                         'Rx Ch 7:': {'Channel Number.': 'Rx Ch 7:'},
                         'Rx Ch 8:': {'Channel Number.': 'Rx Ch 8:'},
                         'Rx Ch 9:': {'Channel Number.': 'Rx Ch 9:'}}

        self.outputDict9={'ARP': {'84': {'Chars In': '0',
                          'Chars Out': '84',
                          'Pkts In': '0',
                          'Pkts Out': '2',
                          'Protocol': 'ARP'}},
           'IPV6_ND': {'1920': {'Chars In': '0',
                                'Chars Out': '1920',
                                'Pkts In': '0',
                                'Pkts Out': '25',
                                'Protocol': 'IPV6_ND'}}}

        self.outputDict10={'TenGigE0/0/0/0': {'ARP': {'Chars In': '0',
                                                      'Chars Out': '84',
                                                      'Pkts In': '0',
                                                      'Pkts Out': '2',
                                                      'Protocol': 'ARP'},
                                              'IPV6_ND': {'Chars In': '0',
                                                          'Chars Out': '1920',
                                                          'Pkts In': '0',
                                                          'Pkts Out': '25',
                                                          'Protocol': 'IPV6_ND'}},
                           'TenGigE0/0/0/1': {'ARP': {'Chars In': '0',
                                                      'Chars Out': '84',
                                                      'Pkts In': '0',
                                                      'Pkts Out': '2',
                                                      'Protocol': 'ARP'},
                                              'IPV6_ND': {'Chars In': '0',
                                                          'Chars Out': '1816',
                                                          'Pkts In': '0',
                                                          'Pkts Out': '24',
                                                          'Protocol': 'IPV6_ND'}},
                           'TenGigE0/0/0/9': {'ARP': {'Chars In': '1500',
                                                      'Chars Out': '1092',
                                                      'Pkts In': '25',
                                                      'Pkts Out': '26',
                                                      'Protocol': 'ARP'},
                                              'IPV4_UNICAST': {'Chars In': '3689807',
                                                               'Chars Out': '0',
                                                               'Pkts In': '45574',
                                                               'Pkts Out': '0',
                                                               'Protocol': 'IPV4_UNICAST'},
                                              'IPV6_ND': {'Chars In': '2476',
                                                          'Chars Out': '2648',
                                                          'Pkts In': '30',
                                                          'Pkts Out': '32',
                                                          'Protocol': 'IPV6_ND'},
                                              'IPV6_UNICAST': {'Chars In': '3932',
                                                               'Chars Out': '0',
                                                               'Pkts In': '44',
                                                               'Pkts Out': '0',
                                                               'Protocol': 'IPV6_UNICAST'},
                                              'MPLS': {'Chars In': '31683189016050',
                                                       'Chars Out': '2791247055432',
                                                       'Pkts In': '211221260107',
                                                       'Pkts Out': '21145811026',
                                                       'Protocol': 'MPLS'}}}

        self.outputDict11={
             'Cleanup': {'End-Time': '-',
                         'Phase': 'Cleanup',
                         'Start-Time': '-',
                         'State': '-'},
             'Load': {'End-Time': 'N/A',
                      'Phase': 'Load',
                      'Start-Time': '13:48:11',
                      'State': 'In progress'},
             'Prepare': {'End-Time': '13:44:11',
                         'Phase': 'Prepare',
                         'Start-Time': '13:41:38',
                         'State': 'Completed'},
             'Run': {'End-Time': '-', 'Phase': 'Run', 'Start-Time': '-', 'State': 'Next'}
        }

        self.outputDict12=\
            {'10': {'Disk': '0',
                    'Ephemeral': '0',
                    'ID': '10',
                    'Is_Public': 'True',
                    'Memory_MB': '1024',
                    'Name': 'Cirros_FLAVOR',
                    'RXTX_Factor': '1.0',
                    'Swap': '',
                    'VCPUs': '2'},
             '11': {'Disk': '0',
                    'Ephemeral': '0',
                    'ID': '11',
                    'Is_Public': 'True',
                    'Memory_MB': '4096',
                    'Name': 'ASAv_FLAVOR',
                    'RXTX_Factor': '1.0',
                    'Swap': '',
                    'VCPUs': '2'},
             '12': {'Disk': '0',
                    'Ephemeral': '0',
                    'ID': '12',
                    'Is_Public': 'True',
                    'Memory_MB': '4096',
                    'Name': 'CSRv_FLAVOR',
                    'RXTX_Factor': '1.0',
                    'Swap': '',
                    'VCPUs': '2'}}


        self.showCommandOutput2 = '''\
            BGP router identifier 192.168.0.12, local AS number 100
            BGP generic scan interval 60 secs
            BGP table state: Active
            Table ID: 0xe0000000   RD version: 8
            BGP main routing table version 8
            BGP scan interval 60 secs

            BGP is operating in STANDALONE mode.

            Process       RcvTblVer   bRIB/RIB   LabelVer  ImportVer  SendTblVer  StandbyVer
            Speaker               8          8          8          8           8           8

            Neighbor        Spk AS   MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down   St/PfxRcd
            50.1.0.2        0   100  63      55        8       0   0     00:51:24  100
            50.1.0.3        0   200  63      55        8       0   0     00:40:16  200
        '''



        self.showCommandOutput3 = '''\
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


        self.showCommandOutput4 = '''\
            NAME
            ------------------------------------------
            ubuntu-14.04.3-server-amd64-disk1.tar.gz
            asav951-201.tar.gz
            isrv-universalk9.16.03.01.tar.gz
        '''


        self.showCommandOutput5 = '''\
                                                  NAME
            ------------------------------------------
              ubuntu-14.04.3-server-amd64-disk1.tar.gz
                                    asav951-201.tar.gz
                      isrv-universalk9.16.03.01.tar.gz
        '''

        self.showCommandOutput6='''
            sysadmin-vm:0_RP0# show environment power location F0/FC0
            Sun Apr  23 22:27:38.178 UTC-07:00

            ================================================================================
               Location     Card Type            Power       Power       Status
                                                 Allocated   Used
                                                 Watts       Watts
            ================================================================================
               F0/FC0       NCS-F-FC               440         291       ON
            '''

        self.showCommandOutput7='''
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

        self.showCommandOutput8='''
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

        self.showCommandOutput9='''
            Cards OIR History of rack: 0

            OIR Events as seen by Master (0/RP1)-
              DATE   TIME (UTC)     EVENT        LOC     CARD TYPE            SERIAL NO
              Normal Seconds        Type         Rck     Detail               Number
              -----  ------------   ----------   -----   ------------------   -----------
              04/22  02:27:57.002   INSERTED     0/7     NC6-10X100G-M-K      SAL1929K8RJ
              04/22  02:22:17.765   REMOVED      0/7     NC6-20X100GE-M-C     SAL211004A5
              04/22  00:45:54.471   DISCOVERED   0/RP0   NC6-RP               SAL1923GBM1
              04/22  00:45:54.426   DISCOVERED   0/FC5   NC6-FC2-U            SAL210304H4
              04/22  00:45:54.331   DISCOVERED   0/FC4   NC6-FC2-U            SAL210304GG
            '''

        self.showCommandOutput10='''
            +-----------
            |  Channel |
            |  Number. |
            +-----------
            | Rx Ch 0: |
            | Rx Ch 1: |
            | Rx Ch 2: |
            | Rx Ch 3: |
            | Rx Ch 4: |
            | Rx Ch 5: |
            | Rx Ch 6: |
            | Rx Ch 7: |
            | Rx Ch 8: |
            | Rx Ch 9: |
            | Rx Ch 10:|
            | Rx Ch 11:|
            +-----------
            '''

        self.showCommandOutput11='''
            TenGigE0/0/0/0
            |  Protocol      |        Pkts In|     Chars In|   Pkts Out|        Chars Out|
            |  ARP           |              0|            0|          2|               84|
            |  IPV6_ND       |              0|            0|         25|             1920|
            '''

        self.showCommandOutput12='''
            TenGigE0/0/0/0
            |  Protocol      |     Pkts In|         Chars In|     Pkts Out|        Chars Out|
            |  ARP           |           0|                0|            2|               84|
            |  IPV6_ND       |           0|                0|           25|             1920|

            TenGigE0/0/0/1
            |  Protocol      |     Pkts In|         Chars In|     Pkts Out|        Chars Out|
            |  ARP           |           0|                0|            2|               84|
            |  IPV6_ND       |           0|                0|           24|             1816|

            TenGigE0/0/0/9
            |  Protocol      |     Pkts In|         Chars In|     Pkts Out|        Chars Out|
            |  IPV4_UNICAST  |       45574|          3689807|            0|                0|
            |  IPV6_UNICAST  |          44|             3932|            0|                0|
            |  MPLS          |211221260107|   31683189016050|  21145811026|    2791247055432|
            |  ARP           |          25|             1500|           26|             1092|
            |  IPV6_ND       |          30|             2476|           32|             2648|
            '''

        self.showCommandOutput13='''
            TenGigE0/0/0/0
            |     Protocol   |Pkts In     |         Chars In| Pkts Out    | Chars Out       |
            |  ARP           | 0          | 0               | 2           | 84              |
            |  IPV6_ND       | 0          | 0               | 25          | 1920            |

            TenGigE0/0/0/1
            |  Protocol      | Pkts In    | Chars In        | Pkts Out    | Chars Out       |
            |  ARP           | 0          | 0               | 2           | 84              |
            |  IPV6_ND       | 0          | 0               | 24          | 1816            |

            TenGigE0/0/0/9
            |  Protocol      | Pkts In   | Chars In        | Pkts Out    | Chars Out       |
            |  IPV4_UNICAST  |45574      | 3689807         | 0           | 0               |
            |  IPV6_UNICAST  |44         | 3932       | 0           | 0               |
            |  MPLS          |211221260107| 31683189016050  | 21145811026 | 2791247055432   |
            |  ARP           |25         | 1500            | 26          | 1092            |
            |  IPV6_ND       |30         | 2476            | 32          | 2648            |
            '''

        self.showCommandOutput14='''
            show issu
            Wed Jul 12 13:49:38.582 UTC
            INSTALL Operation ID    : Operation 2 Started at Wed Jul 12 13:47:59 2017
            ISSU Progress           : 17.0%
            Total ISSU Time         : -
            ISSU Type               : IMAGE(V1-6.4.1.05I/V2-6.4.1.05I)
             
            Phase           Start-Time      End-Time                  State                     
            --------------------------------------------------------------------------------
            Prepare         13:41:38        13:44:11                  Completed                 
            Load            13:48:11        N/A                       In progress               
            Run             -               -                         Next                      
            Cleanup         -               -                         -                         
            --------------------------------------------------------------------------------
            Current Status          : ISSU Node Readiness is Awaited
             
            Setup Information       : Single Chassis
            ISSU Ready/Not Ready    : 0 / 2
             
            Node ISSU readiness per rack per slot
            Key: Ready - 'Y', Not ready - 'N', Primary node - '*', Complete - '-'
             
            Rack 0   RP0   RP1   LC0  
                      *     N     N  
            '''


        self.showCommandOutput15='''
            nova flavor-list
            +----+---------------+-----------+------+-----------+------+-------+-------------+-----------+
            | ID | Name          | Memory_MB | Disk | Ephemeral | Swap | VCPUs | RXTX_Factor | Is_Public |
            +----+---------------+-----------+------+-----------+------+-------+-------------+-----------+
            | 10 | Cirros_FLAVOR | 1024      | 0    | 0         |      | 2     | 1.0         | True      |
            | 11 | ASAv_FLAVOR   | 4096      | 0    | 0         |      | 2     | 1.0         | True      |
            | 12 | CSRv_FLAVOR   | 4096      | 0    | 0         |      | 2     | 1.0         | True      |
            +----+---------------+-----------+------+-----------+------+-------+-------------+-----------+
            [cisco@SVS-NFVI-1-MGMT ~]$
            '''

    def test_tabular_parser(self):
        ''' Test the parsing of tabular "show" command output.
        '''
        parse_key = 'rtr1'
        core.text_to_parse[parse_key] = dedent(showCommandOutput1)
        header = ['Neighbor', 'Spk', 'AS', 'MsgRcvd', 'MsgSent',
                  'TblVer', 'InQ', 'OutQ', 'Up/Down', 'St/PfxRcd']
        labels = ['neighbor', 'spk', 'as', 'msg_rcvd', 'msg_sent' ,
                  'tbl_ver', 'in_q', 'out_q', 'time', 'prefixes']
        tabular_parse_result = column_table_result_core_t(
                                    header, label_fields=labels, index=[0,2],
                                    right_justified=True, parse_key=parse_key);
        self.assertEqual(self.outputDict1, tabular_parse_result.entries)

        core.text_to_parse[parse_key] = dedent(self.showCommandOutput2)
        tabular_parse_result = column_table_result_core_t(
                                    header, label_fields=labels, index=[0,2],
                                    right_justified=False, parse_key=parse_key);
        self.assertEqual(self.outputDict1, tabular_parse_result.entries)


    def test_tabular_parser_with_subclassing(self):

        def _hexint (val):
            return int(val, 16)

        def cleanupLspId (field):
            index = field.rfind("*")
            if index != -1:
                field = field[0:index]
                field = field.strip()
            return field

        def cleanupAttPol(field):
            if python3:
                field = [item for item in map(int, field.split('/'))]
            else:
                field = map(int, field.split("/"))
                field = field[0:3]
            return field


        class my_isis_database_column_parser_t (column_table_result_core_t):
            field_mapping = {
                'LSPID'       :   str,
                'LSP Seq Num' :   _hexint,
                'LSP Checksum':   _hexint,
                'LSP Holdtime':   None,
                }

            table_title_mapping = [ int ]

            def __init__ (self):
                headers = ["LSPID", "LSP Seq Num", "LSP Checksum",
                "LSP Holdtime",  "ATT/P/OL"]
                labels = headers

                column_table_result_core_t.__init__(
                 self,
                 headers,
                 "Total Level-[12] LSP count:",
                 table_title_pattern =
                 r"IS-IS (?:[-\w]+ )?\(?Level-([12])\)? Link State Database:?",
                 label_fields = labels)

            def cleanup_entry_field (self, header, field):
                if header == "LSPID":
                    # Strip the "*" off the LSPID for the router's own LSPID.
                    return cleanupLspId(field)
                elif header == "ATT/P/OL":
                    return cleanupAttPol(field)
                return field

        parse_key = ''
        core.text_to_parse[parse_key]  = dedent(self.showCommandOutput3)
        subclassed_tabular_parse_result = my_isis_database_column_parser_t()
        self.assertEqual(self.outputDict2,
                         subclassed_tabular_parse_result.entries)


    def test_tabular_parser_single_column(self):
        ''' Test the parsing of tabular "show" command output with one column.
        '''
        self.maxDiff = None
        parse_key = 'rtr1'
        core.text_to_parse[parse_key] = dedent(self.showCommandOutput4)
        header = ['NAME']
        tabular_parse_result = column_table_result_core_t(
                                    header,
                                    right_justified=False, parse_key=parse_key)
        self.assertEqual(self.outputDict3, tabular_parse_result.entries)

        core.text_to_parse[parse_key] = dedent(self.showCommandOutput5)
        tabular_parse_result = column_table_result_core_t(
                                    header,
                                    right_justified=True, parse_key=parse_key)
        self.assertEqual(self.outputDict3, tabular_parse_result.entries)

    def test_tabular_parser_multiple_headers(self):
        ''' Test the parsing of tabular "show" command output with multiple
            headers.
        '''
        parse_key = 'rtr1'
        core.text_to_parse[parse_key] = dedent(self.showCommandOutput6)
        header = [['Location',
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
                  '']]
        labels = ["Location",
                  "Card Type",
                  "Power Allocated Watts",
                  "Power Used Watts",
                  "Status"]
        tabular_parse_result = column_table_result_core_t(
                                    header, label_fields=labels, index=[0],
                                    parse_key=parse_key, delimiter = '\s');
        self.assertEqual(self.outputDict4, tabular_parse_result.entries)

    def test_tabular_parser_multiple_headers_delimiters(self):
        ''' Test the parsing of tabular "show" command delimited output
            with multiple headers.
        '''
        parse_key = 'rtr1'
        core.text_to_parse[parse_key] = dedent(self.showCommandOutput7)
        header = [['Asic inst\.',
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
                 '\(#\)']]
        tabular_parse_result = column_table_result_core_t(
                                    header, index=[0,12],
                                    parse_key=parse_key, delimiter = '|');
        self.assertEqual(self.outputDict5, tabular_parse_result.entries)

    def test_tabular_parser_multiple_headers_multiple_fields_delimiters(self):
        ''' Test the parsing of tabular "show" command output with multiple
            headers, multiple fields within table columns and delimiters.
        '''
        parse_key = 'rtr1'
        core.text_to_parse[parse_key] = dedent(self.showCommandOutput8)
        header = [['Channel', 'Channel', 'Signal \.', 'Optical Power',
                   'Optical Light'],
                  ['Number\.','Status','    Strength   ','Alarm', 'Input']]
        labels = ["Channel Number","Channel Status","Signal Strength",
                  "Optical Power Alarm","Optical Power Input"]
        tabular_parse_result = column_table_result_core_t(
                                    header, label_fields=labels, index=[0,4],
                                    parse_key=parse_key, delimiter = '|');
        self.assertEqual(self.outputDict6, tabular_parse_result.entries)

    def test_tabular_parser_multiple_headers_no_delimiter(self):
        ''' Test the parsing of tabular "show" command output with multiple
            headers without delimiters.
        '''
        parse_key = 'rtr1'
        core.text_to_parse[parse_key] = dedent(self.showCommandOutput9)
        header = [['DATE','TIME \([A-Z]+\)','EVENT', 'LOC','CARD TYPE',
                   'SERIAL NO'],
                  ['Normal','Seconds','Type','Rck', 'Detail','Number']]
        labels = ['DATE','TIME','EVENT', 'LOC','CARD TYPE','SERIAL NO']
        tabular_parse_result = column_table_result_core_t(
                                    header, label_fields=labels, index=[1,6],
                                    parse_key=parse_key,);
        self.assertEqual(self.outputDict7, tabular_parse_result.entries)

    def test_tabular_parser_unequal_multiple_headers(self):
        ''' Test the parsing of tabular "show" command output with multiple
            headers with different length.
        '''
        parse_key = 'rtr1'
        core.text_to_parse[parse_key] = dedent(self.showCommandOutput9)
        header = [['DATE','TIME \([A-Z]+\)','EVENT', 'LOC','CARD TYPE',
                   'SERIAL NO'],
                  ['Normal','Seconds','Type','Detail','Number']]
        labels = ['DATE','TIME','EVENT', 'LOC','CARD TYPE','SERIAL NO']
        with self.assertRaises(AttributeError):
          tabular_parse_result = column_table_result_core_t(
                                      header, label_fields=labels, index=[1,6],
                                      parse_key=parse_key,);

    def test_tabular_parser_single_column_delimited_table(self):
        ''' Test the parsing of tabular "show" command output with multiple
            headers with different length.
        '''
        parse_key = 'rtr1'
        core.text_to_parse[parse_key] = dedent(self.showCommandOutput10)
        header = [['Channel'],
                  ['Number\.']]
        labels = ['Channel Number.']
        tabular_parse_result = column_table_result_core_t(
                                    header, label_fields=labels, index=[0],
                                    parse_key=parse_key,);
        self.assertEqual(self.outputDict8, tabular_parse_result.entries)

    def test_tabular_parser_right_justified_delimited_table(self):
        ''' Test the parsing of right justified tabular "show" command output
            with delimiter.
        '''
        parse_key = 'rtr1'
        core.text_to_parse[parse_key] = dedent(self.showCommandOutput11)
        header = [ 'Protocol      ', 'Pkts\s+In', 'Chars\s+In',
          'Pkts\s+Out', 'Chars\s+Out']
        labels = [ 'Protocol', 'Pkts In', 'Chars In',
          'Pkts Out', 'Chars Out']
        tabular_parse_result = column_table_result_core_t(
                                    header, label_fields=labels, index=[0,4],
                                    parse_key=parse_key,
                                    right_justified = True, delimiter = '|');

        self.assertEqual(self.outputDict9, tabular_parse_result.entries)

    def test_tabular_parser_multiple_delimited_tables(self):
        ''' Test the parsing of multiple delimited tables with multi-line
            headers.
        '''
        parse_key = 'rtr1'
        core.text_to_parse[parse_key] = dedent(self.showCommandOutput12)
        header = [ 'Protocol    ', 'Pkts\s+In', 'Chars\s+In',
         'Pkts\s+Out', 'Chars\s+Out']

        labels = [ 'Protocol', 'Pkts In', 'Chars In',
         'Pkts Out', 'Chars Out']

        title_pattern = r'(?P<Title>[^/\s]+/[^/\s]+/[^/\s]+/\S+)\s*'

        tabular_parse_result = column_table_result_core_t(
                                    header, label_fields=labels, index=[0],
                                    parse_key=parse_key,
                                    right_justified = True, delimiter = '|',
                                    table_title_pattern = title_pattern);

        self.assertEqual(self.outputDict10, tabular_parse_result.entries)


    def test_tabular_parser_multiple_delimited_tables_2(self):
        ''' Test the parsing of multiple delimited tables with multi-line
            headers.
        '''
        parse_key = 'rtr1'
        core.text_to_parse[parse_key] = dedent(self.showCommandOutput13)
        header = [ 'Protocol    ', 'Pkts\s+In', 'Chars\s+In',
         'Pkts\s+Out', 'Chars\s+Out']

        labels = [ 'Protocol', 'Pkts In', 'Chars In',
         'Pkts Out', 'Chars Out']

        title_pattern = r'(?P<Title>[^/\s]+/[^/\s]+/[^/\s]+/\S+)\s*'

        tabular_parse_result = column_table_result_core_t(
                                    header, label_fields=labels, index=[0],
                                    parse_key=parse_key,
                                    right_justified = False, delimiter = '|',
                                    table_title_pattern = title_pattern);

        self.assertEqual(self.outputDict10, tabular_parse_result.entries)


    def test_tabular_parser_contains_regexp_sensitive_characters(self):
        ''' Test the parsing of a table containing regex-sensitive characters.
        The raw output contains asterisk characters.
        '''
        parse_key = 'rtr1'
        core.text_to_parse[parse_key] = dedent(self.showCommandOutput14)

        header=["Phase", "Start-Time", "End-Time", "State"]

        tabular_parse_result = column_table_result_core_t(
            parse_key=parse_key,
            index=[0],
            header_fields=header,
            table_terminal_pattern='Status',
            )

        self.assertEqual(self.outputDict11, tabular_parse_result.entries)


    def test_tabular_parser_delimited_table_with_empty_column_ljust(self):
        ''' Test the parsing of tabular "show" command output.
            Ensure empty columns are properly reflected in the parsed output.
        '''
        parse_key = 'rtr1'
        core.text_to_parse[parse_key] = dedent(self.showCommandOutput15)
        header = ["ID", "Name", "Memory_MB", "Disk", "Ephemeral", "Swap","VCPUs", "RXTX_Factor", "Is_Public"]
        tabular_parse_result = column_table_result_core_t(
                                    header, index=[0],
                                    delimiter = '|',
                                    parse_key=parse_key,
                                    right_justified=False);
        self.assertEqual(self.outputDict12, tabular_parse_result.entries)


    def test_tabular_parser_delimited_table_with_empty_column_rjust(self):
        ''' Test the parsing of tabular "show" command output.
            Ensure empty columns are properly reflected in the parsed output.
        '''
        parse_key = 'rtr1'
        core.text_to_parse[parse_key] = dedent(self.showCommandOutput15)
        header = ["ID", "Name", "Memory_MB", "Disk", "Ephemeral", "Swap","VCPUs", "RXTX_Factor", "Is_Public"]
        tabular_parse_result = column_table_result_core_t(
                                    header, index=[0],
                                    delimiter = '|',
                                    parse_key=parse_key,
                                    right_justified=True);
        self.assertEqual(self.outputDict12, tabular_parse_result.entries)
