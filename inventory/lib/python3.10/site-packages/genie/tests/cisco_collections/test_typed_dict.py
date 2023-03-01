#!/usr/bin/env python

import unittest
from unittest.mock import Mock

from genie.utils.cisco_collections import *


class test_typed_dict(unittest.TestCase):

    def test_init(self):

        with self.assertRaises(TypeError):
            typeddict()
        with self.assertRaises(TypeError):
            typeddict(None)
        with self.assertRaises(TypeError):
            typeddict(('a', 1))

        d = typeddict((str, int))
        self.assertEqual(d, dict())
        self.assertRegex(repr(d), r'^typeddict\(\(str, int\)\)$')
        d[1] = 1
        d[2] = 2
        d[3] = 3
        d[4] = 4
        d['1'] = 4
        del d[2]
        del d['4']
        self.assertEqual(d, {'1': 4, '3':3})
        self.assertRegex(repr(d), r'^typeddict\(\(str, int\), \{.+\}\)$')

        with self.assertRaises(ValueError):
            d[1] = 'abc'

if __name__ == '__main__':
    unittest.main()

# vim: ft=python et sw=4
