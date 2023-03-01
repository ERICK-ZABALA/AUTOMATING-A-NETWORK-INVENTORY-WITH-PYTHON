#!/usr/bin/env python

# Import unittest module
import unittest
from unittest.mock import Mock
import types

from genie.decorator import managedattribute
from genie.conf.base import Base
from genie.conf.base.attributes import SubAttributes, SubAttributesDict,\
    AttributesHelper, AttributesInheriter

class Parent(Base):

    testbed = object()

    def aFunc(self):
        pass

class Child(SubAttributes):
    pass

class test_AttributesInheriter(unittest.TestCase):

    def test_getattr(self):
        p = Parent()
        p.a = 'Parent a'
        p.b = 'Parent b'

        sub = AttributesInheriter(parent=p)
        self.assertEqual(sub.a, p.a)
        self.assertEqual(sub.b, p.b)
        with self.assertRaisesRegex(AttributeError,
                                    r''''Parent' object has no attribute 'c'$'''):
            p.c
        with self.assertRaisesRegex(AttributeError,
                                    r''''AttributesInheriter' object has no attribute 'c'$'''):
            sub.c

        sub.b = 'Child b'
        sub.c = 'Child c'
        self.assertEqual(sub.a, p.a)
        self.assertEqual(p.b, 'Parent b')
        self.assertEqual(sub.b, 'Child b')
        with self.assertRaises(AttributeError):
            p.c
        self.assertEqual(sub.c, 'Child c')

        with self.assertRaises(AttributeError):
            sub.aFunc

    def test_isinherited(self):

        class Parent2(Parent):
            a = 1
            b = 2
            ma = managedattribute(name='ma', default=3, type=int)
            mb = managedattribute(name='mb', default=4, type=int)
            @property
            def p(self):
                return 5

        p = Parent2()
        sub = AttributesInheriter(parent=p)

        self.assertEqual(sub.a, 1)
        self.assertIs(sub.isinherited('a'), True)
        self.assertEqual(sub.b, 2)
        self.assertIs(sub.isinherited('b'), True)
        with self.assertRaises(AttributeError):
            sub.c
        self.assertIs(sub.isinherited('c'), False)
        with self.assertRaises(AttributeError):
            sub.d
        self.assertIs(sub.isinherited('d'), False)
        self.assertEqual(sub.ma, 3)
        self.assertIs(sub.isinherited('ma'), True)
        self.assertEqual(sub.mb, 4)
        self.assertIs(sub.isinherited('mb'), True)
        self.assertEqual(sub.p, 5)
        self.assertIs(sub.isinherited('p'), True)

        sub.a = 6
        sub.c = 7
        sub.ma = 8
        sub.p = 'blah'

        self.assertEqual(sub.a, 6)
        self.assertIs(sub.isinherited('a'), False)
        self.assertEqual(sub.b, 2)
        self.assertIs(sub.isinherited('b'), True)
        self.assertEqual(sub.c, 7)
        self.assertIs(sub.isinherited('c'), False)
        with self.assertRaises(AttributeError):
            sub.d
        self.assertIs(sub.isinherited('d'), False)
        self.assertEqual(sub.ma, 8)
        self.assertIs(sub.isinherited('ma'), False)
        self.assertEqual(sub.mb, 4)
        self.assertIs(sub.isinherited('mb'), True)
        self.assertEqual(sub.p, 'blah')
        self.assertIs(sub.isinherited('p'), False)

    def test_managedattribute(self):

        class Managed(object):
            int_only = managedattribute(
                name='int_only',
                default='1',
                type=int,
                gettype=str)
            int_only_no_def = managedattribute(
                name='int_only_no_def',
                type=int,
                gettype=str)

        with self.subTest('int_only'):

            p = Managed()
            self.assertEqual(p.int_only, '1')
            self.assertFalse('int_only' in p.__dict__)
            self.assertFalse('_int_only' in p.__dict__)
            p.int_only = 2
            self.assertEqual(p.int_only, '2')
            self.assertEqual(p._int_only, 2)
            self.assertFalse('int_only' in p.__dict__)
            self.assertTrue('_int_only' in p.__dict__)
            with self.assertRaises(ValueError):
                p.int_only = 'abc'
            self.assertEqual(p.int_only, '2')
            self.assertEqual(p._int_only, 2)
            self.assertFalse('int_only' in p.__dict__)
            self.assertTrue('_int_only' in p.__dict__)
            del p.int_only
            self.assertEqual(p.int_only, '1')
            self.assertFalse('int_only' in p.__dict__)
            self.assertFalse('_int_only' in p.__dict__)

            p = Managed()
            sub = AttributesInheriter(parent=p)
            self.assertEqual(sub.int_only, '1')
            self.assertFalse('int_only' in p.__dict__)
            self.assertFalse('_int_only' in p.__dict__)
            self.assertFalse('int_only' in sub.__dict__)
            self.assertFalse('_int_only' in sub.__dict__)
            sub.int_only = 2
            self.assertEqual(sub.int_only, '2')
            self.assertEqual(sub._int_only, 2)
            self.assertFalse('int_only' in p.__dict__)
            self.assertFalse('_int_only' in p.__dict__)
            self.assertFalse('int_only' in sub.__dict__)
            self.assertTrue('_int_only' in sub.__dict__)
            with self.assertRaises(ValueError):
                sub.int_only = 'abc'
            self.assertEqual(sub.int_only, '2')
            self.assertEqual(sub._int_only, 2)
            self.assertFalse('int_only' in p.__dict__)
            self.assertFalse('_int_only' in p.__dict__)
            self.assertFalse('int_only' in sub.__dict__)
            self.assertTrue('_int_only' in sub.__dict__)
            del sub.int_only
            self.assertEqual(sub.int_only, '1')
            self.assertFalse('int_only' in p.__dict__)
            self.assertFalse('_int_only' in p.__dict__)
            self.assertFalse('int_only' in sub.__dict__)
            self.assertFalse('_int_only' in sub.__dict__)
            with self.assertRaises(AttributeError):
                del sub.int_only
            self.assertFalse('int_only' in p.__dict__)
            self.assertFalse('_int_only' in p.__dict__)
            self.assertFalse('int_only' in sub.__dict__)
            self.assertFalse('_int_only' in sub.__dict__)

            sub2 = AttributesInheriter(parent=sub)
            self.assertEqual(sub2.int_only, '1')
            self.assertFalse('int_only' in p.__dict__)
            self.assertFalse('_int_only' in p.__dict__)
            self.assertFalse('int_only' in sub.__dict__)
            self.assertFalse('_int_only' in sub.__dict__)
            self.assertFalse('int_only' in sub2.__dict__)
            self.assertFalse('_int_only' in sub2.__dict__)
            sub2.int_only = 2
            self.assertEqual(sub2.int_only, '2')
            self.assertEqual(sub2._int_only, 2)
            self.assertFalse('int_only' in p.__dict__)
            self.assertFalse('_int_only' in p.__dict__)
            self.assertFalse('int_only' in sub.__dict__)
            self.assertFalse('_int_only' in sub.__dict__)
            self.assertFalse('int_only' in sub2.__dict__)
            self.assertTrue('_int_only' in sub2.__dict__)
            with self.assertRaises(ValueError):
                sub2.int_only = 'abc'
            self.assertEqual(sub2.int_only, '2')
            self.assertEqual(sub2._int_only, 2)
            self.assertFalse('int_only' in p.__dict__)
            self.assertFalse('_int_only' in p.__dict__)
            self.assertFalse('int_only' in sub.__dict__)
            self.assertFalse('_int_only' in sub.__dict__)
            self.assertFalse('int_only' in sub2.__dict__)
            self.assertTrue('_int_only' in sub2.__dict__)
            del sub2.int_only
            self.assertEqual(sub2.int_only, '1')
            self.assertFalse('int_only' in p.__dict__)
            self.assertFalse('_int_only' in p.__dict__)
            self.assertFalse('int_only' in sub.__dict__)
            self.assertFalse('_int_only' in sub.__dict__)
            self.assertFalse('int_only' in sub2.__dict__)
            self.assertFalse('_int_only' in sub2.__dict__)
            with self.assertRaises(AttributeError):
                del sub2.int_only
            self.assertFalse('int_only' in p.__dict__)
            self.assertFalse('_int_only' in p.__dict__)
            self.assertFalse('int_only' in sub.__dict__)
            self.assertFalse('_int_only' in sub.__dict__)
            self.assertFalse('int_only' in sub2.__dict__)
            self.assertFalse('_int_only' in sub2.__dict__)
            sub.int_only = 2
            self.assertEqual(sub.int_only, '2')
            self.assertEqual(sub2.int_only, '2')
            self.assertFalse('int_only' in p.__dict__)
            self.assertFalse('_int_only' in p.__dict__)
            self.assertFalse('int_only' in sub.__dict__)
            self.assertTrue('_int_only' in sub.__dict__)
            self.assertFalse('int_only' in sub2.__dict__)
            self.assertFalse('_int_only' in sub2.__dict__)
            with self.assertRaises(AttributeError):
                del sub2.int_only
            self.assertEqual(sub.int_only, '2')
            self.assertEqual(sub2.int_only, '2')
            self.assertFalse('int_only' in p.__dict__)
            self.assertFalse('_int_only' in p.__dict__)
            self.assertFalse('int_only' in sub.__dict__)
            self.assertTrue('_int_only' in sub.__dict__)
            self.assertFalse('int_only' in sub2.__dict__)
            self.assertFalse('_int_only' in sub2.__dict__)
            del sub.int_only
            self.assertEqual(sub2.int_only, '1')
            self.assertFalse('int_only' in p.__dict__)
            self.assertFalse('_int_only' in p.__dict__)
            self.assertFalse('int_only' in sub.__dict__)
            self.assertFalse('_int_only' in sub.__dict__)
            self.assertFalse('int_only' in sub2.__dict__)
            self.assertFalse('_int_only' in sub2.__dict__)
            with self.assertRaises(AttributeError):
                del sub.int_only
            self.assertFalse('int_only' in p.__dict__)
            self.assertFalse('_int_only' in p.__dict__)
            self.assertFalse('int_only' in sub.__dict__)
            self.assertFalse('_int_only' in sub.__dict__)
            self.assertFalse('int_only' in sub2.__dict__)
            self.assertFalse('_int_only' in sub2.__dict__)

        with self.subTest('int_only_no_def'):

            p = Managed()
            with self.assertRaises(AttributeError):
                p.int_only_no_def
            self.assertFalse('int_only_no_def' in p.__dict__)
            self.assertFalse('_int_only_no_def' in p.__dict__)
            p.int_only_no_def = 2
            self.assertEqual(p.int_only_no_def, '2')
            self.assertEqual(p._int_only_no_def, 2)
            self.assertFalse('int_only_no_def' in p.__dict__)
            self.assertTrue('_int_only_no_def' in p.__dict__)
            with self.assertRaises(ValueError):
                p.int_only_no_def = 'abc'
            self.assertEqual(p.int_only_no_def, '2')
            self.assertEqual(p._int_only_no_def, 2)
            self.assertFalse('int_only_no_def' in p.__dict__)
            self.assertTrue('_int_only_no_def' in p.__dict__)
            del p.int_only_no_def
            with self.assertRaises(AttributeError):
                p.int_only_no_def
            self.assertFalse('int_only_no_def' in p.__dict__)
            self.assertFalse('_int_only_no_def' in p.__dict__)

            p = Managed()
            sub = AttributesInheriter(parent=p)
            with self.assertRaises(AttributeError):
                sub.int_only_no_def
            self.assertFalse('int_only_no_def' in p.__dict__)
            self.assertFalse('_int_only_no_def' in p.__dict__)
            self.assertFalse('int_only_no_def' in sub.__dict__)
            self.assertFalse('_int_only_no_def' in sub.__dict__)
            sub.int_only_no_def = 2
            self.assertEqual(sub.int_only_no_def, '2')
            self.assertEqual(sub._int_only_no_def, 2)
            self.assertFalse('int_only_no_def' in p.__dict__)
            self.assertFalse('_int_only_no_def' in p.__dict__)
            self.assertFalse('int_only_no_def' in sub.__dict__)
            self.assertTrue('_int_only_no_def' in sub.__dict__)
            with self.assertRaises(ValueError):
                sub.int_only_no_def = 'abc'
            self.assertEqual(sub.int_only_no_def, '2')
            self.assertEqual(sub._int_only_no_def, 2)
            self.assertFalse('int_only_no_def' in p.__dict__)
            self.assertFalse('_int_only_no_def' in p.__dict__)
            self.assertFalse('int_only_no_def' in sub.__dict__)
            self.assertTrue('_int_only_no_def' in sub.__dict__)
            del sub.int_only_no_def
            with self.assertRaises(AttributeError):
                sub.int_only_no_def
            self.assertFalse('int_only_no_def' in p.__dict__)
            self.assertFalse('_int_only_no_def' in p.__dict__)
            self.assertFalse('int_only_no_def' in sub.__dict__)
            self.assertFalse('_int_only_no_def' in sub.__dict__)
            with self.assertRaises(AttributeError):
                del sub.int_only_no_def
            self.assertFalse('int_only_no_def' in p.__dict__)
            self.assertFalse('_int_only_no_def' in p.__dict__)
            self.assertFalse('int_only_no_def' in sub.__dict__)
            self.assertFalse('_int_only_no_def' in sub.__dict__)

            sub2 = AttributesInheriter(parent=sub)
            with self.assertRaises(AttributeError):
                sub2.int_only_no_def
            self.assertFalse('int_only_no_def' in p.__dict__)
            self.assertFalse('_int_only_no_def' in p.__dict__)
            self.assertFalse('int_only_no_def' in sub.__dict__)
            self.assertFalse('_int_only_no_def' in sub.__dict__)
            self.assertFalse('int_only_no_def' in sub2.__dict__)
            self.assertFalse('_int_only_no_def' in sub2.__dict__)
            sub2.int_only_no_def = 2
            self.assertEqual(sub2.int_only_no_def, '2')
            self.assertEqual(sub2._int_only_no_def, 2)
            self.assertFalse('int_only_no_def' in p.__dict__)
            self.assertFalse('_int_only_no_def' in p.__dict__)
            self.assertFalse('int_only_no_def' in sub.__dict__)
            self.assertFalse('_int_only_no_def' in sub.__dict__)
            self.assertFalse('int_only_no_def' in sub2.__dict__)
            self.assertTrue('_int_only_no_def' in sub2.__dict__)
            with self.assertRaises(ValueError):
                sub2.int_only_no_def = 'abc'
            self.assertEqual(sub2.int_only_no_def, '2')
            self.assertEqual(sub2._int_only_no_def, 2)
            self.assertFalse('int_only_no_def' in p.__dict__)
            self.assertFalse('_int_only_no_def' in p.__dict__)
            self.assertFalse('int_only_no_def' in sub.__dict__)
            self.assertFalse('_int_only_no_def' in sub.__dict__)
            self.assertFalse('int_only_no_def' in sub2.__dict__)
            self.assertTrue('_int_only_no_def' in sub2.__dict__)
            del sub2.int_only_no_def
            with self.assertRaises(AttributeError):
                sub2.int_only_no_def
            self.assertFalse('int_only_no_def' in p.__dict__)
            self.assertFalse('_int_only_no_def' in p.__dict__)
            self.assertFalse('int_only_no_def' in sub.__dict__)
            self.assertFalse('_int_only_no_def' in sub.__dict__)
            self.assertFalse('int_only_no_def' in sub2.__dict__)
            self.assertFalse('_int_only_no_def' in sub2.__dict__)
            with self.assertRaises(AttributeError):
                del sub2.int_only_no_def
            self.assertFalse('int_only_no_def' in p.__dict__)
            self.assertFalse('_int_only_no_def' in p.__dict__)
            self.assertFalse('int_only_no_def' in sub.__dict__)
            self.assertFalse('_int_only_no_def' in sub.__dict__)
            self.assertFalse('int_only_no_def' in sub2.__dict__)
            self.assertFalse('_int_only_no_def' in sub2.__dict__)
            sub.int_only_no_def = 2
            self.assertEqual(sub.int_only_no_def, '2')
            self.assertEqual(sub2.int_only_no_def, '2')
            self.assertFalse('int_only_no_def' in p.__dict__)
            self.assertFalse('_int_only_no_def' in p.__dict__)
            self.assertFalse('int_only_no_def' in sub.__dict__)
            self.assertTrue('_int_only_no_def' in sub.__dict__)
            self.assertFalse('int_only_no_def' in sub2.__dict__)
            self.assertFalse('_int_only_no_def' in sub2.__dict__)
            with self.assertRaises(AttributeError):
                del sub2.int_only_no_def
            self.assertEqual(sub.int_only_no_def, '2')
            self.assertEqual(sub2.int_only_no_def, '2')
            self.assertFalse('int_only_no_def' in p.__dict__)
            self.assertFalse('_int_only_no_def' in p.__dict__)
            self.assertFalse('int_only_no_def' in sub.__dict__)
            self.assertTrue('_int_only_no_def' in sub.__dict__)
            self.assertFalse('int_only_no_def' in sub2.__dict__)
            self.assertFalse('_int_only_no_def' in sub2.__dict__)
            del sub.int_only_no_def
            with self.assertRaises(AttributeError):
                sub.int_only_no_def
            with self.assertRaises(AttributeError):
                sub2.int_only_no_def
            self.assertFalse('int_only_no_def' in p.__dict__)
            self.assertFalse('_int_only_no_def' in p.__dict__)
            self.assertFalse('int_only_no_def' in sub.__dict__)
            self.assertFalse('_int_only_no_def' in sub.__dict__)
            self.assertFalse('int_only_no_def' in sub2.__dict__)
            self.assertFalse('_int_only_no_def' in sub2.__dict__)
            with self.assertRaises(AttributeError):
                del sub.int_only_no_def
            self.assertFalse('int_only_no_def' in p.__dict__)
            self.assertFalse('_int_only_no_def' in p.__dict__)
            self.assertFalse('int_only_no_def' in sub.__dict__)
            self.assertFalse('_int_only_no_def' in sub.__dict__)
            self.assertFalse('int_only_no_def' in sub2.__dict__)
            self.assertFalse('_int_only_no_def' in sub2.__dict__)


class test_SubAttributes(unittest.TestCase):

    def test_init(self):
        sub = SubAttributes(parent=Mock(testbed='fake'))

class test_SubAttributesDict(unittest.TestCase):

    def test_init(self):
        p = Parent()

        subdict = SubAttributesDict(Child, parent=p)

    def test_set_keys_attributes(self):
        p = Parent()

        subdict = SubAttributesDict(Child, parent=p)

        subdict['key1'].a = 1
        self.assertEqual(subdict['key1'].a, 1)

        subdict['key1'].a = 2
        self.assertEqual(subdict['key1'].a, 2)

        del subdict['key1'].a
        with self.assertRaises(AttributeError):
            subdict['key1'].a

    def test_read_parent_keys(self):
        p = Parent()
        p.c = 3

        subdict = SubAttributesDict(Child, parent=p)

        subdict['key1'].a = 1
        self.assertEqual(subdict['key1'].a, 1)
        self.assertEqual(subdict['key1'].c, 3)
        p.c = 2
        self.assertEqual(subdict['key1'].c, 2)

        del p.c
        with self.assertRaises(AttributeError):
            subdict['key1'].c

    def test_parent_keys_attribute(self):

        class IntChild(Child):

            @classmethod
            def _sanitize_key(self, key):
                try:
                    key = int(key)
                except ValueError:
                    pass
                return key

        class Parent2(Parent):
            @property
            def my_keys(self):
                # Return a generator to catch corner cases.
                # Return a mix of ints and strs to verify _sanitize_key
                yield from [1, '2', 3]

        p = Parent2()
        p.dyn_sub_attr = SubAttributesDict(
            IntChild, parent=p)
        p.fixed_sub_attr = SubAttributesDict(
            IntChild, parent=p, parent_keys_attribute='my_keys')

        # Until they are initialized, the dicts are empty and contain no items
        self.assertNotIn(1, p.dyn_sub_attr)
        self.assertNotIn(1, p.fixed_sub_attr)
        self.assertNotIn(2, p.dyn_sub_attr)
        self.assertNotIn(2, p.fixed_sub_attr)
        self.assertNotIn(3, p.dyn_sub_attr)
        self.assertNotIn(3, p.fixed_sub_attr)
        self.assertNotIn(4, p.dyn_sub_attr)
        self.assertNotIn(4, p.fixed_sub_attr)
        self.assertNotIn(5, p.dyn_sub_attr)
        self.assertNotIn(5, p.fixed_sub_attr)
        self.assertNotIn('1', p.dyn_sub_attr)
        self.assertNotIn('1', p.fixed_sub_attr)
        self.assertNotIn('2', p.dyn_sub_attr)
        self.assertNotIn('2', p.fixed_sub_attr)
        self.assertNotIn('3', p.dyn_sub_attr)
        self.assertNotIn('3', p.fixed_sub_attr)
        self.assertNotIn('4', p.dyn_sub_attr)
        self.assertNotIn('4', p.fixed_sub_attr)
        self.assertNotIn('5', p.dyn_sub_attr)
        self.assertNotIn('5', p.fixed_sub_attr)

        # Although the dicts are empty, parent_keys_attribute announces the
        # keys available for iteration
        self.assertCountEqual(list(p.dyn_sub_attr), [])
        self.assertSequenceEqual(list(p.fixed_sub_attr), [1, 2, 3])
        self.assertCountEqual(list(p.fixed_sub_attr.data), [])

        # Allowed keys can be accessed and missing items are automatically
        # instantiated
        self.assertIsInstance(p.dyn_sub_attr[1], IntChild)
        self.assertIsInstance(p.fixed_sub_attr[1], IntChild)
        self.assertCountEqual(list(p.dyn_sub_attr), [1])
        self.assertSequenceEqual(list(p.fixed_sub_attr), [1, 2, 3])
        self.assertCountEqual(list(p.fixed_sub_attr.data), [1])

        # Once instantiated, the dicts contain these items
        self.assertIn(1, p.dyn_sub_attr)
        self.assertIn(1, p.fixed_sub_attr)
        self.assertNotIn(2, p.dyn_sub_attr)
        self.assertNotIn(2, p.fixed_sub_attr)
        self.assertNotIn(3, p.dyn_sub_attr)
        self.assertNotIn(3, p.fixed_sub_attr)
        self.assertNotIn(4, p.dyn_sub_attr)
        self.assertNotIn(4, p.fixed_sub_attr)
        self.assertNotIn(5, p.dyn_sub_attr)
        self.assertNotIn(5, p.fixed_sub_attr)
        self.assertIn('1', p.dyn_sub_attr)
        self.assertIn('1', p.fixed_sub_attr)
        self.assertNotIn('2', p.dyn_sub_attr)
        self.assertNotIn('2', p.fixed_sub_attr)
        self.assertNotIn('3', p.dyn_sub_attr)
        self.assertNotIn('3', p.fixed_sub_attr)
        self.assertNotIn('4', p.dyn_sub_attr)
        self.assertNotIn('4', p.fixed_sub_attr)
        self.assertNotIn('5', p.dyn_sub_attr)
        self.assertNotIn('5', p.fixed_sub_attr)

        # Only allowed keys are automatically instantiated
        self.assertIsInstance(p.dyn_sub_attr[4], IntChild)
        with self.assertRaises(KeyError):
            p.fixed_sub_attr[4]
        self.assertCountEqual(list(p.dyn_sub_attr), [1, 4])
        self.assertSequenceEqual(list(p.fixed_sub_attr), [1, 2, 3])
        self.assertCountEqual(list(p.fixed_sub_attr.data), [1])

        # Only allowed keys can be assigned
        p.dyn_sub_attr[3] = IntChild(parent=p)
        p.fixed_sub_attr[3] = IntChild(parent=p)
        p.dyn_sub_attr[5] = IntChild(parent=p)
        with self.assertRaises(KeyError):
            p.fixed_sub_attr[5] = IntChild(parent=p)
        self.assertCountEqual(list(p.dyn_sub_attr), [1, 3, 4, 5])
        self.assertSequenceEqual(list(p.fixed_sub_attr), [1, 2, 3])
        self.assertCountEqual(list(p.fixed_sub_attr.data), [1, 3])

        # Once instantiated, the dicts contain these items
        self.assertIn(1, p.dyn_sub_attr)
        self.assertIn(1, p.fixed_sub_attr)
        self.assertNotIn(2, p.dyn_sub_attr)
        self.assertNotIn(2, p.fixed_sub_attr)
        self.assertIn(3, p.dyn_sub_attr)
        self.assertIn(3, p.fixed_sub_attr)
        self.assertIn(4, p.dyn_sub_attr)
        self.assertNotIn(4, p.fixed_sub_attr)
        self.assertIn(5, p.dyn_sub_attr)
        self.assertNotIn(5, p.fixed_sub_attr)
        self.assertIn('1', p.dyn_sub_attr)
        self.assertIn('1', p.fixed_sub_attr)
        self.assertNotIn('2', p.dyn_sub_attr)
        self.assertNotIn('2', p.fixed_sub_attr)
        self.assertIn('3', p.dyn_sub_attr)
        self.assertIn('3', p.fixed_sub_attr)
        self.assertIn('4', p.dyn_sub_attr)
        self.assertNotIn('4', p.fixed_sub_attr)
        self.assertIn('5', p.dyn_sub_attr)
        self.assertNotIn('5', p.fixed_sub_attr)

        # Insert an arbitrary item as if it's key wae previous allowed, but not
        # anymore.
        p.fixed_sub_attr.data[4] = IntChild(parent=p)
        self.assertIn(4, p.fixed_sub_attr)
        self.assertIn('4', p.fixed_sub_attr)
        self.assertSequenceEqual(list(p.fixed_sub_attr), [1, 2, 3])
        self.assertCountEqual(list(p.fixed_sub_attr.data), [1, 3, 4])

        # Existing items can be popped by key name
        do1 = p.dyn_sub_attr[1]
        fo1 = p.fixed_sub_attr[1]
        self.assertIs(p.dyn_sub_attr.pop(1), do1)
        self.assertIs(p.fixed_sub_attr.pop(1), fo1)
        self.assertCountEqual(list(p.dyn_sub_attr), [3, 4, 5])
        self.assertSequenceEqual(list(p.fixed_sub_attr), [1, 2, 3])
        self.assertCountEqual(list(p.fixed_sub_attr.data), [3, 4])

        do3 = p.dyn_sub_attr[3]
        fo3 = p.fixed_sub_attr[3]
        self.assertIs(p.dyn_sub_attr.pop('3'), do3)
        self.assertIs(p.fixed_sub_attr.pop('3'), fo3)
        self.assertCountEqual(list(p.dyn_sub_attr), [4, 5])
        self.assertSequenceEqual(list(p.fixed_sub_attr), [1, 2, 3])
        self.assertCountEqual(list(p.fixed_sub_attr.data), [4])

        # Once popped, the dicts do not contain these items
        self.assertNotIn(1, p.dyn_sub_attr)
        self.assertNotIn(1, p.fixed_sub_attr)
        self.assertNotIn(2, p.dyn_sub_attr)
        self.assertNotIn(2, p.fixed_sub_attr)
        self.assertNotIn(3, p.dyn_sub_attr)
        self.assertNotIn(3, p.fixed_sub_attr)
        self.assertIn(4, p.dyn_sub_attr)
        self.assertIn(4, p.fixed_sub_attr)
        self.assertIn(5, p.dyn_sub_attr)
        self.assertNotIn(5, p.fixed_sub_attr)
        self.assertNotIn('1', p.dyn_sub_attr)
        self.assertNotIn('1', p.fixed_sub_attr)
        self.assertNotIn('2', p.dyn_sub_attr)
        self.assertNotIn('2', p.fixed_sub_attr)
        self.assertNotIn('3', p.dyn_sub_attr)
        self.assertNotIn('3', p.fixed_sub_attr)
        self.assertIn('4', p.dyn_sub_attr)
        self.assertIn('4', p.fixed_sub_attr)
        self.assertIn('5', p.dyn_sub_attr)
        self.assertNotIn('5', p.fixed_sub_attr)

        # Non-existing items cannot be popped
        with self.assertRaises(KeyError):
            p.dyn_sub_attr.pop(2)
        with self.assertRaises(KeyError):
            p.fixed_sub_attr.pop(2)
        self.assertCountEqual(list(p.dyn_sub_attr), [4, 5])
        self.assertSequenceEqual(list(p.fixed_sub_attr), [1, 2, 3])
        self.assertCountEqual(list(p.fixed_sub_attr.data), [4])

        with self.assertRaises(KeyError):
            p.dyn_sub_attr.pop('2')
        with self.assertRaises(KeyError):
            p.fixed_sub_attr.pop('2')
        self.assertCountEqual(list(p.dyn_sub_attr), [4, 5])
        self.assertSequenceEqual(list(p.fixed_sub_attr), [1, 2, 3])
        self.assertCountEqual(list(p.fixed_sub_attr.data), [4])

        self.assertIs(p.dyn_sub_attr.pop(2, False), False)
        self.assertIs(p.dyn_sub_attr.pop('2', False), False)
        self.assertCountEqual(list(p.dyn_sub_attr), [4, 5])
        self.assertSequenceEqual(list(p.fixed_sub_attr), [1, 2, 3])
        self.assertCountEqual(list(p.fixed_sub_attr.data), [4])

        self.assertIs(p.fixed_sub_attr.pop(2, False), False)
        self.assertIs(p.fixed_sub_attr.pop('2', False), False)
        self.assertCountEqual(list(p.dyn_sub_attr), [4, 5])
        self.assertSequenceEqual(list(p.fixed_sub_attr), [1, 2, 3])
        self.assertCountEqual(list(p.fixed_sub_attr.data), [4])

        # Failed pops, don't change the contained items
        self.assertNotIn(1, p.dyn_sub_attr)
        self.assertNotIn(1, p.fixed_sub_attr)
        self.assertNotIn(2, p.dyn_sub_attr)
        self.assertNotIn(2, p.fixed_sub_attr)
        self.assertNotIn(3, p.dyn_sub_attr)
        self.assertNotIn(3, p.fixed_sub_attr)
        self.assertIn(4, p.dyn_sub_attr)
        self.assertIn(4, p.fixed_sub_attr)
        self.assertIn(5, p.dyn_sub_attr)
        self.assertNotIn(5, p.fixed_sub_attr)
        self.assertNotIn('1', p.dyn_sub_attr)
        self.assertNotIn('1', p.fixed_sub_attr)
        self.assertNotIn('2', p.dyn_sub_attr)
        self.assertNotIn('2', p.fixed_sub_attr)
        self.assertNotIn('3', p.dyn_sub_attr)
        self.assertNotIn('3', p.fixed_sub_attr)
        self.assertIn('4', p.dyn_sub_attr)
        self.assertIn('4', p.fixed_sub_attr)
        self.assertIn('5', p.dyn_sub_attr)
        self.assertNotIn('5', p.fixed_sub_attr)

        # popitem returns an arbitraty (key, value) tuple.
        # With parent_keys_attribute, the order is respected.
        p.dyn_sub_attr[1]
        p.fixed_sub_attr[1]
        p.dyn_sub_attr[2]
        p.fixed_sub_attr[2]
        self.assertCountEqual(list(p.dyn_sub_attr), [1, 2, 4, 5])
        self.assertSequenceEqual(list(p.fixed_sub_attr), [1, 2, 3])
        self.assertCountEqual(list(p.fixed_sub_attr.data), [1, 2, 4])
        expected_dl = (
            (1, p.dyn_sub_attr[1]),
            (2, p.dyn_sub_attr[2]),
            (4, p.dyn_sub_attr[4]),
            (5, p.dyn_sub_attr[5]),
        )
        expected_fl = (
            (1, p.fixed_sub_attr[1]),
            (2, p.fixed_sub_attr[2]),
        )
        dl = (
            p.dyn_sub_attr.popitem(),
            p.dyn_sub_attr.popitem(),
            p.dyn_sub_attr.popitem(),
            p.dyn_sub_attr.popitem(),
        )
        fl = (
            p.fixed_sub_attr.popitem(),
            p.fixed_sub_attr.popitem(),
        )
        self.assertCountEqual(expected_dl, dl)
        self.assertSequenceEqual(expected_fl, fl)
        self.assertCountEqual(list(p.dyn_sub_attr), [])
        self.assertSequenceEqual(list(p.fixed_sub_attr), [1, 2, 3])
        self.assertCountEqual(list(p.fixed_sub_attr.data), [4])

        with self.assertRaises(KeyError):
            p.dyn_sub_attr.popitem(),
        with self.assertRaises(KeyError):
            p.fixed_sub_attr.popitem(),
        self.assertCountEqual(list(p.dyn_sub_attr), [])
        self.assertSequenceEqual(list(p.fixed_sub_attr), [1, 2, 3])
        self.assertCountEqual(list(p.fixed_sub_attr.data), [4])

        # clear works and also gets rid of arbitrary items
        p.dyn_sub_attr[1]
        p.fixed_sub_attr[1]
        p.dyn_sub_attr[2]
        p.fixed_sub_attr[2]
        self.assertCountEqual(list(p.dyn_sub_attr), [1, 2])
        self.assertSequenceEqual(list(p.fixed_sub_attr), [1, 2, 3])
        self.assertCountEqual(list(p.fixed_sub_attr.data), [1, 2, 4])
        p.dyn_sub_attr.clear()
        p.fixed_sub_attr.clear()
        self.assertCountEqual(list(p.dyn_sub_attr), [])
        self.assertSequenceEqual(list(p.fixed_sub_attr), [1, 2, 3])
        self.assertCountEqual(list(p.fixed_sub_attr.data), [])
        p.dyn_sub_attr.clear()
        p.fixed_sub_attr.clear()
        self.assertCountEqual(list(p.dyn_sub_attr), [])
        self.assertSequenceEqual(list(p.fixed_sub_attr), [1, 2, 3])
        self.assertCountEqual(list(p.fixed_sub_attr.data), [])

class test_AttributesHelper(unittest.TestCase):

    def test_init(self):

        p = Parent()
        p.a = 'pa'
        p.b = 'pb'
        p.d = {
                'k1': 1,
                'k2': 2,
                'k3': 3,
                }

        h = AttributesHelper(p)

        self.assertIs(type(h.value('a')), str)
        self.assertIs(type(h.value_generator('a')), types.GeneratorType)
        self.assertIs(h.value('a'), p.a)
        self.assertSequenceEqual(list(h.value_generator('a')), [p.a])
        self.assertIs(h.value('b'), p.b)
        self.assertSequenceEqual(list(h.value_generator('b')), [p.b])
        self.assertIs(h.value('c'), None)
        self.assertSequenceEqual(list(h.value_generator('c')), [])

        self.assertIs(type(h.mapping_items('d')), types.GeneratorType)
        self.assertCountEqual(list(h.mapping_items('d')), [
            ('k1', 1, AttributesHelper(p.d['k1'], None)),
            ('k2', 2, AttributesHelper(p.d['k2'], None)),
            ('k3', 3, AttributesHelper(p.d['k3'], None)),
            ])
        self.assertSequenceEqual(list(h.mapping_items('d', sort=True)), [
            ('k1', 1, AttributesHelper(p.d['k1'], None)),
            ('k2', 2, AttributesHelper(p.d['k2'], None)),
            ('k3', 3, AttributesHelper(p.d['k3'], None)),
            ])
        self.assertSequenceEqual(list(h.mapping_items('d', keys=())), [
            ])
        self.assertSequenceEqual(list(h.mapping_items('d', keys=('k1', 'k4'), sort=True)), [
            ('k1', 1, AttributesHelper(p.d['k1'], None)),
            ])

if __name__ == '__main__':
    unittest.main()
