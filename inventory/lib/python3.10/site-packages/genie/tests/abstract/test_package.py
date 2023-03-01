import unittest, os
import threading

class Test_AbstractPackage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global test_lib, threading_test_lib
        global AbstractPackage

        from genie.abstract.package import AbstractPackage
        from genie.tests.abstract import test_lib, threading_test_lib

    def test_simple_init(self):

        obj = AbstractPackage(test_lib)

        self.assertTrue(obj.matrix)
        self.assertTrue(obj.learnt)
        self.assertEqual(obj.name, test_lib.__name__)
        self.assertIs(obj.module, test_lib)

    def test_delay_init(self):
        obj = AbstractPackage(test_lib, delay = True)

        self.assertFalse(obj.matrix)
        self.assertFalse(obj.learnt)
        self.assertEqual(obj.name, test_lib.__name__)
        self.assertIs(obj.module, test_lib)

    def test_learn(self):
        
        obj = AbstractPackage(test_lib)
        
        self.assertEqual(sorted(list(obj.matrix.keys())),
                         [('genie', 'tests', 'abstract',  'test_lib'), 
                          ('genie', 'tests', 'abstract',  'test_lib', 'complex'), 
                          ('genie', 'tests', 'abstract',  'test_lib', 'complex', 
                           'module_a'), 
                          ('genie', 'tests', 'abstract',  'test_lib', 'complex', 
                           'module_a', 'module_b'), 
                          ('genie', 'tests', 'abstract',  'test_lib', 'complex', 
                           'module_a', 'module_b', 'module_c'), 
                          ('genie', 'tests', 'abstract',  'test_lib', 'complex', 
                           'module_a', 'module_b', 'module_c', 'myfile'), 
                          ('genie', 'tests', 'abstract',  'test_lib', 'decor'),
                          ('genie', 'tests', 'abstract',  'test_lib', 'simple')])
        self.assertEqual(list(obj.matrix[('genie',
                                          'tests', 
                                          'abstract', 
                                          'test_lib')].keys()),
                         [(),])

        self.assertEqual(sorted(list(obj.matrix[('genie',
                                                 'tests', 
                                                 'abstract', 
                                                 'test_lib',
                                                 'simple')].keys())),
                         [(), 
                          ('iosxe',), 
                          ('iosxe', 'ultra'), 
                          ('iosxe', 'ultra', 'polaris_dev'), 
                          ('nxos',), 
                          ('nxos', 'cli'), 
                          ('nxos', 'n7k'), 
                          ('nxos', 'n7k', 'cli'), 
                          ('nxos', 'n7k', 'yang'), 
                          ('nxos', 'yang')])

        self.assertEqual(sorted(list(obj.matrix[('genie',
                                                 'tests', 
                                                 'abstract', 
                                                 'test_lib',
                                                 'complex')].keys())),
                         [(), ('token_a',)])

        self.assertEqual(sorted(list(obj.matrix[('genie',
                                                 'tests', 
                                                 'abstract', 
                                                 'test_lib',
                                                 'complex',
                                                 'module_a')].keys())),
                         [('token_a',)])

        self.assertEqual(sorted(list(obj.matrix[('genie',
                                                 'tests', 
                                                 'abstract', 
                                                 'test_lib',
                                                 'complex',
                                                 'module_a',
                                                 'module_b')].keys())),
                         [('token_a',), ('token_a', 'token_b')])

        self.assertEqual(sorted(list(obj.matrix[('genie',
                                                 'tests', 
                                                 'abstract', 
                                                 'test_lib',
                                                 'complex',
                                                 'module_a',
                                                 'module_b',
                                                 'module_c')].keys())),
                         [('token_a', 'token_b'),
                          ('token_a', 'token_b', 'token_c')])

        self.assertEqual(sorted(list(obj.matrix[('genie',
                                                 'tests', 
                                                 'abstract', 
                                                 'test_lib',
                                                 'complex',
                                                 'module_a',
                                                 'module_b',
                                                 'module_c', 
                                                 'myfile')].keys())),
                         [('token_a', 'token_b', 'token_c')])


    def test_paths(self):
        obj = AbstractPackage(test_lib)

        self.assertEqual(obj.paths, [os.path.dirname(test_lib.__file__)])

    def test_lookup(self):
        obj = AbstractPackage(test_lib) 

        a = obj.lookup(('genie', 'tests', 'abstract', 'test_lib', 'simple'), 
                        ('nxos','n7k'), 
                        'Ospf')

        assert a is test_lib.simple.nxos.n7k.Ospf

        b = obj.lookup(('genie', 'tests', 'abstract', 'test_lib', 'complex','module_a'), 
                        ('token_a',), 
                        'MyCls')

        assert b is test_lib.complex.token_a.module_a.MyCls

        c = obj.lookup(('genie', 'tests', 'abstract', 'test_lib', 'complex','module_a',
                        'module_b', 'module_c', 'myfile'), 
                        ('token_a', 'token_b', 'token_c'), 
                        'MyCls')

        assert c is test_lib.complex.token_a.module_a.\
        module_b.token_b.module_c.token_c.myfile.MyCls


    def test_lookup_error(self):
        obj = AbstractPackage(test_lib) 

        with self.assertRaises(LookupError):
            a = obj.lookup(('tests', 'abstract',  'test_lib', 'simple'), 
                           ('nxos','n7k'), 
                           'Ospfa')

        with self.assertRaises(LookupError):
            a = obj.lookup(('tests', 'abstract',  'test_lib', 'simple'), 
                           ('nxos','n8k'), 
                           'Ospf')

        with self.assertRaises(LookupError):
            a = obj.lookup(('tests', 'abstract',  'test_lib', 'simle'), 
                           ('nxos','n7k'), 
                           'Ospf')

    def test_registration_error(self):
        from genie.tests.abstract import bad_lib

        with self.assertRaises(ValueError):
            bad_lib.__dict__['__abstract_pkg'].learn()


    def test_threading(self):

        result = []

        obj = AbstractPackage(threading_test_lib, delay=True)
        
        def func(speed):
            obj.learn()
            api = obj.lookup(('genie', 'tests', 'abstract',  'threading_test_lib'),
                             (speed,), 'api')
            result.append(api.speed())
        
        fast = threading.Thread(target=func, args=('fast',))
        slow = threading.Thread(target=func, args=('slow',))

        fast.start()
        slow.start()

        fast.join()
        slow.join()

        self.assertEqual(set(result), set(['fast', 'slow']))