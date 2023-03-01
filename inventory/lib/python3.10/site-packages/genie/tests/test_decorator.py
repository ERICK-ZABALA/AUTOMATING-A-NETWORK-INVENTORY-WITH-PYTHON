#!/usr/bin/env python

import unittest
from unittest.mock import Mock
from unittest import TestCase

import weakref

from genie.decorator import managedattribute


class test_managedattribute(TestCase):

    def assertTypedEqual(self, first, second, msg=None):
        self.assertEqual(
            (type(first), first),
            (type(second), second),
            msg=msg)

    def test_bare(self):

        class C(object):
            a = managedattribute(
                name='a')

        with self.subTest('descriptor returned with class access'):
            self.assertIs(type(C.a), managedattribute)

        c = C()
        with self.assertRaisesRegex(AttributeError, r'^a$'):
            c.a
        with self.assertRaisesRegex(AttributeError, r'^a$'):
            del c.a
        c.a = 1
        self.assertTypedEqual(c.a, 1)
        del c.a
        with self.assertRaisesRegex(AttributeError, r'^a$'):
            c.a

    def test_arg_checks(self):

        with self.subTest('name'):
            with self.assertRaisesRegex(TypeError, r'^name argument missing$'):

                class C(object):
                    a = managedattribute()

        for def_action1 in managedattribute.DefaultActions.__members__.values():
            for def_action2 in managedattribute.DefaultActions.__members__.values():
                with self.subTest('{}+{}'.format(def_action1.value, def_action2.value)):
                    if def_action1 is def_action2:
                        continue
                    with self.assertRaisesRegex(TypeError, r'.* mutually exclusive$'):

                        class C(object):
                            a = managedattribute(
                                name='a',
                                **{
                                    def_action1.value: tuple,
                                    def_action2.value: tuple,
                                })

        for arg, desc in (
                ('fset', 'setter'),
                ('fdel', 'deleter'),
                ('type', 'type'),
        ):
            with self.subTest('read_only+{}'.format(arg)):
                with self.assertRaisesRegex(TypeError, r'^read-only attributes cannot have a %s$' % (desc,)):

                    class C(object):
                        a = managedattribute(
                            name='a',
                            read_only=True,
                            **{
                                arg: tuple,  # dummy callable
                            })

    def test_getter(self):

        class C(object):
            a = managedattribute(
                name='a')

            @a.getter
            def a(self):
                try:
                    return self._a + 1
                except AttributeError:
                    return 1

        c = C()
        self.assertTypedEqual(c.a, 1)
        with self.assertRaisesRegex(AttributeError, r'^a$'):
            del c.a
        c.a = 2
        self.assertTypedEqual(c.a, 3)
        del c.a
        self.assertTypedEqual(c.a, 1)

    def test_setter(self):

        class C(object):
            a = managedattribute(
                name='a')

            @a.setter
            def a(self, value):
                self._a = value + 1

        c = C()
        with self.assertRaisesRegex(AttributeError, r'^a$'):
            c.a
        with self.assertRaisesRegex(AttributeError, r'^a$'):
            del c.a
        c.a = 2
        self.assertTypedEqual(c.a, 3)
        del c.a
        with self.assertRaisesRegex(AttributeError, r'^a$'):
            c.a

    def test_deleter(self):

        class C(object):
            a = managedattribute(
                name='a')

            @a.deleter
            def a(self):
                try:
                    a = self._a
                except AttributeError:
                    raise AttributeError
                a = a - 1
                if not a:
                    del self._a
                else:
                    self._a = a

        c = C()
        with self.assertRaisesRegex(AttributeError, r'^a$'):
            c.a
        with self.assertRaisesRegex(AttributeError, r'^a$'):
            del c.a
        c.a = 2
        self.assertTypedEqual(c.a, 2)
        del c.a
        self.assertTypedEqual(c.a, 1)
        del c.a
        with self.assertRaisesRegex(AttributeError, r'^a$'):
            c.a
        with self.assertRaisesRegex(AttributeError, r'^a$'):
            del c.a

    def test_default(self):

        class C(object):
            a = managedattribute(
                default=1,
                name='a')

        c = C()
        self.assertTypedEqual(c.a, 1)
        with self.assertRaisesRegex(AttributeError, r'^a$'):
            del c.a
        c.a = 2
        self.assertTypedEqual(c.a, 2)
        del c.a
        self.assertTypedEqual(c.a, 1)

    def test_init(self):

        o1 = []

        class C(object):
            a = managedattribute(
                init=o1,
                name='a')

        c = C()
        with self.assertRaisesRegex(AttributeError, r'^a$'):
            del c.a
        self.assertIs(c.a, o1)
        self.assertTypedEqual(c.a, [])
        c.a.append(1)
        self.assertIs(c.a, o1)
        self.assertTypedEqual(o1, [1])
        c.a = 2
        self.assertTypedEqual(c.a, 2)
        self.assertTypedEqual(o1, [1])
        del c.a
        self.assertIs(c.a, o1)
        self.assertTypedEqual(o1, [1])
        del c.a
        with self.assertRaisesRegex(AttributeError, r'^a$'):
            del c.a
        self.assertIs(c.a, o1)
        self.assertTypedEqual(o1, [1])

    def test_initter(self):

        tc = self
        for subtest in ('function arg', 'method arg', 'decorator'):
            with self.subTest(subtest):

                if subtest == 'function arg':

                    class C(object):
                        a = managedattribute(
                            finit=list,
                            name='a')

                elif subtest == 'method arg':

                    class C(object):

                        def a_initter(self):
                            tc.assertIsInstance(self, C)
                            return list()
                        a = managedattribute(
                            finit_method=a_initter,
                            name='a')

                elif subtest == 'decorator':

                    class C(object):
                        a = managedattribute(
                            name='a')

                        @a.initter
                        def a(self):
                            tc.assertIsInstance(self, C)
                            return list()

                else:
                    raise ValueError(subtest)

                c = C()
                with self.assertRaisesRegex(AttributeError, r'^a$'):
                    del c.a
                self.assertTypedEqual(c.a, [])
                o1 = c.a
                self.assertTypedEqual(c.a, [])
                self.assertIs(c.a, o1)
                c.a.append(1)
                self.assertTypedEqual(c.a, [1])
                c.a = 2
                self.assertTypedEqual(c.a, 2)
                del c.a
                self.assertTypedEqual(c.a, [])
                self.assertIsNot(c.a, o1)
                del c.a
                with self.assertRaisesRegex(AttributeError, r'^a$'):
                    del c.a
                self.assertTypedEqual(c.a, [])

    def test_defaulter(self):

        tc = self
        for subtest in ('function arg', 'method arg', 'decorator'):
            with self.subTest(subtest):

                if subtest == 'function arg':

                    class C(object):
                        a = managedattribute(
                            fdef=list,
                            name='a')

                elif subtest == 'method arg':

                    class C(object):

                        def a_defaulter(self):
                            tc.assertIsInstance(self, C)
                            return list()
                        a = managedattribute(
                            fdef_method=a_defaulter,
                            name='a')

                elif subtest == 'decorator':

                    class C(object):
                        a = managedattribute(
                            name='a')

                        @a.defaulter
                        def a(self):
                            tc.assertIsInstance(self, C)
                            return list()

                else:
                    raise ValueError(subtest)

                c = C()
                with self.assertRaisesRegex(AttributeError, r'^a$'):
                    del c.a
                self.assertTypedEqual(c.a, [])
                o1 = c.a
                self.assertTypedEqual(c.a, [])
                self.assertIsNot(c.a, o1)
                c.a.append(1)
                self.assertTypedEqual(c.a, [])
                c.a = 2
                self.assertTypedEqual(c.a, 2)
                del c.a
                self.assertTypedEqual(c.a, [])
                o1 = c.a
                self.assertTypedEqual(c.a, [])
                self.assertIsNot(c.a, o1)
                with self.assertRaisesRegex(AttributeError, r'^a$'):
                    del c.a
                self.assertTypedEqual(c.a, [])

    def test_attr(self):

        tc = self
        for subtest in ('default attr', 'attr arg'):
            with self.subTest(subtest):

                if subtest == 'default attr':
                    attr = '_a'

                    class C(object):
                        a = managedattribute(
                            name='a')

                elif subtest == 'attr arg':
                    attr = 'b'

                    class C(object):
                        a = managedattribute(
                            attr=attr,
                            name='a')

                else:
                    raise ValueError(subtest)

                c = C()
                with self.assertRaisesRegex(AttributeError, r'^a$'):
                    c.a
                with self.assertRaisesRegex(AttributeError, r'^\'C\' object has no attribute \'%s\'$' % (attr,)):
                    getattr(c, attr)
                c.a = 1
                self.assertTypedEqual(c.a, 1)
                self.assertTypedEqual(getattr(c, attr), 1)
                del c.a
                with self.assertRaisesRegex(AttributeError, r'^a$'):
                    c.a
                with self.assertRaisesRegex(AttributeError, r'^\'C\' object has no attribute \'%s\'$' % (attr,)):
                    getattr(c, attr)

    def test_type(self):

        for arg, desc in (
                (int, 'class'),
                ((int,), 'tuple-of-1'),
        ):
            with self.subTest(type=desc):

                class C(object):
                    a = managedattribute(
                        type=arg,
                        name='a')

                c = C()
                c.a = 1
                self.assertTypedEqual(c.a, 1)
                c.a = '1'
                self.assertTypedEqual(c.a, 1)
                with self.assertRaisesRegex(ValueError, r'''^None: int\(\) argument must be a string[a-z\s\-\,]+, not 'NoneType'\.$'''):
                    c.a = None

                self.assertTypedEqual(c.a, 1)
                with self.assertRaisesRegex(ValueError, r'''^x: invalid literal for int\(\) with base 10: 'x'\.$'''):
                    c.a = 'x'
                self.assertTypedEqual(c.a, 1)

        with self.subTest(type='tuple-of-1'):

            class C(object):
                a = managedattribute(
                    type=(int,),
                    name='a')

            c = C()
            c.a = 1
            self.assertTypedEqual(c.a, 1)
            c.a = '1'
            self.assertTypedEqual(c.a, 1)
            with self.assertRaisesRegex(ValueError, r'''^None: int\(\) argument must be a string[a-z\s\-\,]+, not 'NoneType'\.$'''):
                c.a = None
            self.assertTypedEqual(c.a, 1)
            with self.assertRaisesRegex(ValueError, r'''^x: invalid literal for int\(\) with base 10: 'x'\.$'''):
                c.a = 'x'
            self.assertTypedEqual(c.a, 1)

        with self.subTest(type='tuple-of-2'):

            class C(object):
                a = managedattribute(
                    type=(None, int,),
                    name='a')

            c = C()
            c.a = 1
            self.assertTypedEqual(c.a, 1)
            c.a = '1'
            self.assertTypedEqual(c.a, 1)
            c.a = None
            self.assertTypedEqual(c.a, None)
            with self.assertRaisesRegex(ValueError, r'''^x: Not None. invalid literal for int\(\) with base 10: 'x'\.$'''):
                c.a = 'x'
            self.assertTypedEqual(c.a, None)

    def test_type_test_isinstance(self):

        with self.subTest(type='test_isinstance-of-1'):

            class C(object):
                a = managedattribute(
                    type=managedattribute.test_isinstance(int),
                    name='a')

            class MyInt(int):
                pass

            c = C()
            c.a = 1
            self.assertTypedEqual(c.a, 1)
            with self.assertRaisesRegex(ValueError, r'''^None: Not an instance of int\.$'''):
                c.a = None
            with self.assertRaisesRegex(ValueError, r'''^x: Not an instance of int\.$'''):
                c.a = 'x'
            self.assertTypedEqual(c.a, 1)
            c.a = v = MyInt(2)
            self.assertIs(c.a, v)

        with self.subTest(type='test_isinstance-of-2'):

            class C(object):
                a = managedattribute(
                    type=managedattribute.test_isinstance((int, dict)),
                    name='a')

            class MyInt(int):
                pass

            c = C()
            c.a = v = dict()
            self.assertIs(c.a, v)
            c.a = 1
            self.assertTypedEqual(c.a, 1)
            with self.assertRaisesRegex(ValueError, r'''^None: Not an instance of int or dict\.$'''):
                c.a = None
            with self.assertRaisesRegex(ValueError, r'''^x: Not an instance of int or dict\.$'''):
                c.a = 'x'
            self.assertTypedEqual(c.a, 1)
            c.a = v = MyInt(2)
            self.assertIs(c.a, v)

    def test_type_test_istype(self):

        with self.subTest(type='test_istype-of-1'):

            class C(object):
                a = managedattribute(
                    type=managedattribute.test_istype(int),
                    name='a')

            class MyInt(int):
                pass

            c = C()
            c.a = 1
            self.assertTypedEqual(c.a, 1)
            with self.assertRaisesRegex(ValueError, r'''^None: Not of type int\.$'''):
                c.a = None
            with self.assertRaisesRegex(ValueError, r'''^x: Not of type int\.$'''):
                c.a = 'x'
            self.assertTypedEqual(c.a, 1)
            with self.assertRaisesRegex(ValueError, r'''^2: Not of type int\.$'''):
                c.a = MyInt(2)
            self.assertTypedEqual(c.a, 1)

        with self.subTest(type='test_istype-of-2'):

            class C(object):
                a = managedattribute(
                    type=managedattribute.test_istype((int, dict)),
                    name='a')

            class MyInt(int):
                pass

            c = C()
            c.a = v = dict()
            self.assertIs(c.a, v)
            c.a = 1
            self.assertTypedEqual(c.a, 1)
            with self.assertRaisesRegex(ValueError, r'''^None: Not of type int or dict\.$'''):
                c.a = None
            with self.assertRaisesRegex(ValueError, r'''^x: Not of type int or dict\.$'''):
                c.a = 'x'
            self.assertTypedEqual(c.a, 1)
            with self.assertRaisesRegex(ValueError, r'''^2: Not of type int or dict\.$'''):
                c.a = MyInt(2)
            self.assertTypedEqual(c.a, 1)

    def test_type_test_in(self):

        with self.subTest('sequence'):

            class C(object):
                a = managedattribute(
                    type=managedattribute.test_in((None, 4, 6)),
                    name='a')

            c = C()
            c.a = None
            self.assertIs(c.a, None)
            c.a = 4
            self.assertTypedEqual(c.a, 4)
            with self.assertRaisesRegex(ValueError, r'''^5: Not in \(None, 4, 6\)\.$'''):
                c.a = 5
            self.assertTypedEqual(c.a, 4)
            c.a = 6
            self.assertTypedEqual(c.a, 6)

        with self.subTest('range'):

            class C(object):
                a = managedattribute(
                    type=managedattribute.test_in(range(4)),
                    name='a')

            c = C()
            c.a = 0
            self.assertTypedEqual(c.a, 0)
            c.a = 1
            self.assertTypedEqual(c.a, 1)
            c.a = 2
            self.assertTypedEqual(c.a, 2)
            c.a = 3
            self.assertTypedEqual(c.a, 3)
            with self.assertRaisesRegex(ValueError, r'''^4: Not in range\(0, 4\)\.$'''):
                c.a = 4
            self.assertTypedEqual(c.a, 3)
            with self.assertRaisesRegex(ValueError, r'''^None: Not in range\(0, 4\)\.$'''):
                c.a = None
            self.assertTypedEqual(c.a, 3)

    def test_type_test_set_of(self):

        with self.subTest(type='test_set_of-empty'):
            with self.assertRaisesRegex(ValueError, r'''^Empty tuple of transformations.$'''):

                class C(object):
                    a = managedattribute(
                        type=managedattribute.test_set_of(()),
                        name='a')

        for arg, desc in (
                (int, 'class'),
                ((int,), 'tuple-of-1'),
        ):
            with self.subTest(type='test_set_of-' + desc):

                class C(object):
                    a = managedattribute(
                        type=managedattribute.test_set_of(arg),
                        name='a')

                c = C()
                with self.assertRaisesRegex(ValueError, r'''^1: 'int' object is not iterable\.$'''):
                    c.a = 1
                c.a = [1, 1, 2]
                self.assertTypedEqual(c.a, {1, 2})
                v = c.a
                c.a.add(3)
                self.assertTypedEqual(c.a, {1, 2, 3})
                self.assertIs(c.a, v)
                with self.assertRaisesRegex(ValueError, r'''^\[1, 1, 2, 'x'\]: Not cast to set \(x: invalid literal for int\(\) with base 10: 'x'\.\)\.$'''):
                    c.a = [1, 1, 2, 'x']
                self.assertTypedEqual(c.a, {1, 2, 3})
                self.assertIs(c.a, v)
                with self.assertRaisesRegex(ValueError, r'''^\[1, 1, 2, None\]: Not cast to set \(None: int\(\) argument must be a string[a-z\s\-\,]+, not 'NoneType'\.\)\.$'''):
                    c.a = [1, 1, 2, None]
                self.assertTypedEqual(c.a, {1, 2, 3})
                self.assertIs(c.a, v)

        with self.subTest(type='test_set_of-tuple-of-2'):

            class C(object):
                a = managedattribute(
                    type=managedattribute.test_set_of((int, None)),
                    name='a')

            c = C()
            with self.assertRaisesRegex(ValueError, r'''^1: 'int' object is not iterable\.$'''):
                c.a = 1
            c.a = [1, 1, 2]
            self.assertTypedEqual(c.a, {1, 2})
            v = c.a
            c.a.add(3)
            self.assertTypedEqual(c.a, {1, 2, 3})
            self.assertIs(c.a, v)
            with self.assertRaisesRegex(ValueError, r'''^\[1, 1, 2, 'x'\]: Not cast to set \(x: invalid literal for int\(\) with base 10: 'x'\. Not None\.\)\.$'''):
                c.a = [1, 1, 2, 'x']
            self.assertTypedEqual(c.a, {1, 2, 3})
            self.assertIs(c.a, v)
            c.a = [1, 1, 2, None]
            self.assertTypedEqual(c.a, {1, 2, None})
            self.assertIsNot(c.a, v)

    def test_type_test_list_of(self):

        with self.subTest(type='test_list_of-empty'):
            with self.assertRaisesRegex(ValueError, r'''^Empty tuple of transformations.$'''):

                class C(object):
                    a = managedattribute(
                        type=managedattribute.test_list_of(()),
                        name='a')

        for arg, desc in (
                (int, 'class'),
                ((int,), 'tuple-of-1'),
        ):
            with self.subTest(type='test_list_of-' + desc):

                class C(object):
                    a = managedattribute(
                        type=managedattribute.test_list_of(arg),
                        name='a')

                c = C()
                with self.assertRaisesRegex(ValueError, r'''^1: 'int' object is not iterable\.$'''):
                    c.a = 1
                c.a = [1, 1, 2]
                self.assertTypedEqual(c.a, [1, 1, 2])
                v = c.a
                with self.assertRaisesRegex(ValueError, r'''^\[1, 1, 2, 'x'\]: Not cast to list \(x: invalid literal for int\(\) with base 10: 'x'\.\)\.$'''):
                    c.a = [1, 1, 2, 'x']
                self.assertTypedEqual(c.a, [1, 1, 2])
                self.assertIs(c.a, v)
                with self.assertRaisesRegex(ValueError, r'''^\[1, 1, 2, None\]: Not cast to list \(None: int\(\) argument must be a string[a-z\s\-\,]+, not 'NoneType'\.\)\.$'''):
                    c.a = [1, 1, 2, None]
                self.assertTypedEqual(c.a, [1, 1, 2])
                self.assertIs(c.a, v)

        with self.subTest(type='test_list_of-tuple-of-2'):

            class C(object):
                a = managedattribute(
                    type=managedattribute.test_list_of((int, None)),
                    name='a')

            c = C()
            with self.assertRaisesRegex(ValueError, r'''^1: 'int' object is not iterable\.$'''):
                c.a = 1
            c.a = [1, 1, 2]
            self.assertTypedEqual(c.a, [1, 1, 2])
            v = c.a
            with self.assertRaisesRegex(ValueError, r'''^\[1, 1, 2, 'x'\]: Not cast to list \(x: invalid literal for int\(\) with base 10: 'x'\. Not None\.\)\.$'''):
                c.a = [1, 1, 2, 'x']
            self.assertTypedEqual(c.a, [1, 1, 2])
            self.assertIs(c.a, v)
            c.a = [1, 1, 2, None]
            self.assertTypedEqual(c.a, [1, 1, 2, None])
            self.assertIsNot(c.a, v)

    def test_type_test_tuple_of(self):

        with self.subTest(type='test_tuple_of-empty'):
            with self.assertRaisesRegex(ValueError, r'''^Empty tuple of transformations.$'''):

                class C(object):
                    a = managedattribute(
                        type=managedattribute.test_tuple_of(()),
                        name='a')

        for arg, desc in (
                (int, 'class'),
                ((int,), 'tuple-of-1'),
        ):
            with self.subTest(type='test_tuple_of-' + desc):

                class C(object):
                    a = managedattribute(
                        type=managedattribute.test_tuple_of(arg),
                        name='a')

                c = C()
                with self.assertRaisesRegex(ValueError, r'''^1: 'int' object is not iterable\.$'''):
                    c.a = 1
                c.a = [1, 1, 2]
                self.assertTypedEqual(c.a, (1, 1, 2))
                v = c.a
                with self.assertRaisesRegex(ValueError, r'''^\[1, 1, 2, 'x'\]: Not cast to tuple \(x: invalid literal for int\(\) with base 10: 'x'\.\)\.$'''):
                    c.a = [1, 1, 2, 'x']
                self.assertTypedEqual(c.a, (1, 1, 2))
                self.assertIs(c.a, v)
                with self.assertRaisesRegex(ValueError, r'''^\[1, 1, 2, None\]: Not cast to tuple \(None: int\(\) argument must be a string[a-z\s\-\,]+, not 'NoneType'\.\)\.$'''):
                    c.a = [1, 1, 2, None]
                self.assertTypedEqual(c.a, (1, 1, 2))
                self.assertIs(c.a, v)

        with self.subTest(type='test_tuple_of-tuple-of-2'):

            class C(object):
                a = managedattribute(
                    type=managedattribute.test_tuple_of((int, None)),
                    name='a')

            c = C()
            with self.assertRaisesRegex(ValueError, r'''^1: 'int' object is not iterable\.$'''):
                c.a = 1
            c.a = [1, 1, 2]
            self.assertTypedEqual(c.a, (1, 1, 2))
            v = c.a
            with self.assertRaisesRegex(ValueError, r'''^\[1, 1, 2, 'x'\]: Not cast to tuple \(x: invalid literal for int\(\) with base 10: 'x'\. Not None\.\)\.$'''):
                c.a = [1, 1, 2, 'x']
            self.assertTypedEqual(c.a, (1, 1, 2))
            self.assertIs(c.a, v)
            c.a = [1, 1, 2, None]
            self.assertTypedEqual(c.a, (1, 1, 2, None))
            self.assertIsNot(c.a, v)

    def test_type_auto_ref(self):

        class B(object):
            pass

        class C(object):
            a = managedattribute(
                type=managedattribute.auto_ref,
                name='a')

        c = C()

        b1 = B()
        c.a = b1
        self.assertIsInstance(c._a, weakref.ReferenceType)
        self.assertIs(c._a(), b1)
        self.assertIsInstance(c.a, weakref.ReferenceType)
        self.assertIs(c.a(), b1)

        c.a = 1
        self.assertIsInstance(c._a, int)
        self.assertEqual(c._a, 1)
        self.assertIsInstance(c.a, int)
        self.assertEqual(c.a, 1)

    def test_type_test_auto_ref(self):

        class B(object):
            pass

        class C(object):
            a = managedattribute(
                type=managedattribute.test_auto_ref((
                    managedattribute.test_isinstance(B),
                    int,
                )),
                name='a')

        c = C()

        with self.assertRaisesRegex(ValueError, r'''^blah: blah: Not an instance of B\. invalid literal for int\(\) with base 10: 'blah'\.$'''):
            c.a = 'blah'

        b1 = B()
        c.a = b1
        self.assertIsInstance(c._a, weakref.ReferenceType)
        self.assertIs(c._a(), b1)
        self.assertIsInstance(c.a, weakref.ReferenceType)
        self.assertIs(c.a(), b1)

        c.a = 1
        self.assertIsInstance(c._a, int)
        self.assertEqual(c._a, 1)
        self.assertIsInstance(c.a, int)
        self.assertEqual(c.a, 1)

    def test_gettype(self):

        for arg, desc in (
                (int, 'class'),
                ((int,), 'tuple-of-1'),
        ):
            with self.subTest(gettype=desc):

                class C(object):
                    a = managedattribute(
                        gettype=arg,
                        name='a')

                c = C()
                c.a = 1
                self.assertTypedEqual(c._a, 1)
                self.assertTypedEqual(c.a, 1)
                c.a = '1'
                self.assertTypedEqual(c._a, '1')
                self.assertTypedEqual(c.a, 1)
                c.a = 'x'
                self.assertTypedEqual(c._a, 'x')
                with self.assertRaisesRegex(AttributeError, r'''^a$'''):
                    c.a
                c.a = None
                self.assertTypedEqual(c._a, None)
                with self.assertRaisesRegex(AttributeError, r'''^a$'''):
                    c.a

        with self.subTest(gettype='tuple-of-2'):

            class C(object):
                a = managedattribute(
                    gettype=(None, int,),
                    name='a')

            c = C()
            c.a = 1
            self.assertTypedEqual(c._a, 1)
            self.assertTypedEqual(c.a, 1)
            c.a = '1'
            self.assertTypedEqual(c._a, '1')
            self.assertTypedEqual(c.a, 1)
            c.a = 'x'
            self.assertTypedEqual(c._a, 'x')
            with self.assertRaisesRegex(AttributeError, r'''^a$'''):
                c.a
            c.a = None
            self.assertTypedEqual(c._a, None)
            self.assertTypedEqual(c.a, None)

    def test_gettype_auto_unref(self):

        class B(object):
            pass

        class C(object):
            a = managedattribute(
                gettype=managedattribute.auto_unref,
                name='a')

        c = C()
        b1 = B()

        c.a = b1
        self.assertIs(c._a, b1)
        self.assertIs(c.a, b1)

        c.a = 1
        self.assertIs(c._a, 1)
        self.assertIs(c.a, 1)

        c.a = None
        self.assertIs(c._a, None)
        self.assertIs(c.a, None)

        c.a = weakref.ref(b1)
        self.assertIsInstance(c._a, weakref.ReferenceType)
        self.assertIs(c._a(), b1)
        self.assertIs(c.a, b1)

    def test_read_only(self):

        class C(object):
            a = managedattribute(
                read_only=True,
                name='a')

        c = C()
        with self.assertRaisesRegex(AttributeError, r'^a$'):
            c.a
        with self.assertRaisesRegex(AttributeError, r'''^can't delete attribute$'''):
            del c.a
        with self.assertRaisesRegex(AttributeError, r'''^can't set attribute$'''):
            c.a = 1
        c._a = 1
        self.assertTypedEqual(c.a, 1)
        with self.assertRaisesRegex(AttributeError, r'''^can't delete attribute$'''):
            del c.a
        self.assertTypedEqual(c.a, 1)

    def test_doc(self):

        class C(object):
            a = managedattribute(
                name='a')

        self.assertIs(C.a.__doc__, None)

        class C(object):
            a = managedattribute(
                doc='arg-doc',
                name='a')

        self.assertEqual(C.a.__doc__, 'arg-doc')

        class C(object):

            def fget(self):
                pass
            a = managedattribute(
                fget=fget,
                name='a')

        self.assertIs(C.a.__doc__, None)

        class C(object):

            def fget(self):
                '''getter-doc'''
                pass
            a = managedattribute(
                fget=fget,
                name='a')

        self.assertEqual(C.a.__doc__, 'getter-doc')

        class C(object):
            a = managedattribute(
                name='a')

            @a.getter
            def a(self):
                '''getter-doc'''
                pass

        self.assertEqual(C.a.__doc__, 'getter-doc')

        class C(object):

            def fget(self):
                '''getter-doc'''
                pass
            a = managedattribute(
                fget=fget,
                name='a')

            @a.getter
            def a(self):
                '''getter-doc2'''
                pass

        self.assertEqual(C.a.__doc__, 'getter-doc2')

        class C(object):
            a = managedattribute(
                name='a')

            @a.getter
            def a(self):
                '''getter-doc'''
                pass

            @a.getter
            def a(self):
                '''getter-doc2'''
                pass

        self.assertEqual(C.a.__doc__, 'getter-doc2')

        class C(object):

            def fget(self):
                '''getter-doc'''
            a = managedattribute(
                doc='arg-doc',
                name='a')

            @a.getter
            def a(self):
                '''getter-doc'''
                pass

        self.assertEqual(C.a.__doc__, 'arg-doc')

if __name__ == '__main__':
    unittest.main()

# vim: ft=python et sw=4
