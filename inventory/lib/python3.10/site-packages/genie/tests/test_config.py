import unittest

from genie.utils.config import Config

class test_Config(unittest.TestCase):

    def test_config_1(self):
        output = '''\
a
 aa
   aaa
 ab
b
 bb
c
d'''
        config = Config(output)
        self.assertTrue(isinstance(config, Config))
        config.tree()
        self.assertEqual(config.config,
                {'a': {'aa': {'aaa': {}}, 'ab': {}},
                 'b': {'bb': {}}, 'c': {}, 'd': {}})

    def test_config_2(self):
        output = '''\
a
b
c
d'''
        config = Config(output)
        self.assertTrue(isinstance(config, Config))
        config.tree()
        self.assertEqual(config.config,
                {'a': {}, 'b': {}, 'c': {}, 'd': {}})

    def test_config_3(self):
        output = '''\
a a d f
b
c d f
 d f gi
  f
d'''
        config = Config(output)
        self.assertTrue(isinstance(config, Config))
        config.tree()
        self.assertEqual(config.config,
                {'a a d f': {}, 'c d f': {'d f gi': {'f': {}}},
                 'b': {}, 'd': {}})

    def test_config_4(self):
        # Simulating a MOTD which doesnt need to respect the indent rule
        output = '''\
a a d f
b
motd
   qw
  w
 z
mot2
 q
  q
    q
 w
c d f
 d f gi
  f
d'''
        config = Config(output)
        self.assertTrue(isinstance(config, Config))
        config.tree()
        self.assertEqual(config.config,
                {'a a d f': {}, 'motd': {'qw': {}},
                 'w': {'z': {}}, 'b': {}, 'd': {},
                 'mot2': {'q': {'q': {'q': {}}},
                 'w': {}}, 'c d f': {'d f gi': {'f': {}}}})



    def test_config_json(self):
        # Some device type returns Json - SONiC
        output = '''\
{
    "AAA": {
        "authentication": {
            "login": "tacacs+"
        }
    },
    "ACL_RULE": {
        "TEST_ACL_TABLE|DROP_ON_ETH68": {
            "PRIORITY": "1100",
            "SRC_IP": "10.2.2.2/30",
            "DST_IP": "ANY",
            "PACKET_ACTION": "DROP",
            "IP_TYPE": "ANY"
        }
    },
    "PORT": {
        "Ethernet0": {
            "alias": "Eth1",
            "lanes": "11,22,33,44",
            "description": "Nope",
            "speed": "100000",
            "mtu": "9100"
        },
        "Ethernet4": {
            "alias": "Eth2",
            "lanes": "55,43,12,22",
            "description": "Yep",
            "speed": "100000",
            "mtu": "9100"
        }
   }
}'''
        config = Config(output)
        self.assertTrue(isinstance(config, Config))
        config.tree()
        self.assertEqual(config.config,
            {'ACL_RULE': {'TEST_ACL_TABLE|DROP_ON_ETH68': {'SRC_IP': '10.2.2.2/30', 'PACKET_ACTION': 'DROP', 'DST_IP': 'ANY', 'IP_TYPE': 'ANY', 'PRIORITY': '1100'}}, 'AAA': {'authentication': {'login': 'tacacs+'}}, 'PORT': {'Ethernet0': {'description': 'Nope', 'speed': '100000', 'lanes': '11,22,33,44', 'alias': 'Eth1', 'mtu': '9100'}, 'Ethernet4': {'description': 'Yep', 'speed': '100000', 'lanes': '55,43,12,22', 'alias': 'Eth2', 'mtu': '9100'}}})


    def test_config_5(self):
        # test exclude ^C
        output = '''\
            banner motd \x03CC
            =============================================================

             If you don't have permission to access this router,
             please shut your session right now.

             Go! Global! Go!

            =============================================================
            \x03
            !
        '''
        config = Config(output)
        self.assertTrue(isinstance(config, Config))
        config.tree()
        self.assertEqual(config.config,
                {'banner motd ^CCC': {}, 
                 '=============================================================': {},
                 '^C': {}})


if __name__ == '__main__':
    unittest.main()

