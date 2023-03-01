#!/usr/bin/env python
""" Unit tests for the util within metaparser package. """

import unittest

from genie.metaparser.util import keynames_exist, \
                            keynames_convert, \
                            reform_nestdict_from_keys, \
                            nestedkey_rename, \
                            dict_2_list_of_keys, \
                            get_value_from_nestdict, \
                            create_dict_from_nestedkeys, \
                            merge_dict

class TestMetaparserUtil(unittest.TestCase):
    def setUp(self):
        pass
    
    ########## keynames_exist
    def test_keynames_exist_dot_format(self):
        dic = {'country': 'canada', 
                    'province': {'city': 'ottawa', 'county': 'kanata'}}
        keynames = ['country', 'province.city']
        self.assertEqual(keynames_exist(dic, keynames), None)

    def test_keynames_exist_normal_format(self):
        dic = {'country': 'canada', 
                    'province': {'city': 'ottawa', 'county': 'kanata'}}
        keynames = [['country'], ['province', 'city']]
        self.assertEqual(keynames_exist(dic, keynames), None)

    def test_keynames_exist_normal_format_tuple(self):
        dic = {'country': 'canada', 
                    'province': {'city': 'ottawa', 'county': 'kanata'}}
        keynames = [('country'), ('province', 'city')]
        self.assertEqual(keynames_exist(dic, keynames), None)

    def test_keynames_noexist_dot_format(self):
        dic = {'country': 'canada', 
                    'province': {'city': 'ottawa', 'county': 'kanata'}}
        keynames = ['country', 'province.area']
        
        with self.assertRaises(KeyError):
            keynames_exist(dic, keynames)

    def test_keynames_noexist_normal_format(self):
        dic = {'country': 'canada', 
                    'province': {'city': 'ottawa', 'county': 'kanata'}}
        keynames = [['country'], ['province', 'area']]
        with self.assertRaises(KeyError):
            keynames_exist(dic, keynames)

    # dict_2_list_of_keys
    def test_dict_2_list_of_keys(self):
        dic = {'country': 'canada', 
                'province': {'city': 'ottawa', 'county': 'kanata'}}
        result = dict_2_list_of_keys(dic)
        self.assertTrue(['country'] in result)
        self.assertTrue(['province', 'city'] in result)
        self.assertTrue(['province', 'county'] in result)

    ########## keynames_convert
    def test_keynames_convert_tuple_format(self):
        dic = {'country': 'canada', 
                    'province': {'city': 'ottawa', 'county': 'kanata'}}
        names_mapping =  [('province.city','cities'), ('country','countries')]
        result = keynames_convert(dic, names_mapping)
        self.assertTrue('cities' in result['province'])
        self.assertTrue('countries' in result)

    def test_keynames_convert_list_format(self):
        dic = {'country': 'canada', 
                    'province': {'city': 'ottawa', 'county': 'kanata'}}
        names_mapping =  [['province.city','cities'], ['country','countries']]
        result = keynames_convert(dic, names_mapping)
        self.assertTrue('cities' in result['province'])
        self.assertTrue('countries' in result)

    # nestedkey_rename
    def test_nestedkey_rename(self):
        dic = {'country': 'canada', 
                    'province': {'city': 'ottawa', 'county': 'kanata'}}
        keys = ['province','city']
        new_key = 'cities'
        result = nestedkey_rename(dic, keys, new_key)
        self.assertTrue('cities' in result['province'])

    def test_nestedkey_rename_tuple(self):
        dic = {'country': 'canada', 
                    'province': {'city': 'ottawa', 'county': 'kanata'}}
        keys = ('province','city')
        new_key = 'cities'
        result = nestedkey_rename(dic, keys, new_key)
        self.assertTrue('cities' in result['province'])

    ########## reform_nestdict_from_keys
    def test_reform_nestdict_from_keys(self):
        dic = {'country': 'canada', 
                    'province': {'city': 'ottawa', 'county': 'kanata'}}
        # keys = ['province.city', 'province.county']
        keys = [['province','city'], ['province','county']]
        new_dict = reform_nestdict_from_keys(dic, keys)
        self.assertTrue('city' in new_dict['province'])
        self.assertTrue('county' in new_dict['province'])
        self.assertTrue('country' not in new_dict)

    def test_reform_nestdict_from_keys_dot_format(self):
        dic = {'country': 'canada', 
                    'province': {'city': 'ottawa', 'county': 'kanata'}}
        keys = ['province.city', 'province.county']
        new_dict = reform_nestdict_from_keys(dic, keys)
        self.assertTrue('city' in new_dict['province'])
        self.assertTrue('county' in new_dict['province'])
        self.assertTrue('country' not in new_dict)

    # get_value_from_nestdict
    def test_get_value_from_nestdict(self):
        dic = {'country': 'canada', 
                    'province': {'city': 'ottawa', 'county': 'kanata'}}
        keys = ['province','city']
        
        self.assertEqual(get_value_from_nestdict(dic, keys), 'ottawa')

    def test_get_value_from_nestdict_tuple_format(self):
        dic = {'country': 'canada', 
                    'province': {'city': 'ottawa', 'county': 'kanata'}}
        keys = ('province','city')
        
        self.assertEqual(get_value_from_nestdict(dic, keys), 'ottawa')
    
    # create_dict_from_nestedkeys
    def test_create_dict_from_nestedkeys(self):
        keys = ['province','city']
        value = 'ottawa'

        result = create_dict_from_nestedkeys(keys, value)
        self.assertEqual(result['province'].get('city'), 'ottawa')

    # merge_dict
    def test_merge_dict(self):
        dict1 = {'province': {'city': 'ottawa'}, 'country': 'canada'}
        dict2 = {'province': {'county': 'kanata'}, 'country': 'canada'}
        result  = merge_dict(dict1, dict2)
        self.assertTrue('city' in result['province'])
        self.assertTrue('county' in result['province'])

    def test_merge_dict_exception(self):
        dict1 = {'province': {'city': 'ottawa'}}
        dict2 = {'province': 'ontario'}
        with self.assertRaises(Exception):
            merge_dict(dict1, dict2)
        
