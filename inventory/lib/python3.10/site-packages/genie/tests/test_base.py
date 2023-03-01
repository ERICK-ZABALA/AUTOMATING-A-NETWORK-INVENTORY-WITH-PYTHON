#!/usr/bin/env python

import unittest
from unittest.mock import Mock
from unittest import TestCase

import weakref

from genie.base import Base


class test_Base(TestCase):

    def test_init(self):

        class C(Base):
            a = 1

        c = C()
        self.assertEqual(c.a, 1)
        with self.assertRaises(AttributeError):
            c.b

        c = C(a=2)
        self.assertEqual(c.a, 2)
        with self.assertRaises(AttributeError):
            c.b

        c = C(b=3)
        self.assertEqual(c.a, 1)
        self.assertEqual(c.b, 3)

    def test_repr(self):

        class C(Base):
            pass

        c = C()
        self.assertEqual(repr(c), '<C object at 0x%x>' % (id(c),))
        c.name = 'hello'
        self.assertEqual(repr(c), '<C object \'hello\' at 0x%x>' % (id(c),))
        c.name = None
        self.assertEqual(repr(c), '<C object None at 0x%x>' % (id(c),))


if __name__ == '__main__':
    unittest.main()

# vim: ft=python et sw=4
