#!/usr/bin/env python

import unittest
from unittest.mock import Mock

from genie.utils.cisco_collections import *


class test_typed_set(unittest.TestCase):

    def test_init(self):

        with self.assertRaises(TypeError):
            typedset()
        with self.assertRaises(TypeError):
            typedset(None)
        with self.assertRaises(TypeError):
            typedset('a')

        s = typedset(int)
        self.assertEqual(s, set())
        self.assertRegex(repr(s), r'^typedset\(int\)$')
        s.add(1)
        s.add(2)
        s.add(3)
        s.add(2)
        s.remove(3)
        self.assertEqual(s, {1, 2})
        self.assertRegex(repr(s), r'^typedset\(int, \{\d+, \d+\}\)$')

        s = typedset(int, '')
        self.assertEqual(s, set())
        self.assertRegex(repr(s), r'^typedset\(int\)$')
        s.add(1)
        s.add(2)
        s.add(3)
        s.add(2)
        s.remove(3)
        self.assertEqual(s, {1, 2})
        self.assertRegex(repr(s), r'^typedset\(int, \{\d+, \d+\}\)$')

        def my_func(value):
            return int(value)
        s = typedset(my_func, '54634')
        self.assertEqual(s, set(int(c) for c in '54634'))
        self.assertRegex(repr(s), r'^typedset\(<function \S+.<locals>.my_func at 0x\w+>, \{\d+, \d+, \d+, \d+\}\)$')

        with self.assertRaises(ValueError):
            s.add('abc')
        with self.assertRaises(ValueError):
            s.remove('abc')

if __name__ == '__main__':
    unittest.main()

# vim: ft=python et sw=4
