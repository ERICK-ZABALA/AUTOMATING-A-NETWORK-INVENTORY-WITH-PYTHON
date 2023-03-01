import unittest

from genie.utils.dq import Dq

parsed_output = {"processor_pool":{"total":735981852,"used":272743032,"free":463238820},"pid":{"0":{"index":{"1":{"pid":0,"tty":0,"allocated":256940960,"freed":73576632,"holding":158001024,"getbufs":392,"retbufs":12905093,"process":"*Init*", "test_key": "^net_conf_aws", "checkSum": "0x1abc"}}}}}
module = {'rp': {'1': {'NX-OSv Supervisor Module': {'ports': '0', 'model': 'N7K-SUP1', 'status': 'active', 'software': '7.3(0)D1(1)', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '5e-00-40-01-00-00 to 5e-00-40-01-07-ff', 'serial_number': 'TM40010000B'}}}, 'lc': {'2': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-02-00 to 02-00-0c-00-02-7f', 'serial_number': 'TM40010000C'}}, '3': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-03-00 to 02-00-0c-00-03-7f', 'serial_number': 'TM40010000D'}}, '4': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': [1,2,3], 'mac_address': '02-00-0c-00-04-00 to 02-00-0c-00-04-7f', 'serial_number': 'TM40010000E'}}}}
module_t = {'rp': {'1': {'NX-OSv Supervisor Module': {'ports': '0', 'model': 'N7K-SUP1', 'status': 'active', 'software': '7.3(0)D1(1)', 'hardware': '0.0', 'slot/world_wide_name': [1,2, 'a', [1,2,3]],'list_d': [1,2,3], 'mac_address': '5e-00-40-01-00-00 to 5e-00-40-01-07-ff', 'serial_number': 'TM40010000B'}}}, 'lc': {'2': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': [1,2,3], 'mac_address': '02-00-0c-00-02-00 to 02-00-0c-00-02-7f', 'serial_number': 'TM40010000C'}}, '3': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'list_c': [1,2,3], 'mac_address': '02-00-0c-00-03-00 to 02-00-0c-00-03-7f', 'serial_number': 'TM40010000D', '3': [1,2,3]}}, '4': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': [1,2,3], 'mac_address': '02-00-0c-00-04-00 to 02-00-0c-00-04-7f', 'list_a':[1,2,3], 'list_b':[2,3], 'serial_number': 'TM40010000E', '4': [1,3]}}}}
peer = {'total_peers': 1, 'total_established_peers': 1, 'local_as': 65000, 'vrf': {'default': {'local_as': 65000, 'vrf_peers': 1, 'vrf_established_peers': 1, 'router_id': '10.2.2.2', 'neighbor': {'10.1.1.1': {'remote_as': 65000, 'connections_dropped': 1, 'last_flap': '3d14h', 'last_read': '00:00:01', 'last_write': '00:00:32', 'state': 'established', 'local_port': 179, 'remote_port': [1,3,2,9], 'notifications_sent': 1, 'notifications_received': 0}}}}}

 # This is not the actual representation of any parsed command. The actual output is manipulated for testing purposes
ospf = {"ospf-neighbor-information":{"ospf-neighbor":[{"activity-timer":"35","interface-name":"ge-0/0/0.0","neighbor-address":["111.87.5.94", '1.2.3.4', '0.0.0.0', '2.2.3.4'],"neighbor-id":{'id1': ["111.87.5.253", '1.1.1.1', '9.8.166.1']},"neighbor-priority":"128","ospf-neighbor-state":"Full"},{"activity-timer":"34","interface-name":"ge-0/0/1.0","neighbor-address":["106.187.14.121", '2.2.2.2'],"neighbor-id":{'id2': ["106.187.14.240"]},"neighbor-priority":"128","ospf-neighbor-state":"Full"},{"activity-timer":"32","interface-name":"ge-0/0/2.0","neighbor-address":["27.86.198.26"],"neighbor-id":{'id3':["27.86.198.239", '1.2.66.77']},"neighbor-priority":"1","ospf-neighbor-state":"Full"}]}}
vrf = {'vrf': {'default': {'neighbor': {'10.1.1.1': {'address_family': {'ipv4 unicast': {'neighbor_table_version': 4, 'as': 65000, 'msg_rcvd': 5694, 'msg_sent': 5175, 'tbl_ver': 11, 'inq': 0, 'outq': 0, 'up_down': '3d14h', 'state_pfxrcd': '1',
'prefix_received': '1', 'state': 'established', 'route_identifier': '10.2.2.2', 'local_as': 65000, 'bgp_table_version': 11, 'config_peers': 1, 'capable_peers': 1, 'attribute_entries': '[2/288]', 'as_path_entries': '[0/0]', 'community_entries': '[0/0]', 'clusterlist_entries': '[0/0]', 'prefixes': {'total_entries': 2, 'memory_usage': 288}, 'path': {'total_entries': 2, 'memory_usage': 288}}}}}}}}
cpu_load = {'bgp': {'value': 10}, 'ospf': {'value': 20}}

class test_dq(unittest.TestCase):

    maxDiff = None

    def test_init(self):
        module_Dq = Dq(module)
        peer_Dq = Dq(peer)
        vrf_Dq = Dq(vrf)
        self.assertEqual(len(module_Dq), 34)
        self.assertEqual(len(peer_Dq), 20)
        self.assertEqual(len(vrf_Dq), 24)

    def test_reconstruct(self):
        module_Dq = Dq(module)
        peer_Dq = Dq(peer)
        vrf_Dq = Dq(vrf)
        self.assertEqual(module, module_Dq.reconstruct())
        self.assertEqual(peer, peer_Dq.reconstruct())
        self.assertEqual(vrf, vrf_Dq.reconstruct())

    def test_contains(self):
        mod = Dq(module)
        mod_t = Dq(module_t)
        output = mod.contains('rp')
        self.assertEqual(output.reconstruct(),
                {'rp': {'1': {'NX-OSv Supervisor Module': {'ports': '0', 'model': 'N7K-SUP1', 'status': 'active', 'software': '7.3(0)D1(1)', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '5e-00-40-01-00-00 to 5e-00-40-01-07-ff', 'serial_number': 'TM40010000B'}}}})

        output = mod.contains('N7K-SUP1')
        self.assertEqual(output.reconstruct(),
                {'rp': {'1': {'NX-OSv Supervisor Module': {'model': 'N7K-SUP1'}}}})


        output = mod.contains('Active', regex=True, ignore_case=True)
        self.assertEqual(output.reconstruct(),
                         {'rp': {'1': {'NX-OSv Supervisor Module': {'status': 'active'}}}})

        output = mod.contains('N7K-SUP1', level=-1)
        self.assertEqual(output.reconstruct(),
                {'rp': {'1': {'NX-OSv Supervisor Module': {'ports': '0', 'model': 'N7K-SUP1', 'status': 'active', 'software': '7.3(0)D1(1)', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '5e-00-40-01-00-00 to 5e-00-40-01-07-ff', 'serial_number': 'TM40010000B'}}}})

        output = mod.contains('[1,2]', regex=True)
        self.assertEqual(output.reconstruct(),
                {"rp":{"1":{"NX-OSv Supervisor Module":{"ports":"0","model":"N7K-SUP1","status":"active","software":"7.3(0)D1(1)","hardware":"0.0","slot/world_wide_name":"--","mac_address":"5e-00-40-01-00-00 to 5e-00-40-01-07-ff","serial_number":"TM40010000B"}}},"lc":{"2":{"NX-OSv Ethernet Module":{"ports":"48","model":"N7K-F248XP-25","status":"ok","software":"NA","hardware":"0.0","slot/world_wide_name":"--","mac_address":"02-00-0c-00-02-00 to 02-00-0c-00-02-7f","serial_number":"TM40010000C"}},'4': {'NX-OSv Ethernet Module': {'slot/world_wide_name': [1, 2]}}}})

        output = mod.contains('[1,2]', regex=True, level=-1)
        self.assertEqual(output.reconstruct(),
                {'rp': {'1': {'NX-OSv Supervisor Module': {'ports': '0', 'model': 'N7K-SUP1', 'status': 'active', 'software': '7.3(0)D1(1)', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '5e-00-40-01-00-00 to 5e-00-40-01-07-ff', 'serial_number': 'TM40010000B'}}}, 'lc': {'2': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-02-00 to 02-00-0c-00-02-7f', 'serial_number': 'TM40010000C'}}, '3': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-03-00 to 02-00-0c-00-03-7f', 'serial_number': 'TM40010000D'}}, '4': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': [1,2,3], 'mac_address': '02-00-0c-00-04-00 to 02-00-0c-00-04-7f', 'serial_number': 'TM40010000E'}}}})

        output = mod.contains([1,2,3])
        self.assertEqual(output.reconstruct(),  {'lc': {'4': {'NX-OSv Ethernet Module': {'slot/world_wide_name': [1, 2, 3]}}}})

        output = mod_t.contains( [1,2,'a', [1,2,3]])
        self.assertEqual(output.reconstruct(),
                {'rp': {'1': {'NX-OSv Supervisor Module': {'slot/world_wide_name': [1, 2, 'a', [1, 2, 3]]}}}})

        output = mod_t.contains([1,2,3], regex=True)
        self.assertEqual(output.reconstruct(), {})

        output = mod_t.contains([1,2,3])
        self.assertEqual(output.reconstruct(),
                {'rp': {'1': {'NX-OSv Supervisor Module': {'list_d': [1, 2, 3]}}}, 'lc': {'2': {'NX-OSv Ethernet Module': {'slot/world_wide_name': [1, 2, 3]}}, '3': {'NX-OSv Ethernet Module': {'list_c': [1, 2, 3], '3': [1, 2, 3]}}, '4': {'NX-OSv Ethernet Module': {'slot/world_wide_name': [1, 2, 3], 'list_a': [1, 2, 3]}}}})

        output = mod.contains('lc').contains('4')
        self.assertEqual(output.reconstruct(),
                {'lc': {'4': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': [1, 2, 3], 'mac_address': '02-00-0c-00-04-00 to 02-00-0c-00-04-7f', 'serial_number': 'TM40010000E'}}}})

        output = mod.contains('lc').contains('4').contains('status')
        self.assertEqual(output.reconstruct(),
                {'lc': {'4': {'NX-OSv Ethernet Module': {'status': 'ok'}}}})
        
        output = mod.contains('.*ware', regex=True)
        self.assertEqual(output.reconstruct(),
                {"rp":{"1":{"NX-OSv Supervisor Module":{"software":"7.3(0)D1(1)","hardware":"0.0"}}},"lc":{"2":{"NX-OSv Ethernet Module":{"software":"NA","hardware":"0.0"}},"3":{"NX-OSv Ethernet Module":{"software":"NA","hardware":"0.0"}},"4":{"NX-OSv Ethernet Module":{"software":"NA","hardware":"0.0"}}}})

        parsed_output_dq = Dq(parsed_output)
        output = parsed_output_dq.contains('*Init*', regex=True, escape_special_chars=['*'])
        self.assertEqual(output.reconstruct(),
                {'pid': {'0': {'index': {'1': {'process': '*Init*'}}}}})

        # escaped "^" and won't treat "^" as special character with its regex value 
        output = parsed_output_dq.contains(r"^net_conf[\S\s]*", regex=True, escape_special_chars=['^'])
        self.assertEqual(output.reconstruct(),
                {'pid': {'0': {'index': {'1': {'test_key': '^net_conf_aws'}}}}})

        # Since the "^" is not escaped, "^" has regex value, hence it would match values 
        # that starts with net_conf. There is no such value in this dictionary so the output 
        # is rightfully empty
        output = parsed_output_dq.contains(r"^net_conf[\S\s]*", regex=True)
        self.assertEqual(output.reconstruct(),
                {})

    def test_not_contains(self):
        mod = Dq(module)
        output = mod.not_contains('rp')
        self.assertEqual(output.reconstruct(),
                {'lc': {'2': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-02-00 to 02-00-0c-00-02-7f', 'serial_number': 'TM40010000C'}}, '3': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-03-00 to 02-00-0c-00-03-7f', 'serial_number': 'TM40010000D'}}, '4': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': [1, 2, 3], 'mac_address': '02-00-0c-00-04-00 to 02-00-0c-00-04-7f', 'serial_number': 'TM40010000E'}}}})

        output = mod.not_contains('Ports', regex=True, ignore_case=True)
        self.assertEqual(output.reconstruct(),
                {'rp': {'1': {'NX-OSv Supervisor Module': {'model': 'N7K-SUP1', 'status': 'active', 'software': '7.3(0)D1(1)', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '5e-00-40-01-00-00 to 5e-00-40-01-07-ff', 'serial_number': 'TM40010000B'}}}, 'lc': {'2': {'NX-OSv Ethernet Module': {'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-02-00 to 02-00-0c-00-02-7f', 'serial_number': 'TM40010000C'}}, '3': {'NX-OSv Ethernet Module': {'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-03-00 to 02-00-0c-00-03-7f', 'serial_number': 'TM40010000D'}}, '4': {'NX-OSv Ethernet Module': {'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': [1, 2, 3], 'mac_address': '02-00-0c-00-04-00 to 02-00-0c-00-04-7f', 'serial_number': 'TM40010000E'}}}})

        output = mod.not_contains('N7K-SUP1', level=-2)
        self.assertEqual(output.reconstruct(),
                {"rp":{"1":{"NX-OSv Supervisor Module":{"ports":"0","software":"7.3(0)D1(1)","status":"active","hardware":"0.0","slot/world_wide_name":"--", 'mac_address': '5e-00-40-01-00-00 to 5e-00-40-01-07-ff', 'serial_number': 'TM40010000B'}}},'lc': {'2': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-02-00 to 02-00-0c-00-02-7f', 'serial_number': 'TM40010000C'}}, '3': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-03-00 to 02-00-0c-00-03-7f', 'serial_number': 'TM40010000D'}}, '4': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': [1, 2, 3], 'mac_address': '02-00-0c-00-04-00 to 02-00-0c-00-04-7f', 'serial_number': 'TM40010000E'}}}})

        output = mod.not_contains('rp').not_contains('4')
        self.assertEqual(output.reconstruct(),
                {'lc': {'2': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-02-00 to 02-00-0c-00-02-7f', 'serial_number': 'TM40010000C'}}, '3': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-03-00 to 02-00-0c-00-03-7f', 'serial_number': 'TM40010000D'}}}})

        output = mod.not_contains('N7K-SUP1', level=-1).not_contains('4')
        self.assertEqual(output.reconstruct(),
                {"rp":{"1":{"NX-OSv Supervisor Module":{"ports":"0","software":"7.3(0)D1(1)","status":"active","hardware":"0.0","slot/world_wide_name":"--", 'mac_address': '5e-00-40-01-00-00 to 5e-00-40-01-07-ff', 'serial_number': 'TM40010000B'}}}, 'lc': {'2': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-02-00 to 02-00-0c-00-02-7f', 'serial_number': 'TM40010000C'}}, '3': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-03-00 to 02-00-0c-00-03-7f', 'serial_number': 'TM40010000D'}}}})

        output = mod.not_contains('.*(address|number).*', regex=True)
        self.assertEqual(output.reconstruct(), 
                {"rp":{"1":{"NX-OSv Supervisor Module":{"ports":"0","model":"N7K-SUP1","status":"active","software":"7.3(0)D1(1)","hardware":"0.0","slot/world_wide_name":"--"}}},"lc":{"2":{"NX-OSv Ethernet Module":{"ports":"48","model":"N7K-F248XP-25","status":"ok","software":"NA","hardware":"0.0","slot/world_wide_name":"--"}},"3":{"NX-OSv Ethernet Module":{"ports":"48","model":"N7K-F248XP-25","status":"ok","software":"NA","hardware":"0.0","slot/world_wide_name":"--"}},"4":{"NX-OSv Ethernet Module":{"ports":"48","model":"N7K-F248XP-25","status":"ok","software":"NA","hardware":"0.0","slot/world_wide_name":[1,2,3]}}}})

        output = mod.not_contains('1|4', regex=True).not_contains('.*ware', regex=True)
        self.assertEqual(output.reconstruct(), 
                {"lc":{"2":{"NX-OSv Ethernet Module":{"ports":"48","model":"N7K-F248XP-25","status":"ok","slot/world_wide_name":"--","mac_address":"02-00-0c-00-02-00 to 02-00-0c-00-02-7f","serial_number":"TM40010000C"}},"3":{"NX-OSv Ethernet Module":{"ports":"48","model":"N7K-F248XP-25","status":"ok","slot/world_wide_name":"--","mac_address":"02-00-0c-00-03-00 to 02-00-0c-00-03-7f","serial_number":"TM40010000D"}}}})
    
    def test_contains_and_not_contains(self):
        mod = Dq(module)
        output = mod.contains('lc').contains('4').not_contains('status')
        self.assertEqual(output.reconstruct(),
                {'lc': {'4': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': [1, 2, 3], 'mac_address': '02-00-0c-00-04-00 to 02-00-0c-00-04-7f', 'serial_number': 'TM40010000E'}}}})

        output = mod.contains('(1|4)', regex=True).not_contains('.*ware', regex=True).not_contains('2')
        self.assertEqual(output.reconstruct(),
                {"rp":{"1":{"NX-OSv Supervisor Module":{"ports":"0","model":"N7K-SUP1","status":"active","slot/world_wide_name":"--","mac_address":"5e-00-40-01-00-00 to 5e-00-40-01-07-ff","serial_number":"TM40010000B"}}},"lc":{"4":{"NX-OSv Ethernet Module":{"ports":"48","model":"N7K-F248XP-25","status":"ok","slot/world_wide_name":[1,2,3],"mac_address":"02-00-0c-00-04-00 to 02-00-0c-00-04-7f","serial_number":"TM40010000E"}}}})
    
    def test_contains_list(self):
        mod = Dq(module)
        output = mod.contains(2)
        self.assertEqual(output.reconstruct(),
                {'lc': {'4': {'NX-OSv Ethernet Module': {'slot/world_wide_name': [2]}}}})

    def test_contains_key_wrong_regex_input(self):
        mod = Dq(module)

        # Example correct input: mod.contains_key_value('NX-OSv.*', '.*ware', key_regex=True, value_regex=True)
        output = mod.contains_key_value('NX-OSv.*', '.*ware', value_regex=True)
        self.assertEqual(output.reconstruct(), {})

        # Example correct input: mod.contains_key_value('NX-OSv.*', '.*ware', key_regex=True, value_regex=True)
        output = mod.contains_key_value('NX-OSv.*', '.*ware', key_regex=True)
        self.assertEqual(output.reconstruct(), {})

        mod.contains_key_value('NX-OSv.*', '.*ware')
        self.assertEqual(output.reconstruct(), {})

        output = mod.contains_key_value('NX-OSv', 'ware', key_regex=True, value_regex=True)
        self.assertEqual(output.reconstruct(), {})

        # Example correct input: mod.contains_key_value('.*world_wide_name', [1,3], key_regex=True)
        output = mod.contains_key_value('.*world_wide_name', '[1,2,3]', key_regex=True, value_regex=True)
        self.assertEqual(output.reconstruct(), {})

        output = mod.contains_key_value('.*world_wide_name', [1,2,3], key_regex=True, value_regex=True)
        self.assertEqual(output.reconstruct(), {})

        # Example correct input: mod.contains_key_value('mac_address', '[a-z0-9\-\s]+', value_regex=True)
        output = mod.contains_key_value(r'mac_address', r'[a-z0-9\-\s]', value_regex=True)
        self.assertEqual(output.reconstruct(), {})

    def test_contains_key_value_leaf(self):
        mod = Dq(module)
        mod_t = Dq(module_t)
        os = Dq(ospf)

        output = mod.contains_key_value('model', 'N7K-F248XP-25')
        self.assertEqual(output.reconstruct(),
                {'lc': {'2': {'NX-OSv Ethernet Module': {'model': 'N7K-F248XP-25'}}, '3': {'NX-OSv Ethernet Module': {'model': 'N7K-F248XP-25'}}, '4': {'NX-OSv Ethernet Module': {'model': 'N7K-F248XP-25'}}}})

        output = mod.contains_key_value('model', 'N7K.*', value_regex=True)
        self.assertEqual(output.reconstruct(),
                {"rp":{"1":{"NX-OSv Supervisor Module":{"model":"N7K-SUP1"}}},"lc":{"2":{"NX-OSv Ethernet Module":{"model":"N7K-F248XP-25"}},"3":{"NX-OSv Ethernet Module":{"model":"N7K-F248XP-25"}},"4":{"NX-OSv Ethernet Module":{"model":"N7K-F248XP-25"}}}})

        output = mod.contains_key_value('mac_address', r'[a-z0-9\-\s]+', value_regex=True)
        self.assertEqual(output.reconstruct(),
                {'rp': {'1': {'NX-OSv Supervisor Module': {'mac_address': '5e-00-40-01-00-00 to 5e-00-40-01-07-ff'}}}, 'lc': {'2': {'NX-OSv Ethernet Module': {'mac_address': '02-00-0c-00-02-00 to 02-00-0c-00-02-7f'}}, '3': {'NX-OSv Ethernet Module': {'mac_address': '02-00-0c-00-03-00 to 02-00-0c-00-03-7f'}}, '4': {'NX-OSv Ethernet Module': {'mac_address': '02-00-0c-00-04-00 to 02-00-0c-00-04-7f'}}}})

        output = mod.contains_key_value('slot/world_wide_name|mac.*|model', r'[a-zA-Z0-9\-\s]+', key_regex=True, value_regex=True)
        self.assertEqual(output.reconstruct(),
                {"rp":{"1":{"NX-OSv Supervisor Module":{"model":"N7K-SUP1","slot/world_wide_name":"--","mac_address":"5e-00-40-01-00-00 to 5e-00-40-01-07-ff"}}},"lc":{"2":{"NX-OSv Ethernet Module":{"model":"N7K-F248XP-25","slot/world_wide_name":"--","mac_address":"02-00-0c-00-02-00 to 02-00-0c-00-02-7f"}},"3":{"NX-OSv Ethernet Module":{"model":"N7K-F248XP-25","slot/world_wide_name":"--","mac_address":"02-00-0c-00-03-00 to 02-00-0c-00-03-7f"}},"4":{"NX-OSv Ethernet Module":{"model":"N7K-F248XP-25","mac_address":"02-00-0c-00-04-00 to 02-00-0c-00-04-7f"}}}})

        output = mod.contains_key_value('model', 'N7K')
        self.assertEqual(output.reconstruct(), {})

        output = mod.contains_key_value('ports', 'N7K.*', value_regex=True)
        self.assertEqual(output.reconstruct(), {})

        output = mod.contains_key_value('slot/world_wide_name', [1,2,3])
        self.assertEqual(output.reconstruct(),
                {'lc': {'4': {'NX-OSv Ethernet Module': {'slot/world_wide_name': [1, 2, 3]}}}})

        output = mod_t.contains_key_value('slot/world_wide_name',[1,2,3])
        self.assertEqual(output.reconstruct(),
                {'lc': {'2': {'NX-OSv Ethernet Module': {'slot/world_wide_name': [1, 2, 3]}}, '4': {'NX-OSv Ethernet Module': {'slot/world_wide_name': [1, 2, 3]}}}})

        output = mod_t.contains_key_value('slot/world_wide_name',[1,2,3], value_regex=True)
        self.assertEqual(output.reconstruct(), {})

        output = mod_t.contains_key_value('list.*', [1,2,3], key_regex=True)
        self.assertEqual(output.reconstruct(),
                {'rp': {'1': {'NX-OSv Supervisor Module': {'list_d': [1, 2, 3]}}}, 'lc': {'3': {'NX-OSv Ethernet Module': {'list_c': [1, 2, 3]}}, '4': {'NX-OSv Ethernet Module': {'list_a': [1, 2, 3]}}}})

        output = os.contains_key_value('id.*', ['111.87.5.253', '1.1.1.1', '9.8.166.1'], key_regex=True)
        self.assertEqual(output.reconstruct(),
                {'ospf-neighbor-information': {'ospf-neighbor': [{'neighbor-id': {'id1': ['111.87.5.253','1.1.1.1','9.8.166.1']}}]}})

        item = [{'activity-timer': '35', 'interface-name': 'ge-0/0/0.0', 'neighbor-address': ['111.87.5.94', '1.2.3.4', '0.0.0.0', '2.2.3.4'], 'neighbor-id': {'id1': ['111.87.5.253', '1.1.1.1', '9.8.166.1']}, 'neighbor-priority': '128', 'ospf-neighbor-state': 'Full'}, {'activity-timer': '34', 'interface-name': 'ge-0/0/1.0', 'neighbor-address': ['106.187.14.121', '2.2.2.2'], 'neighbor-id': {'id2': ['106.187.14.240']}, 'neighbor-priority': '128', 'ospf-neighbor-state': 'Full'}, {'activity-timer': '32', 'interface-name': 'ge-0/0/2.0', 'neighbor-address': ['27.86.198.26'], 'neighbor-id': {'id3': ['27.86.198.239', '1.2.66.77']}, 'neighbor-priority': '1', 'ospf-neighbor-state': 'Full'}]
        output = os.contains_key_value('ospf-neighbor', item)
        self.assertEqual(output.reconstruct(), os.reconstruct())

        parsed_output_dq = Dq(parsed_output)
        output = parsed_output_dq.contains_key_value('process', '*Init*', value_regex=True, escape_special_chars_value=['*'])
        self.assertEqual(output.reconstruct(),
                {'pid': {'0': {'index': {'1': {'process': '*Init*'}}}}})

        output = parsed_output_dq.contains_key_value('process', '*Init$', value_regex=True, escape_special_chars_value=['*'])
        self.assertEqual(output.reconstruct(), {})

        output = parsed_output_dq.contains_key_value('CHECKSUM', '0x1abc', key_regex=True, ignore_case_key=True)
        self.assertEqual(output.reconstruct(), {'pid': {'0': {'index': {'1': {'checkSum': '0x1abc'}}}}})

        output = parsed_output_dq.contains_key_value('checkSum', '0x1ABC',value_regex=True, ignore_case_value=True).get_values('checkSum')
        self.assertEqual(output[0], '0x1abc')

        # There is a issue with reconstructing this form of output that need to be resolved in pyats
        # currently this is considered as limitation
        # output = mod_t.contains_key_value('a', [1,2,3])
        # self.assertEqual(output.reconstruct(), 
        #         {'rp': {'1': {'NX-OSv Supervisor Module': {'slot/world_wide_name': [{'a': [1,2,3]}]}}}})


    def test_contains_key_value_not_leaf(self):
        mod = Dq(module)
        output = mod.contains_key_value('rp', '1')
        self.assertEqual(output.reconstruct(),
                {'rp': {'1': {'NX-OSv Supervisor Module': {'ports': '0', 'model': 'N7K-SUP1', 'status': 'active', 'software': '7.3(0)D1(1)', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '5e-00-40-01-00-00 to 5e-00-40-01-07-ff', 'serial_number': 'TM40010000B'}}}})

        output = mod.contains_key_value('NX-OSv.*', '.*ware', key_regex=True, value_regex=True)
        self.assertEqual(output.reconstruct(),
                {"rp":{"1":{"NX-OSv Supervisor Module":{"software":"7.3(0)D1(1)","hardware":"0.0"}}},"lc":{"2":{"NX-OSv Ethernet Module":{"software":"NA","hardware":"0.0"}},"3":{"NX-OSv Ethernet Module":{"software":"NA","hardware":"0.0"}},"4":{"NX-OSv Ethernet Module":{"software":"NA","hardware":"0.0"}}}})

        output = mod.contains_key_value('[1,2,3]', 'NX-OSv Ethernet Module', key_regex=True)
        self.assertEqual(output.reconstruct(),
                {"lc":{"2":{"NX-OSv Ethernet Module":{"ports":"48","model":"N7K-F248XP-25","status":"ok","software":"NA","hardware":"0.0","slot/world_wide_name":"--","mac_address":"02-00-0c-00-02-00 to 02-00-0c-00-02-7f","serial_number":"TM40010000C"}},"3":{"NX-OSv Ethernet Module":{"ports":"48","model":"N7K-F248XP-25","status":"ok","software":"NA","hardware":"0.0","slot/world_wide_name":"--","mac_address":"02-00-0c-00-03-00 to 02-00-0c-00-03-7f","serial_number":"TM40010000D"}}}})

    def test_not_contains_key_value_not_leaf(self):
        mod = Dq(module)
        output = mod.not_contains_key_value('rp', '1')
        self.assertEqual(output.reconstruct(),
                {'lc': {'2': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-02-00 to 02-00-0c-00-02-7f', 'serial_number': 'TM40010000C'}}, '3': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-03-00 to 02-00-0c-00-03-7f', 'serial_number': 'TM40010000D'}}, '4': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': [1, 2, 3], 'mac_address': '02-00-0c-00-04-00 to 02-00-0c-00-04-7f', 'serial_number': 'TM40010000E'}}}})

        output = mod.not_contains_key_value('RP', '1', key_regex=True, ignore_case_key=True)
        self.assertEqual(output.reconstruct(),
                {'lc': {'2': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-02-00 to 02-00-0c-00-02-7f', 'serial_number': 'TM40010000C'}}, '3': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-03-00 to 02-00-0c-00-03-7f', 'serial_number': 'TM40010000D'}}, '4': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': [1, 2, 3], 'mac_address': '02-00-0c-00-04-00 to 02-00-0c-00-04-7f', 'serial_number': 'TM40010000E'}}}})

        output = mod.not_contains_key_value('rp', '1').not_contains('4').not_contains_key_value('lc', '3')
        self.assertEqual(output.reconstruct(),
                {'lc': {'2': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-02-00 to 02-00-0c-00-02-7f', 'serial_number': 'TM40010000C'}}}})

        output = mod.not_contains_key_value('lc', '(3|4)', value_regex=True).not_contains('N7.*', regex=True).not_contains('NA')
        self.assertEqual(output.reconstruct(), 
                {'rp': {'1': {'NX-OSv Supervisor Module': {'ports': '0', 'status': 'active', 'software': '7.3(0)D1(1)', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '5e-00-40-01-00-00 to 5e-00-40-01-07-ff', 'serial_number': 'TM40010000B'}}}, 'lc': {'2': {'NX-OSv Ethernet Module': {'ports': '48', 'status': 'ok', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-02-00 to 02-00-0c-00-02-7f', 'serial_number': 'TM40010000C'}}}})

    def test_contains_key_value_regex_equal_contains_key_value(self):
        mod = Dq(module)
        output_regex = mod.contains_key_value('NX-NX-OSv Ethernet Module', 'hardware', key_regex=True, value_regex=True)
        output =   mod.contains_key_value('NX-NX-OSv Ethernet Module', 'hardware')
        self.assertEqual(output_regex.reconstruct(), output.reconstruct())
    
    def test_contains_key_equal_contains(self):
        mod = Dq(module)
        self.assertEqual(mod.contains('N7K-F248XP-25'),
                         mod.contains_key_value('model', 'N7K-F248XP-25'))

        self.assertEqual(mod.contains('mac_address'),
                         mod.contains_key_value('mac_address', r'[a-z0-9\-\s]+', value_regex=True))

        self.assertEqual(mod.contains('0.0'), 
                         mod.contains_key_value('.*ware', '0.0', key_regex=True))

    def test_count(self):
        mod = Dq(module)
        self.assertEqual(mod.contains('N7K-F248XP-25').count(), 3)

    def test_count_not_exists(self):
        mod = Dq(module)
        self.assertEqual(mod.contains('dont exists').count(), 0)

    def test_raw(self):
        mod = Dq(module)
        self.assertEqual(mod.raw("[rp][1][NX-OSv Supervisor Module]"),
                {'ports': '0', 'model': 'N7K-SUP1', 'status': 'active', 'software': '7.3(0)D1(1)', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '5e-00-40-01-00-00 to 5e-00-40-01-07-ff', 'serial_number': 'TM40010000B'})

        self.assertEqual(mod.raw("[rp][1][NX-OSv Supervisor Module][model][0]"), 'N')

    def test_raw_error(self):
        mod = Dq(module)
        with self.assertRaises(KeyError):
            mod.raw("[rp][1][NX-OSv Su]")

    def test_sum_value_operator(self):
        cpu = Dq(cpu_load)
        output = cpu.sum_value_operator('value', '>', 3)
        self.assertEqual(output.reconstruct(),
                {'value': 30.0})

        output = cpu.sum_value_operator('value', '<', 90)
        self.assertEqual(output.reconstruct(),
                {'value': 30.0})

        output = cpu.sum_value_operator('value', '<=', 30)
        self.assertEqual(output.reconstruct(),
                {'value': 30.0})

        output = cpu.sum_value_operator('value', '>=', 30)
        self.assertEqual(output.reconstruct(),
                {'value': 30.0})

        output = cpu.sum_value_operator('value', '==', 30)
        self.assertEqual(output.reconstruct(),
                {'value': 30.0})

        output = cpu.sum_value_operator('value', '!=', 15)
        self.assertEqual(output.reconstruct(),
                {'value': 30.0})

        output = cpu.sum_value_operator('value', '!=', 30)
        self.assertEqual(output.reconstruct(),
                {})

    def test_value_operator_greater(self):
        mod = Dq(module)
        output = mod.value_operator('lc', '>', '3')
        self.assertEqual(output.reconstruct(),
                {'lc': {'4': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': [1, 2, 3], 'mac_address': '02-00-0c-00-04-00 to 02-00-0c-00-04-7f', 'serial_number': 'TM40010000E'}}}})

        self.assertEqual(output.contains('1').count(), 0)
        self.assertEqual(output.contains('2').count(), 0)
        self.assertEqual(output.contains('3').count(), 0)
        self.assertEqual(output.contains('4').count(), 10)

        output = mod.value_operator('lc', '<', '3')
        self.assertEqual(output.contains('1').count(), 0)
        self.assertEqual(output.contains('2').count(), 8)
        self.assertEqual(output.contains('3').count(), 0)
        self.assertEqual(output.contains('4').count(), 0)

        output = mod.value_operator('lc', '<=', '3')
        self.assertEqual(output.contains('1').count(), 0)
        self.assertEqual(output.contains('2').count(), 8)
        self.assertEqual(output.contains('3').count(), 8)
        self.assertEqual(output.contains('4').count(), 0)

        output = mod.value_operator('lc', '>=', '3')
        self.assertEqual(output.contains('1').count(), 0)
        self.assertEqual(output.contains('2').count(), 0)
        self.assertEqual(output.contains('3').count(), 8)
        self.assertEqual(output.contains('4').count(), 10)

        output = mod.value_operator('lc', '==', '3')
        self.assertEqual(output.contains('1').count(), 0)
        self.assertEqual(output.contains('2').count(), 0)
        self.assertEqual(output.contains('3').count(), 8)
        self.assertEqual(output.contains('4').count(), 0)

        output = mod.value_operator('lc', '!=', '3')
        self.assertEqual(output.contains('1').count(), 0)
        self.assertEqual(output.contains('2').count(), 8)
        self.assertEqual(output.contains('3').count(), 0)
        self.assertEqual(output.contains('4').count(), 10)

    def test_get_values(self):
        mod = Dq(module)
        self.assertEqual(mod.get_values('lc'), ['2', '3', '4'])

        os = Dq(ospf)
        self.assertEqual(os.get_values('ospf-neighbor'), 
                        [{"activity-timer":"35","interface-name":"ge-0/0/0.0","neighbor-address":["111.87.5.94", '1.2.3.4', '0.0.0.0', '2.2.3.4'],"neighbor-id":{'id1':["111.87.5.253", '1.1.1.1', '9.8.166.1']},"neighbor-priority":"128","ospf-neighbor-state":"Full"},{"activity-timer":"34","interface-name":"ge-0/0/1.0","neighbor-address":["106.187.14.121", '2.2.2.2'],"neighbor-id":{'id2':["106.187.14.240"]},"neighbor-priority":"128","ospf-neighbor-state":"Full"},{"activity-timer":"32","interface-name":"ge-0/0/2.0","neighbor-address":["27.86.198.26"],"neighbor-id":{'id3':["27.86.198.239", '1.2.66.77']},"neighbor-priority":"1","ospf-neighbor-state":"Full"}])

        self.assertEqual(os.get_values('activity-timer'), ['35', '34', '32'])

        self.assertEqual(os.get_values('neighbor-priority'), ['128', '128', '1'])

        self.assertEqual(os.get_values('neighbor-address'), ['111.87.5.94', '1.2.3.4', '0.0.0.0', '2.2.3.4', "106.187.14.121", '2.2.2.2', '27.86.198.26'])

        self.assertEqual(os.get_values('neighbor-id'), ['id1', 'id2', 'id3'])

        self.assertEqual(os.get_values('id1'), ["111.87.5.253", '1.1.1.1', '9.8.166.1'])

    def test_get_value_index(self):
        mod = Dq(module)
        self.assertEqual(mod.get_values('[1]'), ['1', '2', '3', '4'])

        # index
        self.assertEqual(mod.get_values('[1]', 2), '3')

        # slicing-1
        self.assertEqual(mod.get_values('[1]', '[2:]'), ['3', '4'])

        # slicing-2
        self.assertEqual(mod.get_values('[1]', '[1:2]'), ['2'])

        # slicing-3
        self.assertEqual(mod.get_values('[1]', '[:2]'), ['1', '2'])

        # slicing-4
        self.assertEqual(mod.get_values('[1]', '[:]'), ['1', '2', '3', '4'])

        # out of range
        self.assertEqual(mod.get_values('[1]', 7), [])

        os = Dq(ospf)
        self.assertEqual(os.get_values('ospf-neighbor', index=1), 
                        {"activity-timer":"34","interface-name":"ge-0/0/1.0","neighbor-address":["106.187.14.121", '2.2.2.2'],"neighbor-id":{'id2':["106.187.14.240"]},"neighbor-priority":"128","ospf-neighbor-state":"Full"})

    def test_get_value_index_error(self):
        mod = Dq(module)
        self.assertEqual(mod.get_values('[7]'), [])

    def test_get_value_leaf(self):
        mod = Dq(module)
        self.assertEqual(mod.get_values('model'), ['N7K-SUP1', 'N7K-F248XP-25', 'N7K-F248XP-25', 'N7K-F248XP-25'])

    def test_get_value_first_index_error(self):
        mod = Dq({})
        self.assertEqual(mod.get_values(None), [])

    def test_query_validator_valid_single_function_without_args(self):
        mod = Dq(module)
        query = "count()"
        self.assertEqual(mod.query_validator(query), True)

    def test_query_validator_valid_single_function_with_args(self):
        mod = Dq(module)
        query = "contains('test1', 'test2')"
        self.assertEqual(mod.query_validator(query), True)

    def test_query_validator_nested_functions(self):
        mod = Dq(module)
        query = r"contains('%VARIABLES{abc}\.\d+', regex=True).contains_key_value('key1', 'key2').count()"

        self.assertEqual(mod.query_validator(query), True)

    def test_str_to_dq_query_with_args(self):
        mod = Dq(module)
        query = 'contains("holding")'
        result = {'pid': {'0': {'index': {'1': {'holding': 158001024}}}}}

        self.assertEqual(mod.str_to_dq_query(parsed_output, query), result)

    def test_str_to_dq_query_with_no_args(self):
        mod = Dq(module)
        query = 'contains("holding").count()'
        result = 1

        self.assertEqual(mod.str_to_dq_query(parsed_output, query), result)

    def test_first_item_empty_list(self):
        mod = Dq({'name': [[], ['test']], 'test': [1, 2, 3]})
        self.assertEqual(mod.get_values('name'), [[], ['test']])


if __name__ == '__main__':
    unittest.main()
