import unittest
import sys, os, copy
import threading

class Test_AbstractModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global test_lib
        global AbstractedModule

        from genie.abstract.magic import AbstractedModule
        from genie.abstract.package import AbstractPackage
        from genie.tests.abstract import test_lib

        cls.pkg = AbstractPackage(test_lib)

    def test_getattr_simple(self):

        am = AbstractedModule(self.pkg, [('nxos', 'n7k'), ('nxos',)])
        self.assertIs(am.simple.Ospf, test_lib.simple.nxos.n7k.Ospf)

        am = AbstractedModule(self.pkg, [('nxos', 'n8k'), ('nxos',)])
        self.assertIs(am.simple.Ospf, test_lib.simple.nxos.Ospf)
        

    def test_getattr_complex(self):

        am = AbstractedModule(self.pkg, [('token_a', 'token_b', 'token_c'),
                                         ('token_a', 'token_b', ),
                                         ('token_a', )])

        self.assertIs(am.complex.module_a.module_b.MyCls, 
                      test_lib.complex.token_a.module_a.module_b.token_b.MyCls)

        am = AbstractedModule(self.pkg, [('token_a', 'token_b', 'token_c'),
                                         ('token_a', 'token_b', ),
                                         ('token_a', )])
        self.assertIs(am.complex.module_a.module_b.module_c.myfile.MyCls, 
                      test_lib.complex.token_a.module_a.module_b.token_b.\
                      module_c.token_c.myfile.MyCls)

    def test_get_attr_error(self):


        am = AbstractedModule(self.pkg, [('token_a', 'token_b', 'token_c'),
                                         ('token_a', 'token_b', ),
                                         ('token_a', )])

        with self.assertRaises(LookupError):
            am.complex.b


class Test_Lookup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global test_lib
        global Lookup

        from genie.abstract.magic import Lookup
        from genie.tests.abstract import test_lib


    def test_lookup_init(self):
        from genie.abstract.magic import default_builder

        l = Lookup()

        self.assertIs(type(l._tokens), tuple)
        self.assertIs(l._builder, default_builder)
        self.assertEqual(l._builder_kwargs, {})
        self.assertEqual(l._pkgs, {'test_lib':
                                    test_lib.__dict__['__abstract_pkg']})

        self.assertTrue(hasattr(l, 'test_lib'))

    def test_lookup_device(self):
        class Device():
            a = 1
            b = 2
            custom = {
                'abstraction': {
                    'order': ['a', 'b'],
                    'a': 100,
                    'b': 200,
                }
            }

        l = Lookup.from_device(Device())
        self.assertEqual(l._tokens, (100, 200))

    def test_lookup_device_only_abstraction(self):
        class Device():
            a = 999
            b = 9999

        l = Lookup.from_device(Device(), default_tokens=['a', 'b'])
        self.assertEqual(l._tokens, (999, 9999))
    
    def test_lookup_device_only_abstraction_optionals(self):
        class Device():
            a = 999
            c = 99999

        l = Lookup.from_device(Device(), default_tokens=['c', 'b', 'a'])
        self.assertEqual(l._tokens, (99999, 999))
    
    def test_lookup_device_default(self):
        class Device():
            custom = {
                'abstraction': {
                    'order': ['a', 'b'],
                    'a': 100,
                    'b': 200,
                }
            }

        l = Lookup.from_device(Device())
        self.assertEqual(l._tokens, (100, 200))

    def test_lookup_device_fallback(self):
        class Device():
            a = 1
            b = 2
            custom = {
                'abstraction': {
                    'order': ['a', 'b'],
                }
            }

        l = Lookup.from_device(Device())
        self.assertEqual(l._tokens, (1, 2))

    def test_lookup_device_error(self):
        class Device():
            custom = {
                'abstraction': {
                    'order': ['a', 'b'],
                }
            }
        with self.assertRaises(ValueError):
            l = Lookup.from_device(Device())

        class Device():
            pass
        with self.assertRaises(ValueError):
            l = Lookup.from_device(Device())

    def test_lookup_device_pkgs(self):
        class Device():
            a = 1
            b = 2
            custom = {
                'abstraction': {
                    'order': ['a', 'b'],
                }
            }

        l = Lookup.from_device(Device(),
                               packages = {'test_lib':test_lib,
                                           'abc': test_lib})

        self.assertTrue(hasattr(l, 'test_lib'))
        self.assertTrue(hasattr(l, 'abc'))

    def test_lookup_stack(self):
        class Device():
            a = 1
            b = 2
            custom = {
                'abstraction': {
                    'order': ['a', 'b'],
                }
            }

        a = test_lib
        b = test_lib
        c = test_lib
        l = Lookup.from_device(Device())

        self.assertTrue(hasattr(l, 'test_lib'))
        self.assertTrue(hasattr(l, 'a'))
        self.assertTrue(hasattr(l, 'b'))
        self.assertTrue(hasattr(l, 'c'))

    def test_lookup_pass_in_pkgs(self):
        l = Lookup(packages = {'test_lib': test_lib,
                               'abc': test_lib})

        self.assertTrue(hasattr(l, 'test_lib'))
        self.assertTrue(hasattr(l, 'abc'))

    def test_custom_builder(self):
        def test(*args): return args

        l = Lookup('a', 'b', 'c', builder = test)

        self.assertEqual(l._sequence, (('a', 'b','c'),))

    def test_default_builder(self):
        def test(*args): return args

        from genie.abstract import magic
        try:
            magic.DEFAULT_BUILDER = test

            l = Lookup('a', 'b', 'c', builder = test)

            self.assertEqual(l._sequence, (('a', 'b','c'),))
        finally:
            magic.DEFAULT_BUILDER = magic.default_builder


    def test_custom_builder_kwargs(self):
        def test(*args, **kwargs): return kwargs

        l = Lookup(a=1,b=2,builder = test)
        self.assertEqual(l._sequence, dict(a=1,b=2))

    def test_caller_stack_collection(self):

        a = test_lib
        b = test_lib
        c = test_lib
        l = Lookup()

        self.assertTrue(hasattr(l, 'test_lib'))
        self.assertTrue(hasattr(l, 'a'))
        self.assertTrue(hasattr(l, 'b'))
        self.assertTrue(hasattr(l, 'c'))

    def test_dir(self):

        a = test_lib
        b = test_lib
        c = test_lib
        l = Lookup()

        self.assertIn('a', dir(l))
        self.assertIn('b', dir(l))
        self.assertIn('c', dir(l))
        self.assertIn('test_lib', dir(l))


class Test_default_builder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global default_builder
        from genie.abstract.magic import default_builder

    def test_simple(self):
        chain = default_builder(['a', 'b', 'c'])

        self.assertEqual(chain, [('a', 'b', 'c'), ('a', 'b'), ('a',), ()])

    def test_mandatory(self):
        chain = default_builder(['a', 'b', 'c','d', 'e'], mandatory = ['c','e'])

        self.assertEqual(chain, [('a', 'b', 'c', 'd', 'e'), 
                                 ('a', 'b', 'c', 'e'), 
                                 ('a', 'c', 'e'), 
                                 ('c', 'e')])

class Test_Threading_Errors(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        global threading_test_lib
        global Lookup

        from genie.abstract import Lookup
        from genie.tests.abstract import threading_test_lib

    def test_threading(self):

        class DeviceA():
            speed = 'slow'
        
        class DeviceB():
            speed = 'fast'

        result = []

        def func(device):
            l = Lookup().from_device(device,
                                     default_tokens = ['speed'],
                                     packages = {'test': threading_test_lib})
            result.append(l.test.api.speed())

        fast = threading.Thread(target=func, args = (DeviceA(),))
        slow = threading.Thread(target=func, args = (DeviceB(),))

        fast.start()
        slow.start()

        fast.join()
        slow.join()

        self.assertEqual(set(result), set(['fast', 'slow']))