import unittest

from genie.utils.diff import Diff, ModifiedItem
from genie.conf.base import Testbed
from genie.decorator import managedattribute
from genie.conf.base import DeviceFeature
from genie.conf.base.attributes import SubAttributes, SubAttributesDict,\
                                       AttributesHelper, KeyedSubAttributes,\
                                       DeviceSubAttributes

from genie.utils.config import Config

from genie.conf.base import DeviceFeature, LinkFeature
from genie.conf.base import ConfigurableBase
from genie.conf.base.attributes import KeyedSubAttributes

from genie.ops.base import Base


class Bgp(Base):
    info = {}

class Routing(ConfigurableBase):
    pass

class test_Diffdict(unittest.TestCase):

    def test_init(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = a

        dd = Diff(a,b)
        dd.d1 = a
        dd.d2 = b
    def test_same_dict(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = a

        dd = Diff(a, b)
        dd.findDiff()
        self.assertEqual(str(dd), '')

    def test_config_object_corner_case1(self):
        x = Config('interface loopback3\n no shutdown')
        y = Config('interface loopback3')
        x.tree()
        y.tree()

        dd = Diff(y, x)
        dd.findDiff()
        self.assertEqual(str(dd), ' interface loopback3\n+ no shutdown')

    def test_diff_dict(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = {'a':5, 'f':7, 'c':{'ca':8, 'cb':9}}

        dd = Diff(a,b)
        dd.findDiff()
        self.assertEqual(str(dd), '+f: 7\n-b: 7')

    def test_modified_dict(self):
        a = {'a':5, 'b':7, 'c':{'cc':7, 'cb':9}}
        b = {'a':5, 'b':7, 'c':{'cc':8, 'cb':9}}

        dd = Diff(a,b)
        dd.findDiff()
        self.assertEqual(str(dd), ' c:\n- cc: 7\n+ cc: 8')

    def test_diff_dict2(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = {'a':5, 'b':7, 'c':{'cc':8, 'cb':9}}

        dd = Diff(a,b)
        dd.findDiff()
        self.assertEqual(str(dd), ' c:\n- ca: 8\n+ cc: 8')

    def test_diff_added(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = {'a':5, 'b':7, 'c':{'cc':8, 'cb':2, 'cd':{'d':5, 'f':2}}}

        dd = Diff(a,b, mode='add')
        dd.findDiff()
        self.assertEqual(len(dd.diffs), 1)
        self.assertEqual(str(dd),
                    ' c:\n+ cc: 8\n+ cd:\n+  d: 5\n+  f: 2')
        self.assertTrue(isinstance(dd.diffs[0], ModifiedItem))
        self.assertEqual(len(dd.diffs[0].items), 2)

        self.assertEqual(dd.diffs[0].items[0].path, 'c')
        self.assertEqual(dd.diffs[0].items[0].item, 'cc')
        self.assertEqual(dd.diffs[0].items[0].value, 8)
        self.assertEqual(dd.diffs[0].items[1].path, 'c')
        self.assertEqual(dd.diffs[0].items[1].item, 'cd')
        self.assertEqual(dd.diffs[0].items[1].value, {'d': 5, 'f': 2})

    def test_diff_added2(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = {'a':5, 'k':7, 'c':{'cc':8, 'cb':2}}

        dd = Diff(a,b, mode='add')
        dd.findDiff()
        self.assertEqual(len(dd.diffs), 2)
        self.assertEqual(dd.diffs[0].path, "")
        self.assertEqual(dd.diffs[0].item, "k")
        self.assertEqual(dd.diffs[0].value, 7)
        self.assertEqual(dd.diffs[1].items[0].path, "c")
        self.assertEqual(dd.diffs[1].items[0].item, "cc")
        self.assertEqual(dd.diffs[1].items[0].value, 8)
        self.assertEqual(str(dd), "+k: 7\n c:\n+ cc: 8")

        dd = Diff(a,b, mode='remove')
        dd.findDiff()
        self.assertEqual(len(dd.diffs), 2)
        self.assertEqual(str(dd), "-b: 7\n c:\n- ca: 8")


        dd = Diff(a,b, mode='modified')
        dd.findDiff()
        self.assertEqual(len(dd.diffs), 1)
        self.assertEqual(str(dd), ' c:\n- cb: 9\n+ cb: 2')

    def test_diff_removed(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = {'a':5, 'b':7, 'c':{'cc':8, 'cb':9}}

        dd = Diff(b,a, mode='add')
        dd.findDiff()
        self.assertEqual(len(dd.diffs), 1)
        self.assertEqual(dd.diffs[0].items[0].path, "c")
        self.assertEqual(dd.diffs[0].items[0].item, "ca")
        self.assertEqual(dd.diffs[0].items[0].value, 8)
        self.assertEqual(str(dd), ' c:\n+ ca: 8')

        dd = Diff(b,a, mode='remove')
        dd.findDiff()
        self.assertEqual(len(dd.diffs), 1)
        self.assertEqual(str(dd), ' c:\n- cc: 8')
        self.assertEqual(dd.diffs[0].items[0].path, "c")
        self.assertEqual(dd.diffs[0].items[0].item, "cc")
        self.assertEqual(dd.diffs[0].items[0].value, 8)

        dd = Diff(b,a, mode='modified')
        dd.findDiff()
        self.assertEqual(str(dd), "")

    def test_diff_removed2(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = {'a':5, 'k':7, 'c':{'cc':8, 'cb':9}}

        dd = Diff(b,a, mode='add')
        dd.findDiff()
        self.assertEqual(len(dd.diffs), 2)
        self.assertEqual(dd.diffs[0].path, "")
        self.assertEqual(dd.diffs[0].item, "b")
        self.assertEqual(dd.diffs[0].value, 7)
        self.assertEqual(dd.diffs[1].items[0].path, "c")
        self.assertEqual(dd.diffs[1].items[0].item, "ca")
        self.assertEqual(dd.diffs[1].items[0].value, 8)
        self.assertEqual(str(dd), '+b: 7\n c:\n+ ca: 8')

        dd = Diff(b,a, mode='remove')
        dd.findDiff()
        self.assertEqual(len(dd.diffs), 2)
        self.assertEqual(dd.diffs[0].path, "")
        self.assertEqual(dd.diffs[0].item, "k")
        self.assertEqual(dd.diffs[0].value, 7)
        self.assertEqual(dd.diffs[1].items[0].path, "c")
        self.assertEqual(dd.diffs[1].items[0].item, "cc")
        self.assertEqual(dd.diffs[1].items[0].value, 8)
        self.assertEqual(str(dd), "-k: 7\n c:\n- cc: 8")

        dd = Diff(b,a, mode='modified')
        dd.findDiff()
        self.assertEqual(str(dd), "")

    def test_diff_modified_1(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        c = {'a':5, 'b':7, 'c':{'ca':9, 'cb':9}}

        dd = Diff(a,c, mode='modified')
        dd.findDiff()

        self.assertEqual(len(dd.diffs), 1)
        self.assertEqual(str(dd), ' c:\n- ca: 8\n+ ca: 9')

    def test_diff_modified(self):
        a = {'a':5, 'b':4, 'c':{'ca':{'d':8, 'x':2, 'e':3, 'w':3}, 'v':2, 'cb':9}}
        c = {'a':5, 'd':3, 'b':7, 'c':{'ca':{'d':9, 'e':2, 'ff':3, 'w':{'s':3}}, 'cb':9}}

        dd = Diff(a, c, mode='modified')
        dd.findDiff()

        self.assertEqual(len(dd.diffs), 2)
        self.assertEqual(str(dd),
                '-b: 4\n+b: 7\n c:\n  ca:\n-  d: 8\n+  d: 9\n-  e: 3\n+  '\
                'e: 2\n-  w: 3\n+  w:\n+   s: 3')

    def test_diff_modified_exclude_value(self):
        a = {'a':5, 'b':4, 'c':{'ca':{'d':8, 'x':2, 'e':3, 'w':3}, 'v':2, 'cb':9}}
        c = {'a':5, 'd':3, 'b':7, 'c':{'ca':{'d':9, 'e':2, 'ff':3, 'w':{'s':3}}, 'cb':9}}

        dd = Diff(a, c, mode='modified', exclude='b')
        dd.findDiff()

        self.assertEqual(len(dd.diffs), 1)
        self.assertEqual(str(dd),
                ' c:\n  ca:\n-  d: 8\n+  d: 9\n-  e: 3\n+  e: 2\n-  w: 3\n+  '\
                'w:\n+   s: 3')

    def test_diff_modified_exclude_value_regex(self):
        a = {'a':5, 'b':4, 'c':{'ca':{'d':8, 'x':2, 'e':3, 'w':3}, 'v':2, 'cb':9}}
        c = {'a':5, 'd':3, 'b':7, 'c':{'ca':{'d':9, 'e':2, 'ff':3, 'w':{'s':3}}, 'cb':9}}

        dd = Diff(a, c, mode='modified', exclude='(b.*)')
        dd.findDiff()

        self.assertEqual(len(dd.diffs), 1)
        self.assertEqual(str(dd),
                ' c:\n  ca:\n-  d: 8\n+  d: 9\n-  e: 3\n+  e: 2\n-  w: 3\n+  '\
                'w:\n+   s: 3')

    def test_diff_modified_exclude_list_value(self):
        a = {'a':5, 'b':4, 'c':{'ca':{'d':8, 'x':2, 'e':3, 'w':3}, 'v':2, 'cb':9}}
        c = {'a':5, 'd':3, 'b':7, 'c':{'ca':{'d':9, 'e':2, 'ff':3, 'w':{'s':3}}, 'cb':9}}

        dd = Diff(a, c, mode='modified', exclude=['b'])
        dd.findDiff()

        self.assertEqual(len(dd.diffs), 1)
        self.assertEqual(str(dd),
                ' c:\n  ca:\n-  d: 8\n+  d: 9\n-  e: 3\n+  e: 2\n-  w: 3\n+  '\
                'w:\n+   s: 3')

    def test_diff_modified_exclude_list_regex(self):
        a = {'a':5, 'b':4, 'c':{'ca':{'d':8, 'x':2, 'e':3, 'w':3}, 'v':2, 'cb':9}}
        c = {'a':5, 'd':3, 'b':7, 'c':{'ca':{'d':9, 'e':2, 'ff':3, 'w':{'s':3}}, 'cb':9}}

        dd = Diff(a, c, mode='modified', exclude=['(b.*)'])
        dd.findDiff()

        self.assertEqual(len(dd.diffs), 1)
        self.assertEqual(str(dd),
                ' c:\n  ca:\n-  d: 8\n+  d: 9\n-  e: 3\n+  e: 2\n-  w: 3\n+  '\
                'w:\n+   s: 3')

    def test_diff_modified_exclude_list_wrong_regex(self):
        a = {'a':5, 'b':4, 'c':{'ca':{'d':8, 'x':2, 'e':3, 'w':3}, 'v':2, 'cb':9}}
        c = {'a':5, 'd':3, 'b':7, 'c':{'ca':{'d':9, 'e':2, 'ff':3, 'w':{'s':3}}, 'cb':9}}

        with self.assertRaises(ValueError):
            dd = Diff(a, c, mode='modified', exclude=['([]b.*)'])

    def test_diff_string_add(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = {'a': 15, 'dd': 123, 'cc': 234}

        dd = Diff(a, b)
        dd.findDiff()
        self.assertEqual(dd.diff_string('+'), 'cc 234\ndd 123')

        a = {'a': 15, 'dd': 123, 'cc': 234}
        b = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}, 'd': {'w': {'z': {'v': 123, 'd': 56}}}}

        dd = Diff(a, b)
        dd.findDiff()
        self.assertEqual(dd.diff_string('+'), 'b 7\nc\n ca 8\n cb 9\nd\n w\n  z\n   d 56\n   v 123')

    def test_diff_string_remove(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = {}

        dd = Diff(a, b)
        dd.findDiff()
        self.assertEqual(dd.diff_string('-'), 'a 5\nb 7\nc\n ca 8\n cb 9')

    def test_diff_string_empty(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = a

        dd = Diff(a, b)
        dd.findDiff()
        self.assertEqual(dd.diff_string('+'), '')

    def test_diff_string_empty2(self):
        a = {'a': 15}
        b = {'b': 16}
        
        dd= Diff(a, b)
        self.assertEqual(dd.diff_string('+'), '')

    def test_diff_string_invalid(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = a

        dd = Diff(a, b)
        dd.findDiff()
        with self.assertRaises(ValueError):
            dd.diff_string('b')

    def test_diff_verbose(self):
        before = {
            'ospf-neighbor-information': {
                'ospf-neighbor': [{
                        'activity-timer': '34',
                        'interface-name': 'ge-0/0/0.0',
                        'neighbor-address': '111.87.5.94',
                        'neighbor-id': '111.87.5.253',
                        'neighbor-priority': '128',
                        'ospf-neighbor-state': 'Full'
                    }, {
                        'activity-timer': '38',
                        'interface-name': 'ge-0/0/1.0',
                        'neighbor-address': '106.187.14.121',
                        'neighbor-id': '106.187.14.240',
                        'neighbor-priority': '128',
                        'ospf-neighbor-state': 'Full'
                    }
                ]
            }
        }
        after = {
            'ospf-neighbor-information': {
                'ospf-neighbor': [{
                        'activity-timer': '34',
                        'interface-name': 'ge-0/0/0.0',
                        'neighbor-address': '111.87.5.94',
                        'neighbor-id': '111.87.5.253',
                        'neighbor-priority': '128',
                        'ospf-neighbor-state': 'Full'
                    }, {
                        'activity-timer': '40',
                        'interface-name': 'ge-0/0/1.0',
                        'neighbor-address': '106.187.14.121',
                        'neighbor-id': '106.187.14.240',
                        'neighbor-priority': '128',
                        'ospf-neighbor-state': 'Full'
                    }
                ]
            }
        }
        dd = Diff(before, after, verbose=True)
        dd.findDiff()
        expected = """ ospf-neighbor-information:
  ospf-neighbor:
   index[1]:
-   activity-timer: 38
+   activity-timer: 40
    interface-name: ge-0/0/1.0
    neighbor-address: 106.187.14.121
    neighbor-id: 106.187.14.240
    neighbor-priority: 128
    ospf-neighbor-state: Full"""
        self.assertEqual(str(dd), expected)

    def test_diff_verbose_nested(self):
        before = {
            'a': [ { 'b': [{ 'c': 1, 'm': 3, 'w': 4 }], 'f': 0 }],
            'c': 1
        }

        after = {
            'a': [ { 'b': [{ 'c': 7, 'm': 3, 'w': 4 }], 'f': 0 }],
            'b': 'w',
            'c': 1
        }
        dd = Diff(before, after, verbose=True)
        dd.findDiff()
        with open('/tmp/ws', 'w') as f:
            f.write(str(dd))
        expected = """+b: w
 a:
  index[0]:
   b:
    index[0]:
-    c: 1
+    c: 7
     m: 3
     w: 4"""
        self.assertEqual(str(dd), expected)

    def test_diff_verbose_multiple_elements(self):
        before = {
        'a':[{ 'a': 1, 'b': 2, 'c': 3 }, { 'a': 1, 'b': 2, 'c': 3 }, { 'a': 1, 'b': 2, 'c': 3 }]
        }
        after = {
        'a':[{ 'a': 1, 'b': 9, 'c': 9 }, { 'a': 7, 'b': 6, 'c': 3 }, { 'a': 1, 'b': 9, 'c': 3 }]
        }
        dd = Diff(before, after, verbose=True)
        dd.findDiff()
        expected = """ a:
  index[0]:
   a: 1
-  b: 2
+  b: 9
-  c: 3
+  c: 9
  index[1]:
-  a: 1
+  a: 7
-  b: 2
+  b: 6
   c: 3
  index[2]:
   a: 1
-  b: 2
+  b: 9
   c: 3"""
        self.assertEqual(str(dd), expected)

    def test_diff_modified_with_verbose(self):
        a = {'a':5, 'b':4, 'c':{'ca':{'d':8, 'x':2, 'e':3, 'w':3}, 'v':2, 'cb':9}}
        c = {'a':5, 'd':3, 'b':7, 'c':{'ca':{'d':9, 'e':2, 'ff':3, 'w':{'s':3}}, 'cb':9}}

        dd = Diff(a, c, mode='modified', verbose=True)
        dd.findDiff()

        self.assertEqual(len(dd.diffs), 2)
        self.assertEqual(str(dd),
                '-b: 4\n+b: 7\n c:\n  ca:\n-  d: 8\n+  d: 9\n-  e: 3\n+  '\
                'e: 2\n-  w: 3\n+  w:\n+   s: 3')

    def test_diff_added_with_verbose(self):
        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':9}}
        b = {'a':5, 'b':7, 'c':{'cc':8, 'cb':2, 'cd':{'d':5, 'f':2}}}

        dd = Diff(a,b, mode='add', verbose=True)
        dd.findDiff()
        self.assertEqual(len(dd.diffs), 1)
        self.assertEqual(str(dd),
                    ' c:\n+ cc: 8\n+ cd:\n+  d: 5\n+  f: 2')
        self.assertTrue(isinstance(dd.diffs[0], ModifiedItem))
        self.assertEqual(len(dd.diffs[0].items), 2)

        self.assertEqual(dd.diffs[0].items[0].path, 'c')
        self.assertEqual(dd.diffs[0].items[0].item, 'cc')
        self.assertEqual(dd.diffs[0].items[0].value, 8)
        self.assertEqual(dd.diffs[0].items[1].path, 'c')
        self.assertEqual(dd.diffs[0].items[1].item, 'cd')
        self.assertEqual(dd.diffs[0].items[1].value, {'d': 5, 'f': 2})

    def test_diff_modified_exclude_list_regex_with_verbose(self):
        a = {'a':5, 'b':4, 'c':{'ca':{'d':8, 'x':2, 'e':3, 'w':3}, 'v':2, 'cb':9}}
        c = {'a':5, 'd':3, 'b':7, 'c':{'ca':{'d':9, 'e':2, 'ff':3, 'w':{'s':3}}, 'cb':9}}

        dd = Diff(a, c, mode='modified', exclude=['(b.*)'], verbose=True)
        dd.findDiff()

        self.assertEqual(len(dd.diffs), 1)
        self.assertEqual(str(dd),
                ' c:\n  ca:\n-  d: 8\n+  d: 9\n-  e: 3\n+  e: 2\n-  w: 3\n+  '\
                'w:\n+   s: 3')

    def test_diff_verbose_array_order(self):
        a = { '1': {'value': [1, 2, 3, 4]}}
        b = { '1': {'value': [1, 3, 3, 4]}}
        dd = Diff(a, b, verbose=True)
        dd.findDiff()
        expected = """ 1:
  value:
   index[0]: 1
-  index[1]: 2
+  index[1]: 3
   index[2]: 3
   index[3]: 4"""
        self.assertEqual(str(dd), expected)

    def test_diff_two_trees_both_with_diff(self):
        before = {
            'instance': {
                'default': {
                    'vrf': {
                        'default': {
                            'neighbor': {
                                '1111:2222:3333::4444': {
                                    'address_family': {
                                        'ipv6 unicast': {
                                            'accepted_prefixes': 11
                                        }
                                    }
                                },
                                '1111:2222:3333::5555': {
                                    'address_family': {
                                        'ipv6 unicast': {
                                            'accepted_prefixes': 33,
                                            'test': 123
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        after = {
            'instance': {
                'default': {
                    'vrf': {
                        'default': {
                            'neighbor': {
                                '1111:2222:3333::4444': {
                                    'address_family': {
                                        'ipv6 unicast': {
                                            'accepted_prefixes': 22
                                        }
                                    }
                                },
                                '1111:2222:3333::5555': {
                                    'address_family': {
                                        'ipv6 unicast': {
                                            'accepted_prefixes': 44,
                                            'test': 123
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        dd = Diff(before, after, verbose=True)
        dd.findDiff()
        expected = """ instance:
  default:
   vrf:
    default:
     neighbor:
      1111:2222:3333::4444:
       address_family:
        ipv6 unicast:
-        accepted_prefixes: 11
+        accepted_prefixes: 22
      1111:2222:3333::5555:
       address_family:
        ipv6 unicast:
-        accepted_prefixes: 33
+        accepted_prefixes: 44"""
        self.assertEqual(str(dd), expected)


class Feature(Routing, DeviceFeature, LinkFeature):
    class DeviceAttributes(DeviceSubAttributes):
        class VrfAttributes(KeyedSubAttributes):
            pass

        vrf_attr = managedattribute(
            name='vrf_attr',
            read_only=True,
            doc=VrfAttributes.__doc__)

        @vrf_attr.initter
        def vrf_attr(self):
            return SubAttributesDict(self.VrfAttributes, parent=self)

    name = managedattribute(
        name='name',
        default=None,
        type=managedattribute.test_istype(str))

    a_type = managedattribute(
        name='a_type',
        default=None,
        type=managedattribute.test_istype(str))

    device_attr = managedattribute(
        name='device_attr',
        read_only=True,
        doc=DeviceAttributes.__doc__)

    @device_attr.initter
    def device_attr(self):
        return SubAttributesDict(self.DeviceAttributes, parent=self)


class test_Diffobj(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tb = Testbed()

    def test_same_obj(self):
        f = Feature(testbed=self.tb)
        g = Feature(testbed=self.tb)

        dd = Diff(f, g)
        dd.findDiff()
        self.assertEqual(str(dd), '')

    def test_diff_obj_first_level(self):
        f = Feature(testbed=self.tb)
        g = Feature(testbed=self.tb)

        f.name = 'mine'
        g.name = 'me'

        dd = Diff(f, g)
        dd.findDiff()
        self.assertEqual(len(dd.diffs), 1)
        self.assertEqual(dd.diffs[0].items[0].path, '')
        self.assertEqual(dd.diffs[0].items[0].item, 'name')
        self.assertEqual(dd.diffs[0].items[0].value, 'mine')
        self.assertEqual(dd.diffs[0].items[1].path, '')
        self.assertEqual(dd.diffs[0].items[1].item, 'name')
        self.assertEqual(dd.diffs[0].items[1].value, 'me')
        self.assertEqual(str(dd), '-name: mine\n+name: me')

        dd = Diff(f, g, mode='add')
        dd.findDiff()
        self.assertEqual(str(dd), '')
        dd = Diff(f, g, mode='remove')
        dd.findDiff()
        self.assertEqual(str(dd), '')

        dd = Diff(f, g, mode='modified')
        dd.findDiff()
        self.assertEqual(len(dd.diffs), 1)
        self.assertEqual(dd.diffs[0].items[0].path, '')
        self.assertEqual(dd.diffs[0].items[0].item, 'name')
        self.assertEqual(dd.diffs[0].items[0].value, 'mine')
        self.assertEqual(dd.diffs[0].items[1].path, '')
        self.assertEqual(dd.diffs[0].items[1].item, 'name')
        self.assertEqual(dd.diffs[0].items[1].value, 'me')
        self.assertEqual(str(dd), '-name: mine\n+name: me')

    def test_add_remove_obj_first_level(self):
        f = Feature(testbed=self.tb)
        g = Feature(testbed=self.tb)

        f.name = 'mine'
        f.f_only = 5
        g.name = 'me'
        g.g_only = 5

        dd = Diff(f, g)
        dd.findDiff()
        self.assertEqual(len(dd.diffs), 3)

        self.assertEqual(dd.diffs[0].path, '')
        self.assertEqual(dd.diffs[0].item, 'g_only')
        self.assertEqual(dd.diffs[0].value, 5)

        self.assertEqual(dd.diffs[1].path, '')
        self.assertEqual(dd.diffs[1].item, 'f_only')
        self.assertEqual(dd.diffs[1].value, 5)

        self.assertEqual(dd.diffs[2].items[0].path, '')
        self.assertEqual(dd.diffs[2].items[0].item, 'name')
        self.assertEqual(dd.diffs[2].items[0].value, 'mine')
        self.assertEqual(dd.diffs[2].items[1].path, '')
        self.assertEqual(dd.diffs[2].items[1].item, 'name')
        self.assertEqual(dd.diffs[2].items[1].value, 'me')

        self.assertEqual(str(dd),
                         '+g_only: 5\n-f_only: 5\n-name: mine\n+name: me')

        dd = Diff(f, g, mode='add')
        dd.findDiff()
        self.assertEqual(len(dd.diffs), 1)

        self.assertEqual(dd.diffs[0].path, '')
        self.assertEqual(dd.diffs[0].item, 'g_only')
        self.assertEqual(dd.diffs[0].value, 5)
        self.assertEqual(str(dd), '+g_only: 5')

        dd = Diff(f, g, mode='remove')
        dd.findDiff()
        self.assertEqual(len(dd.diffs), 1)

        self.assertEqual(dd.diffs[0].path, '')
        self.assertEqual(dd.diffs[0].item, 'f_only')
        self.assertEqual(dd.diffs[0].value, 5)
        self.assertEqual(str(dd), '-f_only: 5')

        dd = Diff(f, g, mode='modified')
        dd.findDiff()
        self.assertEqual(len(dd.diffs), 1)
        self.assertEqual(dd.diffs[0].items[0].path, '')
        self.assertEqual(dd.diffs[0].items[0].item, 'name')
        self.assertEqual(dd.diffs[0].items[0].value, 'mine')
        self.assertEqual(dd.diffs[0].items[1].path, '')
        self.assertEqual(dd.diffs[0].items[1].item, 'name')
        self.assertEqual(dd.diffs[0].items[1].value, 'me')
        self.assertEqual(str(dd), '-name: mine\n+name: me')

    def test_second_level(self):
        f = Feature(testbed=self.tb)
        g = Feature(testbed=self.tb)


        f.device_attr['adevice'].name = 'mine'
        g.device_attr['adevice'].name = 'me'
        f.device_attr['adevice'].old = 'old_value'
        g.device_attr['adevice'].new = 'new_value'
        f.test = 3
        g.test = 2
        f.same = 2
        g.same = 2

        dd = Diff(f, g, mode='add')
        dd.findDiff()

        self.assertEqual(len(dd.diffs), 1)
        self.assertEqual(dd.diffs[0].items[0].items[0].path,
                         'device_attr\nadevice')
        self.assertEqual(dd.diffs[0].items[0].items[0].item,'new')
        self.assertEqual(dd.diffs[0].items[0].items[0].value, 'new_value')
        self.assertEqual(str(dd), ' device_attr:\n  adevice:\n+  new: new_value')

        dd = Diff(f, g, mode='remove')
        dd.findDiff()

        self.assertEqual(len(dd.diffs), 1)
        self.assertEqual(dd.diffs[0].items[0].items[0].path,
                         'device_attr\nadevice')
        self.assertEqual(dd.diffs[0].items[0].items[0].item,'old')
        self.assertEqual(dd.diffs[0].items[0].items[0].value, 'old_value')
        self.assertEqual(str(dd), ' device_attr:\n  adevice:\n-  old: old_value')

        dd = Diff(f, g, mode='modified')
        dd.findDiff()

        self.assertEqual(len(dd.diffs), 2)
        self.assertEqual(dd.diffs[1].items[0].path, '')
        self.assertEqual(dd.diffs[1].items[0].item, 'test')
        self.assertEqual(dd.diffs[1].items[0].value, 3)
        self.assertEqual(dd.diffs[1].items[1].path, '')
        self.assertEqual(dd.diffs[1].items[1].item, 'test')
        self.assertEqual(dd.diffs[1].items[1].value, 2)

        self.assertEqual(dd.diffs[0].items[0].items[0].path,
                         'device_attr\nadevice')
        self.assertEqual(dd.diffs[0].items[0].items[0].items[0].path,
                        'device_attr\nadevice')
        self.assertEqual(dd.diffs[0].items[0].items[0].items[0].item, 'name')
        self.assertEqual(dd.diffs[0].items[0].items[0].items[0].value, 'mine')

        self.assertEqual(dd.diffs[0].items[0].items[0].items[1].path,
                         'device_attr\nadevice')
        self.assertEqual(dd.diffs[0].items[0].items[0].items[1].item, 'name')
        self.assertEqual(dd.diffs[0].items[0].items[0].items[1].value, 'me')


        self.assertEqual(str(dd), ' device_attr:\n  adevice:\n-  name: mine\n+  name: me\n-test: 3\n+test: 2')




class test_DiffConfig(unittest.TestCase):
    cli = '''
telnet vrf default ipv4 server max-servers 90
line console
 exec-timeout 0 0
!
vty-pool default 0 99 line-template default
interface MgmtEth0/RSP0/CPU0/0
 ipv4 address 10.1.1.183 255.255.255.0
!
interface MgmtEth0/RSP0/CPU0/1
 shutdown
!
interface MgmtEth0/RSP1/CPU0/0
 ipv4 address 10.1.1.184 255.255.255.0
  dd
    '''

    config = '''
vty-pool default 0 99 line-template default
interface MgmtEth0/RSP0/CPU0/0
 ipv6 address 10.1.1.183 255.255.255.0
 ipv6 address 13.1.1.183 255.255.255.0
  xda
   level
 we
interface GigabitEthernet0/0/0/5
 no shutdown
interface GigabitEthernet0/0/0/6
 shutdown
router ospf 100
 description 5
    '''

    def test_config_add(self):

        x = Config(output=self.cli)
        j = Config(output=self.config)
        x.tree()
        j.tree()

        g = Diff(x, j, mode='add')
        g.findDiff()
        self.assertEqual(len(g.diffs), 4)
        self.assertEqual(str(g),'+interface GigabitEthernet0/0/0/5\n+ no shutdown\n+interface GigabitEthernet0/0/0/6\n+ shutdown\n+router ospf 100\n+ description 5\n interface MgmtEth0/RSP0/CPU0/0\n+ ipv6 address 10.1.1.183 255.255.255.0\n+ ipv6 address 13.1.1.183 255.255.255.0\n+  xda\n+   level\n+ we')

    def test_config_remove(self):

        x = Config(output=self.cli)
        j = Config(output=self.config)
        x.tree()
        j.tree()

        g = Diff(x, j, mode='remove')
        g.findDiff()
        self.assertEqual(len(g.diffs), 5)
        self.assertEqual(str(g),'-interface MgmtEth0/RSP0/CPU0/1\n- shutdown\n-interface MgmtEth0/RSP1/CPU0/0\n- ipv4 address 10.1.1.184 255.255.255.0\n-  dd\n-line console\n- exec-timeout 0 0\n-telnet vrf default ipv4 server max-servers 90\ninterface MgmtEth0/RSP0/CPU0/0\n- ipv4 address 10.1.1.183 255.255.255.0')

    def test_config_remove(self):

        x = Config(output=self.cli)
        j = Config(output=self.config)
        x.tree()
        j.tree()

        g = Diff(x, j, mode='modified')
        g.findDiff()
        self.assertEqual(len(g.diffs), 0)
        self.assertEqual(str(g),'')

    def test_config_all(self):

        x = Config(output=self.cli)
        j = Config(output=self.config)
        x.tree()
        j.tree()

        g = Diff(x, j)
        g.findDiff()
        self.assertEqual(len(g.diffs), 8)
        self.assertEqual(str(g), '+interface GigabitEthernet0/0/0/5\n+ no shutdown\n+interface GigabitEthernet0/0/0/6\n+ shutdown\n+router ospf 100\n+ description 5\n-interface MgmtEth0/RSP0/CPU0/1\n- shutdown\n-interface MgmtEth0/RSP1/CPU0/0\n- ipv4 address 10.1.1.184 255.255.255.0\n-  dd\n-line console\n- exec-timeout 0 0\n-telnet vrf default ipv4 server max-servers 90\n interface MgmtEth0/RSP0/CPU0/0\n- ipv4 address 10.1.1.183 255.255.255.0\n+ ipv6 address 10.1.1.183 255.255.255.0\n+ ipv6 address 13.1.1.183 255.255.255.0\n+  xda\n+   level\n+ we')

    def test_config_all_exclude(self):

        x = Config(output=self.cli)
        j = Config(output=self.config)
        x.tree()
        j.tree()


        g = Diff(x, j, exclude=['(interface.*)'])
        g.findDiff()
        self.assertEqual(len(g.diffs), 3)
        self.assertEqual(str(g), '+router ospf 100\n+ description 5\n-line console\n- exec-timeout 0 0\n-telnet vrf default ipv4 server max-servers 90')

class test_DiffMixed(unittest.TestCase):
    new = {'instance':
            {'default': {'bgp_id': '100',
                'vrf': {'default':
                        {'address_family':
                            {'ipv6 unicast':
                               {'nexthop_trigger_delay_non_critical': 10000,
                                'nexthop_trigger_enable': True,
                                'nexthop_trigger_delay_critical': 3000},
                             'ipv4 unicast': {
                                'nexthop_trigger_delay_non_critical': 10000,
                                'nexthop_trigger_enable': True,
                                'nexthop_trigger_delay_critical': 3000}},
                         'confederation_identifier': 0,
                         'router_id': '100.1.1.1',
                         'neighbor': {
                            '200.1.1.1': {
                                'address_family': {'ipv4 unicast':
                                    {'route_map_name_out': 'zhi-test',
                                    'route_map_name_in': 'zhi-test',
                                    'bgp_table_version': 5}},
                                'bgp_neighbor_counters': {'messages':
                                    {'received': {'notifications': 0,
                                                  'keepalives': 1258,
                                                  'total': 1265,
                                                  'bytes_in_queue': 0,
                                                  'updates': 3,
                                                  'total_bytes': 23959,
                                                  'capability': 1,
                                                  'opens': 3,
                                                  'route_refresh': 0},
                                     'sent': {'notifications': 3,
                                              'keepalives': 1258,
                                              'total': 1268,
                                              'bytes_in_queue': 0,
                                              'updates': 3,
                                              'total_bytes': 24026,
                                              'capability': 1,
                                              'opens': 3,
                                              'route_refresh': 0}}},
                                'update_source': 'loopback0',
                                'remote_as': '88', 'shutdown': False,
                                'holdtime': '180', 'up_time': '00:01:52',
                                'bgp_negotiated_keepalive_timers': {
                                    'hold_time': '180',
                                    'keepalive_interval': '60'},
                                'local_as_as_no': 'None',
                                'keepalive_interval': '60',
                                'session_state': 'Idle',
                                'bgp_session_transport': {'connection':
                                    {'last_reset': 'never',
                                     'reset_reason': 'no error',
                                     'state': 'Idle'}}, 'bgp_version': 4},
                            '200:1::1:1': {
                                'address_family': {'ipv6 unicast':
                                                    {'bgp_table_version': 3}},
                                'bgp_neighbor_counters': {'messages':
                                    {'received': {'notifications': 0,
                                                  'keepalives': 20,
                                                  'total': 23,
                                                  'bytes_in_queue': 0,
                                                  'updates': 1,
                                                  'total_bytes': 417,
                                                  'capability': 1,
                                                  'opens': 1,
                                                  'route_refresh': 0},
                                     'sent': {'notifications': 1,
                                              'keepalives': 20, 'total': 24,
                                              'bytes_in_queue': 0, 'updates': 1,
                                              'total_bytes': 442,
                                              'capability': 1, 'opens': 1,
                                              'route_refresh': 0}}},
                                'update_source': 'loopback0',
                                'remote_as': '88', 'shutdown': False,
                                'holdtime': '180', 'up_time': '20:38:28',
                                'bgp_negotiated_keepalive_timers':
                                    {'hold_time': '180',
                                    'keepalive_interval': '60'},
                                'local_as_as_no': 'None',
                                'keepalive_interval': '60',
                                'session_state': 'Idle',
                                'bgp_session_transport':
                                    {'connection': {'last_reset': 'never',
                                        'reset_reason': 'no error',
                                        'state': 'Idle'}}, 'bgp_version': 4},
                            '50.1.1.101': {
                                'bgp_neighbor_counters':
                                    {'messages': {
                                        'received': {'notifications': 0,
                                                     'keepalives': 0,
                                                     'total': 0,
                                                     'bytes_in_queue': 0,
                                                     'updates': 0,
                                                     'total_bytes': 0,
                                                     'capability': 0,
                                                     'opens': 0,
                                                     'route_refresh': 0},
                                        'sent': {'notifications': 0,
                                                 'keepalives': 0, 'total': 0,
                                                 'bytes_in_queue': 0,
                                                 'updates': 0,
                                                 'total_bytes': 0,
                                                 'capability': 0,
                                                 'opens': 0,
                                                 'route_refresh': 0}}},
                                'up_time': '20:56:50',
                                'update_source': 'loopback0',
                                'ebgp_multihop': True,
                                'shutdown': False, 'holdtime': '180',
                                'ebgp_multihop_max_hop': 5,
                                'bgp_negotiated_keepalive_timers':
                                    {'hold_time': '180',
                                    'keepalive_interval': '60'},
                                'local_as_as_no': 'None',
                                'remote_as': '300',
                                'keepalive_interval': '60',
                                'address_family':
                                    {'ipv4 unicast': {'bgp_table_version': 5}},
                                'bgp_session_transport':
                                    {'connection': {'last_reset': 'never',
                                                    'reset_reason': 'no error',
                                                    'state': 'Idle'}},
                                'bgp_version': 4, 'session_state': 'Idle'},
                            '50:1::1:101': {
                                'bgp_neighbor_counters': {'messages': {
                                    'received': {'notifications': 0,
                                                 'keepalives': 0,
                                                 'total': 0,
                                                 'bytes_in_queue': 0,
                                                 'updates': 0,
                                                 'total_bytes': 0,
                                                 'capability': 0,
                                                 'opens': 0,
                                                 'route_refresh': 0},
                                    'sent': {'notifications': 0,
                                             'keepalives': 0,
                                             'total': 0,
                                             'bytes_in_queue': 0,
                                             'updates': 0, 'total_bytes': 0,
                                             'capability': 0, 'opens': 0,
                                             'route_refresh': 0}}},
                                'up_time': '20:34:34',
                                'update_source': 'loopback0',
                                'ebgp_multihop': True, 'shutdown': False,
                                'holdtime': '180', 'ebgp_multihop_max_hop': 5,
                                'bgp_negotiated_keepalive_timers':
                                    {'hold_time': '180',
                                    'keepalive_interval': '60'},
                                'local_as_as_no': 'None',
                                'remote_as': '300', 'keepalive_interval': '60',
                                'address_family': {'ipv6 unicast':
                                    {'bgp_table_version': 3}},
                                'bgp_session_transport': {'connection':
                                    {'last_reset': 'never',
                                     'reset_reason': 'no error',
                                     'state': 'Idle'}},
                                'bgp_version': 4, 'session_state': 'Idle'}},
                            'cluster_id': '0.0.0.0'}},
                        'protocol_state': 'running'}}}
    old = {'instance':
            {'default': {'bgp_id': '100',
                'vrf': {'default': {
                    'address_family': {
                        'ipv6 unicast':
                            {'nexthop_trigger_delay_non_critical': 10000,
                            'nexthop_trigger_enable': True,
                            'nexthop_trigger_delay_critical': 3000},
                        'ipv4 unicast':
                            {'nexthop_trigger_delay_non_critical': 10000,
                            'nexthop_trigger_enable': True,
                            'nexthop_trigger_delay_critical': 3000}},
                    'confederation_identifier': 0,
                    'router_id': '100.1.1.1',
                    'neighbor': {
                        '200.1.1.1': {
                            'address_family': {
                                'ipv4 unicast': {
                                    'route_map_name_out': 'zhi-test',
                                    'route_map_name_in': 'zhi-test',
                                    'bgp_table_version': 5}},
                            'bgp_neighbor_counters': {'messages': {
                                'received': {'notifications': 0,
                                             'keepalives': 1258,
                                             'total': 1265,
                                             'bytes_in_queue': 0,
                                             'updates': 3, 'total_bytes': 23959,
                                             'capability': 1, 'opens': 3,
                                             'route_refresh': 0},
                                'sent': {'notifications': 2,
                                         'keepalives': 1258,
                                         'total': 1267, 'bytes_in_queue': 0,
                                         'updates': 3, 'total_bytes': 24005,
                                         'capability': 1, 'opens': 3,
                                         'route_refresh': 0}}},
                            'update_source': 'loopback0', 'remote_as': '100',
                            'shutdown': False, 'holdtime': '180',
                            'up_time': '20:33:24',
                            'bgp_negotiated_keepalive_timers':
                                {'hold_time': '180',
                                'keepalive_interval': '60'},
                            'local_as_as_no': 'None',
                            'keepalive_interval': '60',
                            'session_state': 'Established',
                            'bgp_session_transport': {
                                'connection':
                                    {'last_reset': 'never',
                                     'reset_reason': 'no error',
                                     'state': 'Established'},
                                'transport':
                                    {'local_port': '31342',
                                    'foreign_host': '200.1.1.1',
                                    'foreign_port': '179',
                                    'local_host': '100.1.1.1'}},
                            'bgp_version': 4,
                            'bgp_negotiated_capabilities':
                                {'graceful_restart': 'advertised received',
                                'route_refresh_old': 'advertised received',
                                'dynamic_capability': 'advertised (mp, refresh, gr) received (mp, refresh, gr)',
                                'dynamic_capability_old': 'advertised received',
                                'route_refresh': 'advertised received'}},
                        '200:1::1:1': {
                            'address_family':
                                {'ipv6 unicast': {'bgp_table_version': 3}},
                            'bgp_neighbor_counters': {'messages': {
                                'received': {'notifications': 0,
                                             'keepalives': 20, 'total': 23,
                                             'bytes_in_queue': 0, 'updates': 1,
                                             'total_bytes': 417,
                                             'capability': 1, 'opens': 1,
                                             'route_refresh': 0},
                                'sent': {'notifications': 1, 'keepalives': 20,
                                         'total': 24, 'bytes_in_queue': 0,
                                         'updates': 1, 'total_bytes': 442,
                                         'capability': 1, 'opens': 1,
                                         'route_refresh': 0}}},
                            'update_source': 'loopback0', 'remote_as': '88',
                            'shutdown': False, 'holdtime': '180',
                            'up_time': '20:36:29',
                            'bgp_negotiated_keepalive_timers':
                                {'hold_time': '180',
                                'keepalive_interval': '60'},
                            'bgp_session_transport': {'connection':
                                {'last_reset': 'never',
                                'reset_reason': 'no error',
                                'state': 'Idle'}},
                            'keepalive_interval': '60',
                            'session_state': 'Idle',
                            'local_as_as_no': 'None', 'bgp_version': 4},
                        '50.1.1.101': {'bgp_neighbor_counters': {'messages': {
                            'received': {'notifications': 0,
                                         'keepalives': 0, 'total': 0,
                                         'bytes_in_queue': 0, 'updates': 0,
                                         'total_bytes': 0, 'capability': 0,
                                         'opens': 0, 'route_refresh': 0},
                            'sent': {'notifications': 0, 'keepalives': 0,
                                     'total': 0, 'bytes_in_queue': 0,
                                     'updates': 0, 'total_bytes': 0,
                                     'capability': 0, 'opens': 0,
                                     'route_refresh': 0}}},
                            'up_time': '20:54:50', 'update_source': 'loopback0',
                            'remote_as': '300', 'shutdown': False,
                            'holdtime': '180', 'ebgp_multihop_max_hop': 5,
                            'bgp_negotiated_keepalive_timers':
                                {'hold_time': '180',
                                'keepalive_interval': '60'},
                                'local_as_as_no': 'None', 'ebgp_multihop': True,
                                'keepalive_interval': '60',
                                'address_family': {'ipv4 unicast':
                                    {'bgp_table_version': 5}},
                                'bgp_session_transport':
                                    {'connection': {'last_reset': 'never',
                                                    'reset_reason': 'no error',
                                                    'state': 'Idle'}},
                                'bgp_version': 4, 'session_state': 'Idle'},
                        '50:1::1:101': {
                            'bgp_neighbor_counters': {'messages': {
                                'received': {'notifications': 0,
                                            'keepalives': 0, 'total': 0,
                                            'bytes_in_queue': 0, 'updates': 0,
                                            'total_bytes': 0, 'capability': 0,
                                            'opens': 0, 'route_refresh': 0},
                                'sent': {'notifications': 0, 'keepalives': 0,
                                         'total': 0, 'bytes_in_queue': 0,
                                         'updates': 0, 'total_bytes': 0,
                                         'capability': 0, 'opens': 0,
                                         'route_refresh': 0}}},
                            'up_time': '20:32:34', 'update_source': 'loopback0',
                            'remote_as': '300', 'shutdown': False,
                            'holdtime': '180', 'ebgp_multihop_max_hop': 5,
                            'bgp_negotiated_keepalive_timers':
                                {'hold_time': '180',
                                'keepalive_interval': '60'},
                            'local_as_as_no': 'None', 'ebgp_multihop': True,
                            'keepalive_interval': '60', 'address_family': {
                                'ipv6 unicast': {'bgp_table_version': 3}},
                            'bgp_session_transport': {'connection': {
                                'last_reset': 'never',
                                'reset_reason': 'no error',
                                'state': 'Idle'}},
                            'bgp_version': 4, 'session_state': 'Idle'}
                            }, 'cluster_id': '0.0.0.0'}},
                        'protocol_state': 'running'}}}

    bgp_exclude = ['maker', 'bgp_session_transport',
                   'bgp_negotiated_capabilities', 'notifications',
                   'keepalives', 'total', 'total_bytes',
                   'bgp_negotiated_keepalive_timers', 'updates', 'opens',
                   'bgp_table_version', 'holdtime', 'keepalive_interval',
                   'remote_as']

    def test_dict_vs_object(self):
        obj1 = { 'info' : self.new }
        obj2 = { 'info' : self.old }

        diff = Diff(obj1, obj2, exclude=self.bgp_exclude)
        diff1 = diff.findDiff()

        obj1 = Bgp(device='fake')
        obj2 = Bgp(device='fake')
        obj1.info = self.new
        obj2.info = self.old

        diff = Diff(obj1, obj2, exclude=self.bgp_exclude)
        diff2 = diff.findDiff()
        self.assertEqual(diff1, diff2)

    def test_dict_vs_config(self):

        output1 = '''\
a
 aa
   aaa
 ab
b
 bb
c
d'''
        output2 = '''\
a
 aa
   aa
 ab
   aaa
b
 bb
c
d'''
        config1 = Config(output1)
        config1.tree()
        config2 = Config(output2)
        config2.tree()

        diff = Diff(config1, config2)
        diff1 = diff.findDiff()
        diff = Diff(config1.config, config2.config)
        diff2 = diff.findDiff()
        self.assertEqual(diff1, diff2)

    def test_list_in_dict_with_index_move(self):

        self.maxDiff = None
        output1 = '''\
-changed: true
+changed: false
 imdata:
+ index[0]:
+  infraAccPortP:
+   attributes:
+    annotation:
+    childAction:
+    descr:
+    dn: uni/infra/accportprof-LEAF101_INT1_21
+    extMngdBy:
+    lcOwn: local
+    modTs: 2020-07-16T10:04:08.053+00:00
+    monPolDn: uni/fabric/monfab-default
+    name: LEAF101_INT1_21
+    nameAlias:
+    ownerKey:
+    ownerTag:
+    status:
+    uid: 13550
- index[3]:
-  infraAccPortP:
-   attributes:
-    annotation:
-    childAction:
-    descr: BTF2-LF04
-    dn: uni/infra/accportprof-SW_1204_IPr
-    extMngdBy:
-    lcOwn: local
-    modTs: 2020-06-26T16:50:55.113+00:00
-    monPolDn: uni/fabric/monfab-default
-    name: SW_1204_IPr
-    nameAlias:
-    ownerKey:
-    ownerTag:
-    status:
-    uid: 13569
- index[4]:
-  infraAccPortP:
-   attributes:
-    annotation:
-    childAction:
-    descr:
-    dn: uni/infra/accportprof-POD2_milnicki_int_1_22
-    extMngdBy:
-    lcOwn: local
-    modTs: 2020-04-15T13:01:45.826+00:00
-    monPolDn: uni/fabric/monfab-default
-    name: POD2_milnicki_int_1_22
-    nameAlias:
-    ownerKey:
-    ownerTag:
-    status:
-    uid: 13551
+ index[4]:
+  infraAccPortP:
+   attributes:
+    annotation:
+    childAction:
+    descr:
+    dn: uni/infra/accportprof-Leaf_101
+    extMngdBy:
+    lcOwn: local
+    modTs: 2020-08-10T10:37:21.485+00:00
+    monPolDn: uni/fabric/monfab-default
+    name: Leaf_101
+    nameAlias:
+    ownerKey:
+    ownerTag:
+    status:
+    uid: 13569
-status: 0
+status: -1'''

        golden = {
    "changed": "true",
    "failed": "false",
    "imdata": [
        {
            "infraAccPortP": {
                "attributes": {
                    "annotation": "",
                    "childAction": "",
                    "descr": "",
                    "dn": "uni/infra/accportprof-ab_leaf_Profile",
                    "extMngdBy": "",
                    "lcOwn": "local",
                    "modTs": "2020-07-19T11:53:45.823+00:00",
                    "monPolDn": "uni/fabric/monfab-default",
                    "name": "ab_leaf_Profile",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": "",
                    "status": "",
                    "uid": "13552"
                }
            }
        },
        {
            "infraAccPortP": {
                "attributes": {
                    "annotation": "",
                    "childAction": "",
                    "descr": "",
                    "dn": "uni/infra/accportprof-asaud_IP",
                    "extMngdBy": "",
                    "lcOwn": "local",
                    "modTs": "2020-07-28T02:11:34.583+00:00",
                    "monPolDn": "uni/fabric/monfab-default",
                    "name": "asaud_IP",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": "",
                    "status": "",
                    "uid": "13550"
                }
            }
        },
        {
            "infraAccPortP": {
                "attributes": {
                    "annotation": "",
                    "childAction": "",
                    "descr": "",
                    "dn": "uni/infra/accportprof-Leaf101",
                    "extMngdBy": "",
                    "lcOwn": "local",
                    "modTs": "2020-08-06T11:06:53.290+00:00",
                    "monPolDn": "uni/fabric/monfab-default",
                    "name": "Leaf101",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": "",
                    "status": "",
                    "uid": "13569"
                }
            }
        },
        {
            "infraAccPortP": {
                "attributes": {
                    "annotation": "",
                    "childAction": "",
                    "descr": "BTF2-LF04",
                    "dn": "uni/infra/accportprof-SW_1204_IPr",
                    "extMngdBy": "",
                    "lcOwn": "local",
                    "modTs": "2020-06-26T16:50:55.113+00:00",
                    "monPolDn": "uni/fabric/monfab-default",
                    "name": "SW_1204_IPr",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": "",
                    "status": "",
                    "uid": "13569"
                }
            }
        },
        {
            "infraAccPortP": {
                "attributes": {
                    "annotation": "",
                    "childAction": "",
                    "descr": "",
                    "dn": "uni/infra/accportprof-POD2_milnicki_int_1_22",
                    "extMngdBy": "",
                    "lcOwn": "local",
                    "modTs": "2020-04-15T13:01:45.826+00:00",
                    "monPolDn": "uni/fabric/monfab-default",
                    "name": "POD2_milnicki_int_1_22",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": "",
                    "status": "",
                    "uid": "13551"
                }
            }
        }
    ],
    "status": "0",
    "totalCount": "5",
    "warnings": [
        "Platform linux on host localhost is using the discovered Python interpreter at /usr/bin/python, but future installation of another Python interpreter could change this. See https://docs.ansible.com/ansible/2.9/reference_appendices/interpreter_discovery.html for more information."
    ]
}

        running = {
    "changed": "false",
    "failed": "false",
    "imdata": [
        {
            "infraAccPortP": {
                "attributes": {
                    "annotation": "",
                    "childAction": "",
                    "descr": "",
                    "dn": "uni/infra/accportprof-LEAF101_INT1_21",
                    "extMngdBy": "",
                    "lcOwn": "local",
                    "modTs": "2020-07-16T10:04:08.053+00:00",
                    "monPolDn": "uni/fabric/monfab-default",
                    "name": "LEAF101_INT1_21",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": "",
                    "status": "",
                    "uid": "13550"
                }
            }
        },
        {
            "infraAccPortP": {
                "attributes": {
                    "annotation": "",
                    "childAction": "",
                    "descr": "",
                    "dn": "uni/infra/accportprof-ab_leaf_Profile",
                    "extMngdBy": "",
                    "lcOwn": "local",
                    "modTs": "2020-07-19T11:53:45.823+00:00",
                    "monPolDn": "uni/fabric/monfab-default",
                    "name": "ab_leaf_Profile",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": "",
                    "status": "",
                    "uid": "13552"
                }
            }
        },
        {
            "infraAccPortP": {
                "attributes": {
                    "annotation": "",
                    "childAction": "",
                    "descr": "",
                    "dn": "uni/infra/accportprof-asaud_IP",
                    "extMngdBy": "",
                    "lcOwn": "local",
                    "modTs": "2020-07-28T02:11:34.583+00:00",
                    "monPolDn": "uni/fabric/monfab-default",
                    "name": "asaud_IP",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": "",
                    "status": "",
                    "uid": "13550"
                }
            }
        },
        {
            "infraAccPortP": {
                "attributes": {
                    "annotation": "",
                    "childAction": "",
                    "descr": "",
                    "dn": "uni/infra/accportprof-Leaf101",
                    "extMngdBy": "",
                    "lcOwn": "local",
                    "modTs": "2020-08-06T11:06:53.290+00:00",
                    "monPolDn": "uni/fabric/monfab-default",
                    "name": "Leaf101",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": "",
                    "status": "",
                    "uid": "13569"
                }
            }
        },
        {
            "infraAccPortP": {
                "attributes": {
                    "annotation": "",
                    "childAction": "",
                    "descr": "",
                    "dn": "uni/infra/accportprof-Leaf_101",
                    "extMngdBy": "",
                    "lcOwn": "local",
                    "modTs": "2020-08-10T10:37:21.485+00:00",
                    "monPolDn": "uni/fabric/monfab-default",
                    "name": "Leaf_101",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": "",
                    "status": "",
                    "uid": "13569"
                }
            }
        }
    ],
    "status": "-1",
    "totalCount": "5",
    "warnings": [
        "Platform linux on host localhost is using the discovered Python interpreter at /usr/bin/python, but future installation of another Python interpreter could change this. See https://docs.ansible.com/ansible/2.9/reference_appendices/interpreter_discovery.html for more information."
    ]
}

        dd = Diff(golden, running, list_order=True)
        dd.findDiff()
        self.assertEqual(str(dd), output1)

    def test_nested_list_in_dict_with_index_move(self):

        D1 = {
            'a': 1,
            'b': 2,
            'c': [{
                    'd': 3,
                    'e': 4,
                    'f': [{
                            'x': 5
                        }
                    ]
                }, {
                    'd': 6,
                    'e': 7,
                    'f': [{
                            'x': 8
                        }, {
                            'y': 9
                        }
                    ]
                }
            ]
        }

        D2 = {
            'a': 1,
            'c': [{
                    'e': 7,
                    'd': 6,
                    'f': [{
                            'y': 9
                        }, {
                            'x': 8
                        }
                    ]
                }, {
                    'f': [{
                            'x': 5
                        }
                    ],
                    'd': 3,
                    'e': 4
                }
            ],
            'b': 2
        }


        dd = Diff(D1, D2, list_order=True)
        dd.findDiff()
        self.assertEqual(str(dd), '')

        output = \
""" c:
+ index[0]:
+  d: 6
+  e: 7
+  f:
+   index[0]:
+    x: 8
+   index[1]:
+    y: 19
- index[1]:
-  d: 6
-  e: 7
-  f:
-   index[0]:
-    x: 8
-   index[1]:
-    y: 9"""

        D1 = {'a': 1,
                'b': 2,
                'c': [{'d': 3, 'e': 4, 'f': [{'x': 5}]},
                 {'d': 6, 'e': 7, 'f': [{'x': 8}, {'y': 9}]}]}

        D2 = {'a': 1,
             'c': [{'e': 7, 'd': 6, 'f': [{'y': 19}, {'x': 8}]},
              {'f': [{'x': 5}], 'd': 3, 'e': 4}],
             'b': 2}

        dd = Diff(D1, D2, list_order=True)
        dd.findDiff()
        self.assertEqual(str(dd), output)

    def test_iterable(self):


        output1 = '''\
 c:
  cb:
-  index[5]: 6
+  index[5]: 7
-  index[6]: 7'''
        output2 = '''\
 c:
- cb: {1, 2, 3, 4, 5, 6, 7}
+ cb: {1, 2, 3, 4, 5, 7}'''
        output3 = '''\
 c:
  cb:
-  index[5]: 6
+  index[5]: 7
-  index[6]: 7'''
        output4 = '''\
 c:
- cb:
-  index[0]: 1
-  index[1]: 7
+ cb:
+  1: 7'''
        output5 = '''\
 c:
  cb:
-  index[5]: 6
+  index[5]:
+   index[0]: 6'''
        output6 = '''\
 c:
  cb:
-  index[5]: 6
+  index[5]:
+   index[0]: 6
+   index[1]: 7
-  index[6]: 7'''

        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':[1,2,3,4,5,6,7]}}
        A = {'a':5, 'b':7, 'c':{'ca':8, 'cb':[1,2,3,4,5,7]}}
        dd = Diff(a,A)
        dd.findDiff()
        self.assertEqual(str(dd), output1)

        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':{1,2,3,4,5,6,7}}}
        A = {'a':5, 'b':7, 'c':{'ca':8, 'cb':{1,2,3,4,5,7}}}
        dd = Diff(a,A)
        dd.findDiff()
        self.assertEqual(str(dd), output2)

        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':(1,2,3,4,5,6,7)}}
        A = {'a':5, 'b':7, 'c':{'ca':8, 'cb':(1,2,3,4,5,7)}}
        dd = Diff(a,A)
        dd.findDiff()
        self.assertEqual(str(dd), output3)

        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':[1,7]}}
        A = {'a':5, 'b':7, 'c':{'ca':8, 'cb':{1:7}}}
        dd = Diff(a,A)
        dd.findDiff()
        self.assertEqual(str(dd), output4)

        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':[1,2,3,4,5,6,7]}}
        A = {'a':5, 'b':7, 'c':{'ca':8, 'cb':[1,2,3,4,5,[6],7]}}
        dd = Diff(a,A)
        dd.findDiff()
        self.assertEqual(str(dd), output5)

        a = {'a':5, 'b':7, 'c':{'ca':8, 'cb':[1,2,3,4,5,6,7]}}
        A = {'a':5, 'b':7, 'c':{'ca':8, 'cb':[1,2,3,4,5,(6,7)]}}
        dd = Diff(a,A)
        dd.findDiff()
        self.assertEqual(str(dd), output6)

class test_DiffKeyIsInt(unittest.TestCase):
    def test_first_key_is_int(self):
        output1 = ' 1:\n- a: 1\n+ a: 2'
        a = {1: {'a': 1}}
        A = {1: {'a': 2}}
        dd = Diff(a, A)
        dd.findDiff()
        self.assertEqual(str(dd), output1)

    def test_sort_str_and_int(self):
        output1 = '''\
 info:
  1:
-  next_hop: 10.0.2.1
+  next_hop: 10.0.1.1
+ 2:
+  next_hop: 10.0.2.1'''
        a = {
            'info': {
                1: {'next_hop': '10.0.2.1'}
            }
        }

        A = {
            'info': {
                1: {'next_hop': '10.0.1.1'},
                2: {'next_hop': '10.0.2.1'}
            }
        }

        dd = Diff(a, A)
        dd.findDiff()
        self.assertEqual(str(dd), output1)


if __name__ == '__main__':
    unittest.main()
