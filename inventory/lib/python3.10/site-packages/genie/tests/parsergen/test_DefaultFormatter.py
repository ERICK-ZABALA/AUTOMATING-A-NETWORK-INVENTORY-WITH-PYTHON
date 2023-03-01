#!/bin/env python

import unittest, inspect

# core
from genie.parsergen.core import DefaultFormatter


class TestDefaultFormatter(unittest.TestCase):

    def setUp(self):
        self._testString1 = \
         "This is a test of setting {=various} kinds of formatting."

        self._testString2 = \
         "First:{}, Second:{}, Third:{=3rd}, Fourth:{}"

        self._testString3 = \
         "First:{}, Second:{=2nd}, Third:{=3rd}, Fourth:{}"

        self._testString4 = \
         "First:{}, Second:{=2nd}, Third:{=3rd}"

        self._testString5 = \
         "First:{}, Second:{=2nd}, Third:{}, Fourth:{=4th}"

        self._testString6 = \
         "First:{firstarg}, Second:{secondarg}, Third:{thirdarg=3rd}, Fourth:{fourtharg}"

        self._testString9 = \
         "{}{=default-value!r}{mykey=another-default}{noneval}"

        self._testString10 = \
         "{: {align}{=18}}{=default-value!r}{mykey=another-default}{noneval}"





    def test_default_formatter1(self):
       args = []
       kwargs = {}
       self.assertEqual(DefaultFormatter().
        vformat(self._testString1, args, kwargs),
        "This is a test of setting various kinds of formatting.")


    def test_default_formatter2(self):
       args = [None]
       kwargs = {}
       self.assertEqual(DefaultFormatter().
        vformat(self._testString1, args, kwargs),
        "This is a test of setting various kinds of formatting.")

    def test_default_formatter3(self):
       args = ["first", "second", "third", "fourth"]
       kwargs = {}
       self.assertEqual(DefaultFormatter().
        vformat(self._testString2, args, kwargs),
        "First:first, Second:second, Third:third, Fourth:fourth")

    def test_default_formatter4(self):
       ''' IndexError is raised because non-defaulted fourth argument follows
           a defaulted and non-specified third argument.
       '''
       args = ["first", "second"]
       kwargs = {}
       self.assertRaises(IndexError, DefaultFormatter().
        vformat, self._testString2, args, kwargs)

    def test_default_formatter5(self):
       ''' By specifying our own default for positional arguments,
           we can avoid the IndexError.
       '''
       args = ["first", "second"]
       kwargs = {}
       self.assertEqual(DefaultFormatter(defidxval = 'defidx').
        vformat(self._testString2, args, kwargs),
        "First:first, Second:second, Third:3rd, Fourth:defidx")

       args = ["first"]
       self.assertEqual(DefaultFormatter(defidxval = 'defidx').
        vformat(self._testString2, args, kwargs),
        "First:first, Second:defidx, Third:3rd, Fourth:defidx")

    def test_default_formatter6(self):
       ''' We can avoid a KeyError by specifying a default key
       '''
       args = []
       kwargs= {'firstarg':'first', 'thirdarg':'third'}
       self.assertEqual(DefaultFormatter(defkeyval = 'defkey').
        vformat(self._testString6, args, kwargs),
        "First:first, Second:defkey, Third:third, Fourth:defkey")

    def test_default_formatter7(self):
       ''' Not explicitly specifying a defaulted key is OK, since there is
           a default embedded in the format string.
       '''
       args = []
       kwargs= {'firstarg':'first'}
       self.assertEqual(DefaultFormatter(defkeyval = 'defkey').
        vformat(self._testString6, args, kwargs),
        "First:first, Second:defkey, Third:3rd, Fourth:defkey")

       self.assertRaises(KeyError, DefaultFormatter().
        vformat, self._testString6, args, kwargs)

    def test_default_formatter8(self):
       ''' Specifying a positional argument of None triggers the default
           if so assigned in the format string.
       '''
       args = ["first", "second", None, "fourth"]
       kwargs = {}
       self.assertEqual(DefaultFormatter().
        vformat(self._testString2, args, kwargs),
        "First:first, Second:second, Third:3rd, Fourth:fourth")

    def test_default_formatter9(self):
       args = ["first", None, None, "fourth"]
       kwargs = {}
       self.assertEqual(DefaultFormatter().
        vformat(self._testString3, args, kwargs),
        "First:first, Second:2nd, Third:3rd, Fourth:fourth")

    def test_default_formatter10(self):
       args = ["first"]
       kwargs = {}
       self.assertEqual(DefaultFormatter().
        vformat(self._testString4, args, kwargs),
        "First:first, Second:2nd, Third:3rd")

    def test_default_formatter11(self):
       args = ["first", None, "third"]
       kwargs = {}
       self.assertEqual(DefaultFormatter().
        vformat(self._testString5, args, kwargs),
        "First:first, Second:2nd, Third:third, Fourth:4th")


    def test_default_formatter12(self):
       args = ["firstval"]
       kwargs = {"noneval":"None", "align":">"}
       self.assertEqual(DefaultFormatter().
        vformat(self._testString9, args, kwargs),
        "firstval'default-value'another-defaultNone")

    def test_default_formatter13(self):
       ''' Assigning defaulted key to None in order to select default.
       '''
       args = ["firstval"]
       kwargs = {"noneval":"None", "align":">", "mykey":None}
       self.assertEqual(DefaultFormatter().
        vformat(self._testString9, args, kwargs),
        "firstval'default-value'another-defaultNone")

       kwargs = {"noneval":"None", "align":">", "mykey":"myval"}
       self.assertEqual(DefaultFormatter().
        vformat(self._testString9, args, kwargs),
        "firstval'default-value'myvalNone")

    def test_default_formatter14(self):
       ''' Omitting defaulted key from kwargs also selects the default.
       '''
       args = ["firstval", 20]
       kwargs = {"noneval":"None", "align":">"}
       self.assertEqual(DefaultFormatter().
        vformat(self._testString10, args, kwargs),
        "            firstval'default-value'another-defaultNone")

       args = ["firstval"]
       self.assertEqual(DefaultFormatter().
        vformat(self._testString10, args, kwargs),
        "          firstval'default-value'another-defaultNone")

