import re
import unittest

from genie.ops.base.base import Base
from genie.ops.base.maker import Maker
from genie.ops.base.maker import CmdDict

from genie.ops.base.exceptions import InvalidDest
from genie.conf.base import Device
from genie.conf.base import Testbed

from genie.metaparser import MetaParser
from genie.metaparser.util.schemaengine import (Any,
                                                Optional)

def _dict_compare(a,b):
    '''Make sure a is in b'''
    for key,value in a.items():
        assert key in b
        assert value == b[key]
    return True

class FakeParserSchema(MetaParser):
    ''' Fake parser schema for test
    '''
    schema = {
        Any() : Any()
    }

class FakeParser_1(FakeParserSchema):
    ''' Fake parser for unit tests
    '''
    def cli(self):
        return {
            'l1_a':'a'}

class FakeParser_2(FakeParserSchema):
    ''' Fake parser for unit tests
    '''
    def cli(self):
        return {
            'l1_a':'a',
            'l1_b':'b'}

class FakeParser_3(FakeParserSchema):
    ''' Fake parser for unit tests
    '''
    def cli(self):
        return {
            'l1_a':{
                'l2_a':'aa', 
                'l2_ab':'ab'},
             'l1_b':{
                'l2_bb':'ba', 
                'l2_c':'bc'}}

class FakeParser_4(FakeParserSchema):
    ''' Fake parser for unit tests
    '''
    def cli(self):
        return {
            'l1_a':{
                'l2_a':'aa', 
                'l2_ab':'ab'},
            'l1_b':{
                'l2_bb':'ba', 
                'l2_c':'bc',
                'l2_d':{
                    'l3_d':'ff'}}}

class FakeParser_5(FakeParserSchema):
    ''' Fake parser for unit tests
    '''
    def cli(self):
        return {
            'l1_a':{
                'l2_a':'aa', 
                'l2_ab':'ab'}}

class FakeParser_6(FakeParserSchema):
    ''' Fake parser for unit tests
    '''
    def cli(self):
        return {
            'l1_a':{
                5:'aa', 
                'l2_ab':'ab'}}

class FakeParser_7(FakeParserSchema):
    ''' Fake parser for unit tests
    '''
    def cli(self):
        return {
            'l1_a':{
                5:'aa'}}

class test_maker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.testbed = Testbed()
        cls.dev1 = Device(name='pe1', testbed=cls.testbed, os='nxos')

    def setUp(self):
        try:
            del self.schema
        except:
            pass


    callables = {}

    cli_1 = {'l1_a':'a'}
    cli_2 = {'l1_a':'a',
             'l1_b':'b'}
    cli_3 = {'l1_a':{'l2_a':'aa', 'l2_ab':'ab'},
             'l1_b':{'l2_bb':'ba', 'l2_c':'bc'}}
    cli_4 = {'l1_a':{'l2_a':'aa', 'l2_ab':'ab'},
             'l1_b':{'l2_bb':'ba', 'l2_c':'bc',
                      'l2_d':{'l3_d':'ff'}}}
    cli_5 = {'l1_a':{'l2_a':'aa', 'l2_ab':'ab'}}
    cli_6 = {'l1_a':{5:'aa', 'l2_ab':'ab'}}
    cli_7 = {'l1_a':{5:'aa'}}

    def test_init(self):
        pre_dir = dir(self)
        m = Maker(parent=self)
        m.make()
        post_dir = dir(self)
        self.assertEqual(pre_dir, post_dir)

    # Test of simple structure manipulation

    def test_dest_missing_2levels_regex(self):
        pre_dir = dir(self)
        m = Maker(parent=self)
        m.outputs[FakeParser_6] = {'':self.cli_6}
        m.add_leaf(cmd=FakeParser_6,
                   device=self.dev1,
                   src='[l1_a][(?P<group>.*)]',
                   dest='x[s]')

        # Make sure it finds the right output
        with self.assertRaises(InvalidDest):
            m.make()

    def test_dest_missing_1levels_regex(self):
        pre_dir = dir(self)
        m = Maker(parent=self)
        m.outputs[FakeParser_6] = {'':self.cli_6}
        m.add_leaf(cmd=FakeParser_6,
                   device=self.dev1,
                   src='[l1_a][(?P<group>.*)]',
                   dest='x')

        # Make sure it finds the right output
        with self.assertRaises(InvalidDest):
            m.make()

    def test_dest_missing_2levels_regex2(self):
        pre_dir = dir(self)
        m = Maker(parent=self)
        m.outputs[FakeParser_7] = {'':self.cli_7}
        m.add_leaf(cmd=FakeParser_7,
                   device=self.dev1,
                   src='[l1_a][(?P<group>.*)]',
                   dest='l1_a[s]')

        # Make sure it finds the right output
        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(self.l1_a['s'], self.cli_7['l1_a'][5])
        post_dir = dir(self)
        extra = set(post_dir) - set(pre_dir)
        self.assertEqual(extra, {'l1_a'})

        m.make()

        post_post_dir = dir(self)
        self.assertEqual(post_post_dir, post_dir)

    def test_dest_missing_1levels_regex2(self):
        pre_dir = dir(self)
        m = Maker(parent=self)
        m.outputs[FakeParser_7] = {'':self.cli_7}
        m.add_leaf(cmd=FakeParser_7,
                   device=self.dev1,
                   src='[l1_a][(?P<group>.*)]',
                   dest='l1_a')

        # Make sure it finds the right output
        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(self.l1_a, self.cli_7['l1_a'][5])
        post_dir = dir(self)
        extra = set(post_dir) - set(pre_dir)
        self.assertEqual(extra, {'l1_a'})

        m.make()

        post_post_dir = dir(self)
        self.assertEqual(post_post_dir, post_dir)

    def test_int(self):
        pre_dir = dir(self)
        m = Maker(parent=self)
        m.outputs[FakeParser_6] = {'':self.cli_6}
        m.add_leaf(cmd=FakeParser_6,
                   device=self.dev1,
                   src='[l1_a][(?P<group>.*)]',
                   dest='l1_a[(?P<group>.*)]')
        # Make sure it finds the right output
        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(self.l1_a, self.cli_6['l1_a'])
        post_dir = dir(self)
        extra = set(post_dir) - set(pre_dir)
        self.assertEqual(extra, {'l1_a'})

        m.make()

        post_post_dir = dir(self)
        self.assertEqual(post_post_dir, post_dir)


    def test_same_structure(self):
        pre_dir = dir(self)
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.outputs[FakeParser_5] = {'':self.cli_5}
        m.add_leaf(cmd=FakeParser_1,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a')
        # Make sure it finds the right output
        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(self.l1_a, self.cli_1['l1_a'])
        post_dir = dir(self)
        extra = set(post_dir) - set(pre_dir)
        self.assertEqual(extra, {'l1_a'})

        m.make()

        post_post_dir = dir(self)
        self.assertEqual(post_post_dir, post_dir)

    def test_change_structure(self):
        pre_dir = dir(self)
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.add_leaf(cmd=FakeParser_1,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_b')
        m.make()
        self.assertFalse(hasattr(self, 'l1_a'))
        self.assertTrue(hasattr(self, 'l1_b'))
        self.assertEqual(self.l1_b, self.cli_1['l1_a'])
        post_dir = dir(self)
        extra = set(post_dir) - set(pre_dir)
        self.assertEqual(extra, {'l1_b'})

        m.make()

        post_post_dir = dir(self)
        self.assertEqual(post_post_dir, post_dir)

    def test_wrong_structure(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = self.cli_1
        m.outputs[FakeParser_2] = self.cli_2
        m.outputs[FakeParser_3] = self.cli_3
        m.outputs[FakeParser_4] = self.cli_4
        with self.assertRaises(AssertionError):
            m.add_leaf(cmd=FakeParser_1,
                       device=self.dev1,
                       src='[l1_a]',
                       dest=5)

        m.make()

    def test_wrong_src_type(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = self.cli_1
        m.outputs[FakeParser_2] = self.cli_2
        m.outputs[FakeParser_3] = self.cli_3
        m.outputs[FakeParser_4] = self.cli_4
        with self.assertRaises(AssertionError):
            m.add_leaf(cmd=FakeParser_1,
                       device=self.dev1,
                       src=5,
                       dest='l1_a')

        m.make()

    def test_wrong_src(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.add_leaf(cmd=FakeParser_1,
                   device=self.dev1,
                   src='[I_dont_exists]',
                   dest='l1_a')

        # No exception
        m.make()
        self.assertFalse(hasattr(self, 'l1_a'))

    def test_two_leaf(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a')

        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_b]',
                   dest='l1_b')

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertTrue(hasattr(self, 'l1_b'))
        self.assertEqual(self.l1_a, self.cli_2['l1_a'])
        self.assertEqual(self.l1_b, self.cli_2['l1_b'])

    def test_two_src_change(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_b')

        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_b]',
                   dest='l1_a')

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertTrue(hasattr(self, 'l1_b'))
        self.assertEqual(self.l1_b, self.cli_2['l1_a'])
        self.assertEqual(self.l1_a, self.cli_2['l1_b'])

    def test_two_src_change_schema(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_b')

        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_b]',
                   dest='l1_a')

        self.schema = {'l1_a': str,
                    'l1_b': str}
        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertTrue(hasattr(self, 'l1_b'))
        self.assertEqual(self.l1_b, self.cli_2['l1_a'])
        self.assertEqual(self.l1_a, self.cli_2['l1_b'])

    def test_two_src_change_schema_wrong(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_b')

        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_b]',
                   dest='l1_a')

        self.schema = {'l1_a': str,
                    'l1_b': int}
        with self.assertRaises(Exception):
            m.make(final_call=True)
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertTrue(hasattr(self, 'l1_b'))
        self.assertEqual(self.l1_b, self.cli_2['l1_a'])
        self.assertEqual(self.l1_a, self.cli_2['l1_b'])

    def test_two_src_more_structure(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a[level2]')

        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_b]',
                   dest='l1_b[level2][level3]')

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertTrue(hasattr(self, 'l1_b'))
        self.assertEqual(self.l1_a['level2'], self.cli_2['l1_a'])
        self.assertEqual(self.l1_b['level2']['level3'], self.cli_2['l1_b'])

    def test_merge_two(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a[level2][level3][l1_a]')

        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_b]',
                   dest='l1_a[level2][level3][l1_b]')

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(self.l1_a['level2']['level3']['l1_a'],
                         self.cli_2['l1_a'])
        self.assertEqual(self.l1_a['level2']['level3']['l1_b'],
                         self.cli_2['l1_b'])

    def test_merge_two_already_exists(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a[level2]')

        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_b]',
                   dest='l1_a[level2][level3]')

        with self.assertRaises(Exception):
            m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertFalse(hasattr(self, 'l1_b'))

    # Multiple Dict
    def test_merge_two_dict(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a[level2][level3]')

        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[l1_b]',
                   dest='l1_a[level2][level3]')

        m.make()
        # Now should've merged them into 1 dict
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertTrue(_dict_compare(self.cli_3['l1_a'],
                                      self.l1_a['level2']['level3']))
        self.assertTrue(_dict_compare(self.cli_3['l1_b'],
                                      self.l1_a['level2']['level3']))

    # Attribute of object
    def test_attr(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        self.at = 'level2'
        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a[{self.at}][level3]')
        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertTrue(_dict_compare(self.cli_3['l1_a'],
                                      self.l1_a['level2']['level3']))

    def test_attr_dont_exists(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = self.cli_1
        m.outputs[FakeParser_2] = self.cli_2
        m.outputs[FakeParser_3] = self.cli_3
        m.outputs[FakeParser_4] = self.cli_4
        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a[{self.at}][level3]')

        with self.assertRaises(Exception):
            m.make()
        self.assertFalse(hasattr(self, 'l1_a'))

    def test_two_attr(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        self.at = 'level2'
        self.att = 'level3'
        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a[{self.at}][{self.att}]')
        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertTrue(_dict_compare(self.cli_3['l1_a'],
                                      self.l1_a['level2']['level3']))

    def test_src(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        self.src = 'l1_a'
        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[{self.src}]',
                   dest='l1_a[level2][level3]')
        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertTrue(_dict_compare(self.cli_3['l1_a'],
                                      self.l1_a['level2']['level3']))

    def test_two_src(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        self.src = 'l1_a'
        self.srcc = 'l2_a'
        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[{self.src}][{self.srcc}]',
                   dest='l1_a[level2][level3]')
        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(self.cli_3['l1_a']['l2_a'],
                         self.l1_a['level2']['level3'])

    def test_src_attr(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        self.src = 'l1_a'
        self.srcc = 'l2_a'
        self.at = 'level2'
        self.att = 'level3'
        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[{self.src}][{self.srcc}]',
                   dest='l1_a[{self.at}][{self.att}]')
        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(self.cli_3['l1_a']['l2_a'],
                         self.l1_a['level2']['level3'])

    def test_src_attr_c4(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        self.src = 'l1_a'
        self.srcc = 'l2_a'
        self.at = 'level2'
        self.att = 'level3'
        m.add_leaf(cmd=FakeParser_4,
                   device=self.dev1,
                   src='[l1_a][{self.srcc}]',
                   dest='l1_a[{self.at}][{self.att}]')
        self.schema = {'l1_a':
                        {'level2':
                          {'level3':str,
                           Optional('not_there'): str},
                        },
                      }
        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(self.cli_4['l1_a']['l2_a'],
                         self.l1_a['level2']['level3'])

    def test_attr_other_object(self):
        class test(object):
            pass
        t = test()
        t.value = 'l1_a'
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = self.cli_1
        m.outputs[FakeParser_2] = self.cli_2
        m.outputs[FakeParser_3] = self.cli_3
        m.outputs[FakeParser_4] = self.cli_4
        self.srcc = 'l2_a'
        self.at = 'level2'
        self.att = 'level3'
        m.add_leaf(cmd=FakeParser_4,
                   device=self.dev1,
                   src='[{t.value}][{self.srcc}]',
                   dest='l1_a[{self.at}][{self.att}]')

        with self.assertRaises(Exception):
            m.make()

    # Regex test now
    #src='[(?P<first>.*)]',
    def test_src_reg(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}

        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='(?P<first>.*)',
                   dest='l1_a[(?P<first>.*)][level3]')

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(self.cli_3['l1_a'],
                         self.l1_a['l1_a']['level3'])

    def test_src_reg_wrong_pattern(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}

        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='(?P<first>bbb.*)',
                   dest='l1_a[(?P<first>bbb.*)][level3]')

        m.make()
        self.assertFalse(hasattr(self, 'l1_a'))

    def test_src_reg_where_half_dont_match(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}

        # Stuff of l2_ab shouldnt be in there
        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='(?P<first>.*)[l2_a]',
                   dest='l1_a[(?P<first>.*)][level3]')

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(self.cli_3['l1_a']['l2_a'],
                         self.l1_a['l1_a']['level3'])

    def test_src_reg_where_half_dont_match_reg(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}

        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='(?P<first>.*)[(?P<second>^.*a$)]',
                   dest='l1_a[(?P<first>.*)][level3]')

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(self.cli_3['l1_a']['l2_a'],
                         self.l1_a['l1_a']['level3'])

    def test_src_reg_swap_order(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}

        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='(?P<first>.*)[(?P<second>^.*$)]',
                   dest='l1_a[(?P<second>^.*$)][(?P<first>.*)][level3]')

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(set(self.l1_a.keys()), set(['l2_bb', 'l2_c', 'l2_ab',
                                                    'l2_a']))
        # Verify the key with correct output now
        self.assertEqual(self.l1_a['l2_a']['l1_a']['level3'], 'aa')
        self.assertEqual(self.l1_a['l2_ab']['l1_a']['level3'], 'ab')
        self.assertEqual(self.l1_a['l2_bb']['l1_b']['level3'], 'ba')
        self.assertEqual(self.l1_a['l2_c']['l1_b']['level3'], 'bc')

    def cal(self, item):
        if item == 'l2_ab':
            return 'l3_bb'
        return item

    def test_callables_1(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.outputs[FakeParser_5] = {'':self.cli_5}

        m.add_leaf(cmd=FakeParser_5,
                   device=self.dev1,
                   src='[l1_a][(?P<end>{cal})]',
                   dest='l1_c[(?P<end>{cal})]',
                   callables={'cal':self.cal})

        m.make()
        self.assertTrue(hasattr(self, 'l1_c'))
        self.assertEqual(self.l1_c, {'l2_a': 'aa', 'l3_bb': 'ab'})

    def cal2(self, item):
        if re.match('.*a$', item):
            return item
        else:
            return None

    def cal3(self, item):
        return item

    def cal4(self, item):
        return None

    def test_callables_2(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.outputs[FakeParser_5] = {'':self.cli_5}

        m.add_leaf(cmd=FakeParser_5,
                   device=self.dev1,
                   src='[l1_a][(?P<end>{cal2})]',
                   dest='l1_a[(?P<end>{cal2})]',
                   callables={'cal2':self.cal2})

        m.add_leaf(cmd=FakeParser_5,
                   device=self.dev1,
                   src='[l1_a][(?P<end>{cal3})]',
                   dest='l1_b[(?P<end>{cal3})]',
                   callables={'cal3':self.cal3})

        m.add_leaf(cmd=FakeParser_5,
                   device=self.dev1,
                   src='[l1_a][(?P<end>{cal4})]',
                   dest='l1_c[(?P<end>{cal4})]',
                   callables={'cal4':self.cal4})

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertTrue(hasattr(self, 'l1_b'))
        self.assertFalse(hasattr(self, 'l1_c'))
        self.assertEqual(self.l1_a, {'l2_a': 'aa'})
        self.assertEqual(self.l1_b, {'l2_a': 'aa', 'l2_ab': 'ab'})

    def test_callables_3(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.outputs[FakeParser_5] = {'':self.cli_5}

        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='(?P<first>{cal3})[(?P<second>^{cal3}$)]',
                   dest='l1_a[(?P<second>{cal3})][(?P<first>{cal3})][level3]',
                   callables={'cal3':self.cal3})

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(set(self.l1_a.keys()), set(['l2_bb', 'l2_c', 'l2_ab',
                                                    'l2_a']))
        # Verify the key with correct output now
        self.assertEqual(self.l1_a['l2_a']['l1_a']['level3'], 'aa')
        self.assertEqual(self.l1_a['l2_ab']['l1_a']['level3'], 'ab')
        self.assertEqual(self.l1_a['l2_bb']['l1_b']['level3'], 'ba')
        self.assertEqual(self.l1_a['l2_c']['l1_b']['level3'], 'bc')

    def test_callables_4(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = self.cli_1
        m.outputs[FakeParser_2] = self.cli_2
        m.outputs[FakeParser_3] = self.cli_3
        m.outputs[FakeParser_4] = self.cli_4
        m.outputs[FakeParser_5] = self.cli_5

        m.add_leaf(cmd=FakeParser_5,
                   device=self.dev1,
                   src='(?P<first>{cal3})[(?P<second>^{cal3}$)]',
                   dest='l1_a[(?P<second>{cal3})][(?P<first>{cal3})][level3]',
                   callables={'cal4':self.cal3})

        with self.assertRaises(Exception):
            m.make()

        self.assertFalse(hasattr(self, 'l1_a'))

    def test_callables_5(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = self.cli_1
        m.outputs[FakeParser_2] = self.cli_2
        m.outputs[FakeParser_3] = self.cli_3
        m.outputs[FakeParser_4] = self.cli_4
        m.outputs[FakeParser_5] = self.cli_5

        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='l1_a[l2_a][(?P<second>{cal4})]',
                   dest='l1_a[(?P<second>{cal3})][(?P<first>{cal3})][level3]',
                   callables={'cal4':self.cal3})

        with self.assertRaises(Exception):
            m.make()

        self.assertFalse(hasattr(self, 'l1_a'))

    def test_callables_6(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = self.cli_1
        m.outputs[FakeParser_2] = self.cli_2
        m.outputs[FakeParser_3] = self.cli_3
        m.outputs[FakeParser_4] = self.cli_4
        m.outputs[FakeParser_5] = self.cli_5

        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='l1_a[l2_a][(?P<second>{cal4})]',
                   dest='l1_a[l2_a][(?P<first>{cal3})][level3]',
                   callables={'cal4':self.cal3})

        with self.assertRaises(Exception):
            m.make()

        self.assertFalse(hasattr(self, 'l1_a'))

    def test_callables_7(self):
        self.callables['cal'] = self.dev1
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.outputs[FakeParser_5] = {'':self.cli_5}

        m.add_leaf(cmd=FakeParser_5,
                   device=self.dev1,
                   src='[l1_a][(?P<end>{cal})]',
                   dest='l1_c[(?P<end>{cal})]',
                   callables={'cal':self.cal})

        m.make()
        self.assertTrue(hasattr(self, 'l1_c'))
        self.assertEqual(self.l1_c, {'l2_a': 'aa', 'l3_bb': 'ab'})

    def test_regex_value(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.outputs[FakeParser_5] = {'':self.cli_5}

        m.add_leaf(cmd=FakeParser_5,
                   device=self.dev1,
                   src='[l1_a][(?P<end>.*a$)]',
                   dest='l1_a[(?P<end>^.*a$)]')

        m.add_leaf(cmd=FakeParser_5,
                   device=self.dev1,
                   src='[l1_a][(?P<end>.*)]',
                   dest='l1_b[(?P<end>.*)]')

        m.add_leaf(cmd=FakeParser_5,
                   device=self.dev1,
                   src='[l1_a][(?P<end>zz$)]',
                   dest='l1_c[(?P<end>zz$)]')

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertTrue(hasattr(self, 'l1_b'))
        self.assertFalse(hasattr(self, 'l1_c'))
        self.assertEqual(self.l1_a, {'l2_a': 'aa'})
        self.assertEqual(self.l1_b, {'l2_a': 'aa', 'l2_ab': 'ab'})

    def test_regex_value_range_1(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.outputs[FakeParser_5] = {'':self.cli_5}

        m.add_leaf(cmd=FakeParser_5,
                   device=self.dev1,
                   src='[l1_a][(?P<end>^[a-z]$)]',
                   dest='l1_a[(?P<end>^[a-z]$)]')

        m.make()
        self.assertFalse(hasattr(self, 'l1_a'))

    def test_regex_value_range_2(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.outputs[FakeParser_5] = {'':self.cli_5}

        m.add_leaf(cmd=FakeParser_5,
                   device=self.dev1,
                   src='[l1_a][(?P<end>^[a-z0-9_]+$)]',
                   dest='l1_a[(?P<end>^[a-z0-9_]+$)]')

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))

    def test_regex_doesnt_value_exists(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = self.cli_1
        m.outputs[FakeParser_2] = self.cli_2
        m.outputs[FakeParser_3] = self.cli_3
        m.outputs[FakeParser_4] = self.cli_4
        m.outputs[FakeParser_5] = self.cli_5

        m.add_leaf(cmd=FakeParser_5,
                   device=self.dev1,
                   src='[l1_a][(?P<end>^[a-z0-9_]+$)]',
                   dest='l1_a[(?P<fake>.*)][(?P<end>^[a-z0-9_]+$)]')


        with self.assertRaises(Exception):
            m.make()
        self.assertFalse(hasattr(self, 'l1_a'))

    # Mix and match of unittest

    def test_mix_1(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}

        self.level = 'level3'
        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='(?P<first>.*)[(?P<second>^.*$)]',
                   dest='l1_a[(?P<second>^.*$)][(?P<first>.*)][{self.level}]')

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(set(self.l1_a.keys()), set(['l2_bb', 'l2_c', 'l2_ab',
                                                    'l2_a']))
        # Verify the key with correct output now
        self.assertEqual(self.l1_a['l2_a']['l1_a']['level3'], 'aa')
        self.assertEqual(self.l1_a['l2_ab']['l1_a']['level3'], 'ab')
        self.assertEqual(self.l1_a['l2_bb']['l1_b']['level3'], 'ba')
        self.assertEqual(self.l1_a['l2_c']['l1_b']['level3'], 'bc')

    def test_mix_2(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}

        self.level = 'level3'
        self.l2 = 'l2_a'
        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='(?P<first>.*)[{self.l2}]',
                   dest='l1_a[{self.l2}][(?P<first>.*)][{self.level}]')

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(set(self.l1_a.keys()), set(['l2_a']))
        # Verify the key with correct output now
        self.assertEqual(self.l1_a['l2_a']['l1_a']['level3'], 'aa')

    def test_mix_3(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}

        self.level = 'level3'
        self.l2 = 'l2_a'
        self.l1 = 'l1_a'
        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[{self.l1}][{self.l2}]',
                   dest='l1_a[{self.l2}][{self.l1}][{self.level}]')

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertTrue(set(self.l1_a.keys()), set(['l2_a']))
        # Verify the key with correct output now
        self.assertEqual(self.l1_a['l2_a']['l1_a']['level3'], 'aa')

    def test_too_much_reg(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}

        self.level = 'level3'
        self.l2 = 'l2_a'
        self.l1 = 'l1_a'
        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[l1_a][l2_a][l3_a]',
                   dest='l1_a[l2_a][level3]')

        m.make()
        self.assertFalse(hasattr(self, 'l1_a'))

    def test_too_much_attr(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}

        self.level = 'level3'
        self.l2 = 'l2_a'
        self.l1 = 'l1_a'
        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[[l1_a]][[l2_a][{self.l2}]',
                   dest='l1_a[l2_a][level3]')

        m.make()
        self.assertFalse(hasattr(self, 'l1_a'))

    def test_wrong_regex_syntax(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = self.cli_1
        m.outputs[FakeParser_2] = self.cli_2
        m.outputs[FakeParser_3] = self.cli_3
        m.outputs[FakeParser_4] = self.cli_4

        self.level = 'level3'
        self.l2 = 'l2_a'
        self.l1 = 'l1_a'
        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[l1_a][l2_a][(?P(value).*)]',
                   dest='l1_a[l2_a][level3]')

        with self.assertRaises(Exception):
            m.make()

    def test_action(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = self.cli_1
        m.outputs[FakeParser_2] = self.cli_2
        m.outputs[FakeParser_3] = self.cli_3
        m.outputs[FakeParser_4] = self.cli_4

        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a',
                   action=lambda x: list(x.keys()))

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(set(self.l1_a), set(['l2_ab', 'l2_a']))

    def test_action_value(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a[value]',
                   action=lambda x: list(x.keys()))

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(set(self.l1_a['value']), set(['l2_ab', 'l2_a']))

    def test_action_attr(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        self.l3 = 'value'
        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a[{self.l3}]',
                   action=lambda x: list(x.keys()))

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(set(self.l1_a[self.l3]), set(['l2_ab', 'l2_a']))

    def test_action_reg(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        self.l3 = 'value'
        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a[{self.l3}]',
                   action=lambda x: list(x.keys()))

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(set(self.l1_a[self.l3]), set(['l2_ab', 'l2_a']))

    def test_action_value_wrong(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = self.cli_1
        m.outputs[FakeParser_2] = self.cli_2
        m.outputs[FakeParser_3] = self.cli_3
        m.outputs[FakeParser_4] = self.cli_4
        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a[value]',
                   action=lambda x: list(x.keys()))

        with self.assertRaises(Exception):
            m.make()

    def test_action_attr_wrong(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = self.cli_1
        m.outputs[FakeParser_2] = self.cli_2
        m.outputs[FakeParser_3] = self.cli_3
        m.outputs[FakeParser_4] = self.cli_4
        self.l3 = 'value'
        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a[{self.l3}]',
                   action=lambda x: list(x.keys()))

        with self.assertRaises(Exception):
            m.make()

    def test_action_reg_wrong(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = self.cli_1
        m.outputs[FakeParser_2] = self.cli_2
        m.outputs[FakeParser_3] = self.cli_3
        m.outputs[FakeParser_4] = self.cli_4
        self.l3 = 'value'
        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a[{self.l3}]',
                   action=lambda x: list(x.keys()))

        with self.assertRaises(Exception):
            m.make()

    def test_action(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}

        def keys(item):
            return item.keys()

        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a',
                   action=keys)

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(set(self.l1_a), set(['l2_ab', 'l2_a']))

    def test_each_dictionary_level_is_of_type_LeafDict(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a[level2][level3][l1_a]')

        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_b]',
                   dest='l1_a[level2][level3][l1_b]')

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertTrue(isinstance(self.l1_a['level2'], CmdDict))
        self.assertTrue(isinstance(self.l1_a['level2']['level3'], CmdDict))

    def test_get_cmd_for_corresponding_leaf_with_key_defined(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a[level2][level3][l1_a]')

        m.add_leaf(cmd=FakeParser_2,
                   device=self.dev1,
                   src='[l1_b]',
                   dest='l1_a[level2][level3][l1_b]')

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(self.l1_a['level2']['level3'].leaf_dict['l1_a'],
                         FakeParser_2)
        self.assertEqual(self.l1_a['level2']['level3'].leaf_dict['l1_b'],
                         FakeParser_2)

        with self.assertRaises(KeyError):
            self.l1_a['level2'].leaf_dict['level3']

    def test_get_cmd_for_corresponding_leaf_without_key_defined(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}
        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a[level2][level3]')

        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[l1_b]',
                   dest='l1_a[level2][level3]')

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(self.l1_a['level2']['level3'].leaf_dict['l2_ab'],
                         FakeParser_3)
        self.assertEqual(self.l1_a['level2']['level3'].leaf_dict['l2_a'],
                         FakeParser_3)
        self.assertEqual(self.l1_a['level2']['level3'].leaf_dict['l2_bb'],
                         FakeParser_3)
        self.assertEqual(self.l1_a['level2']['level3'].leaf_dict['l2_c'],
                         FakeParser_3)

        with self.assertRaises(KeyError):
            self.l1_a['level2']['level3'].leaf_dict['l2_cb']

    def test_get_cmd_for_corresponding_leaf_key_with_action(self):
        m = Maker(parent=self)
        m.outputs[FakeParser_1] = {'':self.cli_1}
        m.outputs[FakeParser_2] = {'':self.cli_2}
        m.outputs[FakeParser_3] = {'':self.cli_3}
        m.outputs[FakeParser_4] = {'':self.cli_4}

        def keys(item):
            return item.keys()

        m.add_leaf(cmd=FakeParser_3,
                   device=self.dev1,
                   src='[l1_a]',
                   dest='l1_a[level2][level3][l1_a]',
                   action=keys)

        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(self.l1_a['level2']['level3'].leaf_dict['l1_a'],
            FakeParser_3)


# TO change when the feature class is created
class test_maker_user_perspective(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.testbed = Testbed()
        cls.dev1 = Device(name='pe1', testbed=cls.testbed, os='nxos')

    # To remove
    class Feature(Base):
        schema = {'l1_a':
                  {'level2':
                   {'level3':
                    {'l1_a':str,
                     'l1_b':str,
                    },
                   },
                  },
                  'two':
                  {'level2':
                   {'level3':
                    {'l2_a':str,
                     'l2_ab':str,
                    },
                   },
                  }
                     
                 }

        cli_1 = {'l1_a':'a'}
        cli_2 = {'l1_a':'a',
                 'l1_b':'b'}
        cli_3 = {'l1_a':{'l2_a':'aa', 'l2_ab':'ab'},
                 'l1_b':{'l2_bb':'ba', 'l2_c':'bc'}}
        cli_4 = {'l1_a':{'l2_a':'aa', 'l2_ab':'ab'},
                 'l1_b':{'l2_bb':'ba', 'l2_c':'bc',
                          'l2_d':{'l3_d':'ff'}}}
        cli_6 = {'l1_a':{5:'aa', 'l2_ab':'ab'}}

        def learn(self):
            self.maker.outputs[FakeParser_1] = {'':self.cli_1}
            self.maker.outputs[FakeParser_2] = {'':self.cli_2}
            self.maker.outputs[FakeParser_3] = {'':self.cli_3}
            self.maker.outputs[FakeParser_4] = {'':self.cli_4}
            self.maker.outputs[FakeParser_6] = {'':self.cli_6}

            self.at = 'level2'

            self.add_leaf(cmd=FakeParser_2,
                          src='[l1_a]',
                          dest='l1_a[level2][level3][l1_a]')

            self.add_leaf(cmd=FakeParser_2,
                          src='[l1_b]',
                          dest='l1_a[level2][level3][l1_b]')

            self.add_leaf(cmd=FakeParser_3,
                          src='[l1_a]',
                          dest='two[{self.at}][level3]')

            self.add_leaf(cmd=FakeParser_3,
                          src='(?P<first>.*)[(?P<second>.*)]',
                          dest='three[(?P<second>.*)][(?P<first>.*)][{self.at}]')

            self.add_leaf(cmd=FakeParser_6,
                          src='[l1_a]',
                          dest='l1_c')

            self.make(final_call=True)

    def test_sample(self):

        f = self.Feature(device=self.dev1)
        f.learn()

        self.assertTrue(hasattr(f, 'l1_a'))

        self.assertEqual(f.l1_a['level2']['level3']['l1_a'],
                         f.cli_2['l1_a'])

        self.assertEqual(f.l1_a['level2']['level3']['l1_b'],
                         f.cli_2['l1_b'])
        self.assertTrue(_dict_compare(f.cli_3['l1_a'],
                                      f.two['level2']['level3']))

        self.assertEqual(f.three['l2_a']['l1_a']['level2'], 'aa')
        self.assertEqual(f.three['l2_ab']['l1_a']['level2'], 'ab')
        self.assertEqual(f.three['l2_bb']['l1_b']['level2'], 'ba')
        self.assertEqual(f.three['l2_c']['l1_b']['level2'], 'bc')

    def test_sample_wrong_schema(self):

        f = self.Feature(device=self.dev1)
        f.schema['l1_a']['level2']['level3']['l1_a'] = int
        with self.assertRaises(Exception):
            f.learn()

    def test_sample_attributes_1(self):

        f = self.Feature(device=self.dev1, attributes=['l1_a'])
        f.learn()

        self.assertTrue(hasattr(f, 'l1_a'))
        self.assertEqual(f.l1_a['level2']['level3']['l1_a'],
                         f.cli_2['l1_a'])
        self.assertEqual(f.l1_a['level2']['level3']['l1_b'],
                         f.cli_2['l1_b'])

        self.assertFalse(hasattr(f, 'two'))
        self.assertFalse(hasattr(f, 'three'))

    def test_sample_attributes_2(self):

        # multiple can be given
        f = self.Feature(device=self.dev1, attributes=['l1_a','two'])
        f.learn()

        self.assertTrue(hasattr(f, 'l1_a'))
        self.assertEqual(f.l1_a['level2']['level3']['l1_a'],
                         f.cli_2['l1_a'])
        self.assertEqual(f.l1_a['level2']['level3']['l1_b'],
                         f.cli_2['l1_b'])

        self.assertTrue(hasattr(f, 'two'))
        self.assertTrue(_dict_compare(f.cli_3['l1_a'],
                                      f.two['level2']['level3']))

        self.assertFalse(hasattr(f, 'three'))

    def test_sample_attributes_3(self):

        # Specific src can be given
        f = self.Feature(device=self.dev1,
                         attributes=['l1_a[level2][level3][l1_a]',
                                     'two'])
        f.learn()

        self.assertTrue(hasattr(f, 'l1_a'))
        self.assertTrue('l1_a' in f.l1_a['level2']['level3'])
        self.assertFalse('l1_b' in f.l1_a['level2']['level3'])

        self.assertEqual(f.l1_a['level2']['level3']['l1_a'],
                         f.cli_2['l1_a'])

        self.assertTrue(hasattr(f, 'two'))
        self.assertTrue(_dict_compare(f.cli_3['l1_a'],
                                      f.two['level2']['level3']))

        self.assertFalse(hasattr(f, 'three'))

    def test_sample_attributes_4(self):

        # Too long
        f = self.Feature(device=self.dev1,
                         attributes=['two[level2][level3][l2_ab]'])

        f.learn()
        # No exception but nothing should be learn
        self.assertFalse(hasattr(f, 'l1_a'))
        self.assertFalse(hasattr(f, 'two'))

    def test_sample_attributes_5(self):

        # Regex
        f = self.Feature(device=self.dev1, attributes=['l1_a[(.*)][level3][(.*)]',
                                                 'two'])
        f.learn()

        self.assertTrue(hasattr(f, 'l1_a'))
        self.assertTrue('l1_a' in f.l1_a['level2']['level3'])
        self.assertTrue('l1_b' in f.l1_a['level2']['level3'])

        self.assertEqual(f.l1_a['level2']['level3']['l1_a'],
                         f.cli_2['l1_a'])
        self.assertEqual(f.l1_a['level2']['level3']['l1_b'],
                         f.cli_2['l1_b'])

        self.assertTrue(hasattr(f, 'two'))
        self.assertTrue(_dict_compare(f.cli_3['l1_a'],
                                      f.two['level2']['level3']))

        self.assertFalse(hasattr(f, 'three'))

    def test_sample_attributes_6(self):

        # Regex
        f = self.Feature(device=self.dev1,
                         attributes=['l1_a[(.*)][level3][(.*_b.*)]',
                                     'two'])
        f.learn()

        self.assertTrue(hasattr(f, 'l1_a'))
        self.assertFalse('l1_a' in f.l1_a['level2']['level3'])
        self.assertTrue('l1_b' in f.l1_a['level2']['level3'])

        self.assertEqual(f.l1_a['level2']['level3']['l1_b'],
                         f.cli_2['l1_b'])

        self.assertTrue(hasattr(f, 'two'))
        self.assertTrue(_dict_compare(f.cli_3['l1_a'],
                                      f.two['level2']['level3']))

        self.assertFalse(hasattr(f, 'three'))

    def test_sample_attributes_7(self):

        # Regex
        f = self.Feature(device=self.dev1,
                         attributes=['l1_a[(.*)][level3][(.*_b.*)]', '({[[})'])
        with self.assertRaises(Exception):
            f.learn()

    def test_sample_attributes_8(self):

        # Regex with three which contains also a regex
        f = self.Feature(device=self.dev1,
                         attributes=['three[(.*)][(.*)][level2]'])

        f.learn()

        self.assertFalse(hasattr(f, 'l1_a'))
        self.assertFalse(hasattr(f, 'two'))
        self.assertEqual(f.three['l2_a']['l1_a']['level2'], 'aa')
        self.assertEqual(f.three['l2_ab']['l1_a']['level2'], 'ab')
        self.assertEqual(f.three['l2_bb']['l1_b']['level2'], 'ba')
        self.assertEqual(f.three['l2_c']['l1_b']['level2'], 'bc')

    def test_sample_attributes_9(self):

        # Regex with three which contains also a regex
        # Though not .*, hence wont work
        f = self.Feature(device=self.dev1,
                         attributes=['three[(.*else)][(.*)][level2]'])

        f.learn()

        self.assertFalse(hasattr(f, 'l1_a'))
        self.assertFalse(hasattr(f, 'two'))
        self.assertFalse(hasattr(f, 'three'))

    def test_sample_attributes_10(self):

        # Regex
        f = self.Feature(device=self.dev1,
                         attributes=['three[l2_a]'])
        f.learn()

        self.assertFalse(hasattr(f, 'l1_a'))
        self.assertFalse(hasattr(f, 'two'))
        self.assertEqual(f.three['l2_a']['l1_a']['level2'], 'aa')
        self.assertNotIn('l2_ab', f.three)
        self.assertNotIn('l2_bb', f.three)
        self.assertNotIn('l2_c', f.three)

    def test_sample_attributes_11(self):

        # Regex
        # With attribute which does not exists
        f = self.Feature(device=self.dev1,
                         attributes=['three[nope]'])
        f.learn()

        self.assertFalse(hasattr(f, 'l1_a'))
        self.assertFalse(hasattr(f, 'two'))
        self.assertFalse(hasattr(f, 'three'))

    def test_sample_attributes_11(self):

        # Regex
        # With attribute which does not exists
        f = self.Feature(device=self.dev1,
                         attributes=['three[.*]'])

        f.add_leaf(cmd='cli_3',
                   src='(?P<first>.*)[(?P<second>^.*$)]',
                   dest='three[(?P<second>.*)][(?P<first>.*)][{self.at}]')

        with self.assertRaises(Exception):
            f.make()

        self.assertFalse(hasattr(f, 'l1_a'))
        self.assertFalse(hasattr(f, 'two'))
        self.assertFalse(hasattr(f, 'three'))

    def test_sample_attributes_12(self):

        # Regex
        # With attribute which does not exists
        f = self.Feature(device=self.dev1,
                         attributes=['three[.*]'])

        with self.assertRaises(TypeError):
            f.add_leaf('cli_3',
                       '(?P<first>.*)[(?P<second>^.*$)]',
                       'three[(?P<second>.*)][(?P<first>.*)][{self.at}]')


        self.assertFalse(hasattr(f, 'l1_a'))
        self.assertFalse(hasattr(f, 'two'))
        self.assertFalse(hasattr(f, 'three'))

    def test_learn_specific_commands(self):

        f = self.Feature(device=self.dev1,
                         commands=[FakeParser_2, FakeParser_6])

        f.learn()

        self.assertTrue(hasattr(f, 'l1_a'))
        self.assertTrue(hasattr(f, 'l1_c'))
        with self.assertRaises(AssertionError):
          self.assertTrue(hasattr(f, 'two'))


    def test_learn_specific_commands_with_wrong_command_provided(self):

        f = self.Feature(device=self.dev1,
                         commands=['cli_2','cli_6','banana'])

        with self.assertRaises(ValueError):
          f.learn()


class test_parsers(unittest.TestCase):
    context_manager = {}
    callables = {}
    cli_2 = {'l1_a':'a',
         'l1_b':'b'}
    @classmethod
    def setUpClass(cls):
        cls.testbed = Testbed()
        cls.dev1 = Device(name='pe1', testbed=cls.testbed, os='nxos')

    class myParser1(object):
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

        def parse(self, value):
            return {'bla':value}

    class myParser2(object):
        def __init__(self, **kwargs):
            for k in kwargs:
                setattr(self, k)

        def parse(self):
            return {'bla':5}

    class myParser3(object):
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

        def parse(self, vrf):
            return {'bla':vrf}

    class myParser4(object):
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def parse(self, neighbor, vrf):
            return {'bla':neighbor, 'bla2': vrf}

    def test_kwargs(self):
        pre_dir = dir(self)
        m = Maker(parent=self)
        value = 3
        m.add_leaf(cmd=self.myParser1,
                   device=self.dev1,
                   src='[bla]',
                   dest='l1_a',
                   value=value)
        # Make sure it finds the right output
        m.make()
        self.assertTrue(hasattr(self, 'l1_a'))
        self.assertEqual(self.l1_a, value)

    def test_missing_kwargs(self):
        pre_dir = dir(self)
        m = Maker(parent=self)
        value = 3
        m.add_leaf(cmd=self.myParser1,
                   device=self.dev1,
                   src='[bla]',
                   dest='l1_a')
        # Make sure it finds the right output
        with self.assertRaises(TypeError):
            m.make()

    def test_duplicate_leafs_caching_mechanism(self):
        m = Maker(parent=self)

        m.outputs['cli_2'] = {'':self.cli_2}

        m.add_leaf(cmd=self.myParser3,
                   device=self.dev1,
                   src='[bla]',
                   dest='l1_a',
                   vrf='blue')

        m.add_leaf(cmd=self.myParser3,
                   device=self.dev1,
                   src='[bla]',
                   dest='l1_b',
                   vrf='orange')

        m.add_leaf(cmd=self.myParser3,
                   device=self.dev1,
                   src='[bla]',
                   dest='l1_c',
                   vrf='blue')

        m.make()

        # learned contains the actual learned leafs
        learned_leafs = []
        for itm in m.learned.values():
          for new_itm in itm.values():
            learned_leafs.append(new_itm)

        try:
          self.assertCountEqual(learned_leafs, m.leafs)
        except AssertionError:
          # Count should not be equal if the caching mechanism is working fine.
          pass

        # Verifying that learned leafs are less than the passed ones
        with self.assertRaises(AssertionError):
          self.assertCountEqual(m.learned, m.leafs)

    def test_duplicate_leafs_with_same_kwargs(self):
        m = Maker(parent=self)

        m.outputs['cli_2'] = {'':self.cli_2}

        m.add_leaf(cmd=self.myParser3,
                   device=self.dev1,
                   src='[bla]',
                   dest='l1_a',
                   vrf='blue')

        m.add_leaf(cmd=self.myParser3,
                   device=self.dev1,
                   src='[bla]',
                   dest='l1_b',
                   vrf='orange')

        m.add_leaf(cmd=self.myParser3,
                   device=self.dev1,
                   src='[bla]',
                   dest='l1_c',
                   vrf='blue')

        m.make()

        # learned contains the actual learned leafs
        learned_leafs = []
        for itm in m.learned.values():
          for new_itm in itm.values():
            learned_leafs.append(new_itm)

        # Checking if the duplicated 'vrf=blue' leaf has been learnt or not. It
        # shouldn't be present in the m.learned list.
        self.assertTrue(m.leafs[2] not in m.learned)

    def test_duplicate_leafs_with_multiple_kwargs(self):
        m = Maker(parent=self)

        m.outputs['cli_2'] = {'':self.cli_2}

        m.add_leaf(cmd=self.myParser4,
                   device=self.dev1,
                   src='[bla]',
                   dest='l1_a',
                   neighbor='1.1.1.1',
                   vrf='blue')

        m.add_leaf(cmd=self.myParser4,
                   device=self.dev1,
                   src='[bla]',
                   dest='l1_b',
                   neighbor='1.1.1.1',
                   vrf='orange')

        m.add_leaf(cmd=self.myParser4,
                   device=self.dev1,
                   src='[bla]',
                   dest='l1_c',
                   neighbor='1.1.1.1',
                   vrf='blue')

        m.make()

        # learned contains the actual learned leafs
        learned_leafs = []
        for itm in m.learned.values():
          for new_itm in itm.values():
            learned_leafs.append(new_itm)

        # Checking if the duplicated 'vrf=blue' leaf has been learnt or not. It
        # shouldn't be present in the m.learned list.
        self.assertTrue(m.leafs[2] not in m.learned)

    def test_sorted_kwargs(self):
        m = Maker(parent=self)
        m.outputs['cli_2'] = {'':self.cli_2}

        m.add_leaf(cmd=self.myParser4,
                   device=self.dev1,
                   src='[bla]',
                   dest='l1_a',
                   neighbor='1.1.1.1',
                   vrf='blue')

        m.add_leaf(cmd=self.myParser4,
                   device=self.dev1,
                   src='[bla]',
                   dest='l1_b',
                   vrf='blue',
                   neighbor='1.1.1.1')

        m.make()

        # learned contains the actual learned leafs
        learned_leafs = []
        for itm in m.learned.values():
          for new_itm in itm.values():
            learned_leafs.append(new_itm)

        # Checking the sorted kwrags functionality. Above leafs have the same
        # kwargs but not in order, so we test how many times the cmd will be
        # added in the to_learn list of commands.
        self.assertTrue(m.leafs[1] not in m.learned)

if __name__ == '__main__':
    unittest.main()
