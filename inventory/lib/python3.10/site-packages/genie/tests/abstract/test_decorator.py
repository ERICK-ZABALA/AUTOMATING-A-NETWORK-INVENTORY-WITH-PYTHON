import unittest



class Test_lookupDecorator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global lookup

        from genie.abstract import lookup

    def test_naming(self):
        from genie.abstract.decorator import LookupDecorator

        self.assertIs(LookupDecorator, lookup)

    def test_lookup_init(self):
        from genie.abstract.magic import default_builder
        from genie.abstract.decorator import default_token_getter

        l = lookup()

        self.assertIs(type(l._attrs), tuple)
        self.assertIs(l._getter, default_token_getter)
        self.assertIs(l._builder, default_builder)
        self.assertEqual(l._builder_kwargs, {})
        self.assertIs(l._method, None)
    
    def test_custom_builder(self):
        def test(*args): return args

        l = lookup('a', 'b', 'c', builder = test)

        self.assertIs(l._builder, test)

    def test_custom_builder_kwargs(self):
        def test(*args, **kwargs): return kwargs

        l = lookup(a=1,b=2,builder = test)
        self.assertEqual(l._builder_kwargs, dict(a=1,b=2))

    def test_custom_attr_getter(self):
        def test(*args): return args

        l = lookup('a', 'b', 'c', attr_getter = test)

        self.assertIs(l._getter, test)


    def test_lookup_decorate(self):
        from genie.abstract.decorator import default_token_getter
        from genie.abstract.magic import default_builder

        class Dummy():

            @lookup('os', 'serie', 'type')
            def func(self): return 1

        descriptor = Dummy.__dict__['func']

        self.assertEqual(descriptor._attrs, ('os', 'serie', 'type'))
        self.assertIs(descriptor._getter, default_token_getter)
        self.assertIs(descriptor._builder, default_builder)
        self.assertEqual(descriptor._builder_kwargs, {})

    def test_lookup(self):

        from genie.tests.abstract.test_lib.decor import Ospf

        obj = Ospf('a', 'b', 'c')

        with self.assertRaises(NotImplementedError):
            obj.do_work()

        obj = Ospf('nxos', 'n7k', ' n7003')

        self.assertEqual('genie.tests.abstract.test_lib.decor.nxos', obj.do_work())

        obj = Ospf.OspfChild.OspfChildsChild('xe', None, None)

        self.assertEqual('child.genie.tests.abstract.test_lib.decor.xe', 
                         obj.do_work())
