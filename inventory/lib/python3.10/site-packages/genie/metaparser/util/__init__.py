'''
metaparser utility class

Purpose of this class is helping user manipulating the parser output data 
structures (e.g.: nested dictionaries)

'''
from collections import OrderedDict

def keynames_exist(dic, key_list):
    """ Method to validate if all the keys provided from key_list existing in 
    given dict

    Args:
        dic (`dict`): the given dictionary
        key_list (`list`): list of keys (nestedkeys) need to be checked against 
                           dic.
    Example:
        >>> dic = {'d': 1, 'e': {'f': 2, 'ff': 3}}
        >>> keynames_exist(dic, ['d', 'e.f'])
        OR
        >>> keynames_exist(dic, [['d'], ['e','f']])
        OR
        >>> keynames_exist(dic, [('d',), ('e','f')])

    Returns:
        None - validation passed, all keys provided in key_list exist in dic 
        exception - validation failed, one or more keys not in given dic
    """
    keys_to_check = dict_2_list_of_keys(dic)
    for i in key_list:
        try:
            i = i.split('.')
        except: pass
        finally:
            if list(i) not in keys_to_check:
                raise KeyError('key {key} is not in dictionary'.format(key=i))

def dict_2_list_of_keys(dic, lst=None, loc=None):
    """ Method returns a list of flattened dictionary keys 
    (including all nested keys)

    Args:
        dic (`dict`): the dictionary used to generate keys

    Examples:
        >>> dic = {'k1': 'v1', 'k2': {'k21': 'v21', 'k22': 'v22'}}
        >>> dict_2_list_of_keys(dic)

    Returns: [['k1'], ['k2', 'k21'], ['k2', 'k22']]
    """
    if lst is None:
        lst = []
    if loc is None:
        loc = []
    for k in iter(dic):
        loc.append(k)
        lst.append(loc * 1)
        if isinstance(dic[k], dict):
            dict_2_list_of_keys(dic[k], lst, loc)
        loc.pop()
    return lst

def keynames_convert(dic, mapping):
    """ Method to to convert a list of nested key names

    Args:
        dic (`dict`): original dictionary needs to be converted
        mapping (`list of tuples`): list of tuples defines the key mapping 
            relationship. for example:
            [('k2.k21','k21_new'), ('k1','k1_new'), ('k2.k22','k22_new')]
            Also support list of list format:
            [['k2.k21','k21_new'], ['k1','k1_new'], ['k2.k22','k22_new']]

    Example:
        >>> dic = {'k1': 'v1', 'k2': {'k21': 'v21', 'k22': 'v22'}}
        >>> mapping = [('k2.k21','k21_new'), ('k1','k1_new'), 
        ...            ('k2.k22','k22_new')]
        >>> keynames_convert(dic, mapping)

    Returns: {'k1_new': 'v1', 'k2': {'k21_new': 'v21', 'k22_new': 'v22'}}
    """
    map_dict = OrderedDict(mapping)

    for key, value in map_dict.items():
            key = key.split('.')
            nestedkey_rename(dic, key, value)
    return dic

def nestedkey_rename(dic, keymap, new_key):
    """ Method to rename a single key name of a nested dictionary

    Args:
        dic (`dict`):  dictionary needs to be key renamed
        keymap: (`list` or `tuple`): list (tuple) of nested keys
        new_key ('str'): new key name
        
    Example:
        >>> dic =  {'k1': 'v1', 'k2': {'k21': 'v21', 'k22': 'v22'}}
        >>> nested_rename(dic, ['k2', 'k21'], 'k21_new')
        OR
        >>> nested_rename(dic, ('k2', 'k21'), 'k21_new')

    Returns: {'k1': 'v1', 'k2': {'k21_new': 'v21', 'k22': 'v22'}}
    """
    if len(keymap) == 1:
        dic[new_key] = dic.pop(keymap[0])
    else:
        dic[keymap[0]] = nestedkey_rename(dic[keymap[0]], keymap[1:], new_key)
    return dic

def reform_nestdict_from_keys(dic, key_list):
    """ Method returns a new nested dictionary from a given dictionary with 
    specific keysdefined in key_list

    Args:
        dic (`dict`): the template dictionary used to generate new dict
        key_list ('list'): a list of nested keys from the template dict.
                           format support: 
                           [['a', 'b', 'c'], ['a', 'b', 'd']]
                           OR
                           ['a.b.c', 'a.b.d']
    Examples:
        >>> dic = {'k1': 'v1', 'k2': {'k21': 'v21', 'k22': 'v22'}}
        >>> reform_nestdict_from_keys(dic, ['k1', 'k2.k21'])
    
    Returns: {'k1': 'v1', 'k2': {'k21': 'v21'}}
    """
    
    newdict = {}
    for i in key_list:
        if '.' in  i:
            value = get_value_from_nestdict(dic, i.split('.'))
            temp_dict = create_dict_from_nestedkeys(i.split('.'), value).copy()
        else:
            value = get_value_from_nestdict(dic, i)
            temp_dict = create_dict_from_nestedkeys(i, value).copy()
        newdict = merge_dict(newdict, temp_dict)
    return newdict

def create_dict_from_nestedkeys(keymap, value):
    """ Method returns a new nested dictionary with one nested key and value

    Args:
        keymap (`list`): a list contains flattened nested keys
        value ('obj'): the value for this nested key

    Examples:
        >>> create_dict_from_nestedkeys(['a','b','c'], 22)
    
    Returns: {'a' {'b': {'c': 22}}}
    """
    newdict = value
    for name in reversed(keymap):
        newdict = {name: newdict}
    return newdict

def get_value_from_nestdict(dic, keymap):
    """ method gets a value from a nested key in a nested dict

    Args:
        dic ('dict'): a nested dict
        keymap (`list`): a list contains flattened nested keys

    Examples:
        >>> get_value_from_nestdict({'a' {'b': {'c': 22, 'd': 33}}}, 
        ...                         ['a','b','c'])

    Returns: 22
    """
    for k in keymap: 
        dic = dic[k]
    return dic

def merge_dict(dic_result, dic, path=None, update=False, ignore_update=False):
    """ Method merges dic into dic_result

    Args:
        dic_result: the dict will be returned
        dic ('dict'): the dict used to merge with dict_result
        path (`list`): internal variable for keeping track of stack
        update (`bool`): dic will update dic_result in case of key value
                         mismatch
        ignore_update (`bool`): dic won't update dic_result in case of key
                                value mismatch

    Examples:
        >>> merge_dict({'province': {'city': 'ottawa'}}, 
        ...            {'province': {'county': 'kanata'}})

    Returns: {'province': {'county': 'kanata', 'city': 'ottawa'}}
    """
    if path is None:
        path = []
    for key in dic:
        if key in dic_result:
            if isinstance(dic_result[key], dict) and isinstance(dic[key], dict):
                merge_dict(dic_result[key], dic[key], path + [str(key)],
                           update=update, ignore_update=ignore_update)
            elif dic_result[key] == dic[key]:
                # same leaf value
                pass
            elif update:
                dic_result[key] = dic[key]
            elif ignore_update:
                # Same key has two different values, we keep the first one.
                pass
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            dic_result[key] = dic[key]
    return dic_result
