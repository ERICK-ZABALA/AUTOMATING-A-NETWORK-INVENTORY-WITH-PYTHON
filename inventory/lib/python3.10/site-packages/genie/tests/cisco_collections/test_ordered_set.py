#!/usr/bin/env python

import unittest
from unittest.mock import Mock

from genie.utils.cisco_collections import *

class test_ordered_set(unittest.TestCase):

    def test_as_set(self):

        class OrderedSetSubclass(OrderedSet):
            pass

        for s in (
            'abracadaba',
            'simsalabim',
        ):
            with self.subTest(s=s):
                set1 = set(s)
                oset1 = OrderedSetSubclass(s)
                for i in range(len(set1)):
                    e = s[i]
                    with self.subTest(i=i, e=e):
                        self.assertIn(e, oset1)
                self.assertNotIn('z', oset1)
                # Behave like Python's set; Order is not important.
                self.assertEqual(set1, set1)
                self.assertEqual(oset1, set1)
                self.assertEqual(set1, oset1)
                self.assertEqual(oset1, OrderedSet(reversed(s)))

                self.assertEqual(oset1 | {'a', 'b', 's'}, set1 | {'a', 'b', 's'})
                self.assertIs(type(oset1 | {'a', 'b', 's'}), type(oset1))
                oset2 = OrderedSetSubclass(oset1)
                oset2 |= {'a', 'b', 's'}
                self.assertEqual(oset2, set1 | {'a', 'b', 's'})

                self.assertEqual(oset1 & {'a', 'b', 's'}, set1 & {'a', 'b', 's'})
                self.assertIs(type(oset1 & {'a', 'b', 's'}), type(oset1))
                oset2 = OrderedSetSubclass(oset1)
                oset2 &= {'a', 'b', 's'}
                self.assertEqual(oset2, set1 & {'a', 'b', 's'})

                self.assertEqual(oset1 ^ {'a', 'b', 's'}, set1 ^ {'a', 'b', 's'})
                self.assertIs(type(oset1 ^ {'a', 'b', 's'}), type(oset1))
                oset2 = OrderedSetSubclass(oset1)
                oset2 ^= {'a', 'b', 's'}
                self.assertEqual(oset2, set1 ^ {'a', 'b', 's'})

                self.assertEqual(oset1 - {'a', 'b', 's'}, set1 - {'a', 'b', 's'})
                self.assertIs(type(oset1 - {'a', 'b', 's'}), type(oset1))
                oset2 = OrderedSetSubclass(oset1)
                oset2 -= {'a', 'b', 's'}
                self.assertEqual(oset2, set1 - {'a', 'b', 's'})

    def test_as_sequence(self):

        class OrderedSetSubclass(OrderedSet):
            pass

        seq1 = 'abcde'
        oset1 = OrderedSetSubclass(seq1)
        self.assertSequenceEqual(oset1, seq1)
        for i in range(len(seq1)):
            with self.subTest(i=i):
                self.assertEqual(oset1[i], seq1[i])
        for start in range(-len(seq1), len(seq1)+1):
            for stop in range(-len(seq1), len(seq1)+1):
                for step in range(-3, 4):
                    if step == 0:
                        continue
                    i = slice(start, stop, step)
                    with self.subTest(i=i):
                        v = oset1[i]
                        self.assertIs(type(v), type(oset1))
                        self.assertSequenceEqual(v, seq1[i])

if __name__ == '__main__':
    unittest.main()

# vim: ft=python et sw=4
