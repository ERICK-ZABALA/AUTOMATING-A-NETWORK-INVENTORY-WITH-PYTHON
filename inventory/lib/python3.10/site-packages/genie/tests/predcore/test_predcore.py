#!/bin/env python
''' Unit tests for the predcore cisco-shared package.
'''

import unittest
import sys
import logging
import re
import time
from inspect import getmembers
from pprint import pprint
from textwrap import dedent

python3 = sys.version_info >= (3,0)

# module level logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


if python3:
    from unittest.mock import patch
    from unittest.mock import call
    from unittest.mock import create_autospec
    warnstr = 'warning'
else:
    from mock import patch
    from mock import call
    from mock import create_autospec
    warnstr = 'warn'

logging_mock = create_autospec(logging)
time_mock = create_autospec(time)
time_mock.time = create_autospec(time.time)
time_mock.sleep = create_autospec(time.sleep)
with patch.dict('sys.modules', {'logging' : logging_mock,
                                'time'    : time_mock},
                                autospec=True):
    from genie import predcore
    from genie.predcore import Predicate
    from genie.predcore import AndPredicate
    from genie.predcore import OrPredicate
    from genie.predcore import NotPredicate
    from genie.predcore import InPredicate
    from genie.predcore import PredicateTestedFalseSignal
    from genie.predcore import Prerequisite
    from genie.predcore import PrerequisiteWhile
    from genie.predcore import TimedPredicate
    from genie.predcore import FunctionCallEqualsPredicate
    from genie.predcore import InRangePredicate
    from genie.predcore import IterableEqualPredicate
    from genie.predcore import DictEqualPredicate
    from genie.predcore import ListEqualPredicate
    from genie.predcore import IsSubsetPredicate
    from genie.predcore import IsSupersetPredicate
    from genie.predcore import IsSequenceEqualDiffPredicate


class TestPredicatePrerequisite(unittest.TestCase):

    class IsEvenPredicate(Predicate):
        ''' Predicate that tests True if the input value is even '''

        def __init__(self, value):
            self._value = value

        def dump(self):
            return "IsEvenPredicate({})".format(self._value)

        def test(self):
            return (self._value % 2 == 0)


    class CountDownPredicate(Predicate):
        ''' Predicate that accepts a value and decrements it by one every time
            the predicate is tested for truth.  The predicate tests True
            as long as the value is positive and nonzero.'''

        def __init__(self, value):
            self._value = value

        def dump(self):
            return "CountDownPredicate({})".format(self._value)

        def test(self):
            self._value -= 1
            return (self._value <= 0 )

    @staticmethod
    def call_lists_are_equal(list1, list2):
        ''' Check for equality of two lists containing mocked-up calls.
        '''

        tolerance = 0.001
        '''Any two floats whose values differ by less than this value are
           considered equal.
        '''

        for item1,item2 in zip(list1, list2):
            str1 = str(item1)
            str2 = str(item2)
            if ('call.sleep' in str1) and ('call.sleep' in str2):
                #
                # If a call item is time.sleep(), extract the sleep duration
                # float and perform a proper tolerance-based comparison.
                #
                m1 = re.match('call\.sleep\(([0-9\.]+)\)', str1)
                m2 = re.match('call\.sleep\(([0-9\.]+)\)', str2)
                if      m1 and m2 and \
                        (abs(float(m1.groups()[0]) -
                             float(m2.groups()[0])) > tolerance):
                    logger.info('{} != {}'.format(str1, str2))
                    return False
            elif ('object at 0x' in str1) and ('object at 0x' in str2):
                #
                # Remove object references to allow call lists to be
                # properly compared.  Not only do the object references
                # change from run to run, but the representation in
                # python2 and python3 differs.
                #
                m1 = re.match('.*<(.*object at 0x[0-9a-f]+.*>)', str1)
                m2 = re.match('.*<(.*object at 0x[0-9a-f]+.*>)', str2)
                if m1 and m2:
                    str1 = re.sub(m1.groups()[0], '', str1)
                    str2 = re.sub(m2.groups()[0], '', str2)
                    if  str1 != str2:
                        logger.info('{} != {}'.format(str1, str2))
                        return False
            else:
                if item1 != item2:
                    logger.info('{} != {}'.format(str1, str2))
                    return False

        return True



    def setUp(self):
        self.maxDiff = None

        self.andPredOutput1 = """\
        AndPredicate (
        passed  : ,

        failed  : ,

        untested: CountDownPredicate(3)
                  CountDownPredicate(2)
                  CountDownPredicate(1))"""

        self.andPredOutput2 = """\
        AndPredicate (
        passed  : ,

        failed  : CountDownPredicate(2),

        untested: CountDownPredicate(2)
                  CountDownPredicate(1))"""

        self.andPredOutput3 = """\
        AndPredicate (
        passed  : ,

        failed  : CountDownPredicate(1),

        untested: CountDownPredicate(2)
                  CountDownPredicate(1))"""

        self.andPredOutput4 = """\
        AndPredicate (
        passed  : CountDownPredicate(0),

        failed  : CountDownPredicate(1),

        untested: CountDownPredicate(1))"""

        self.andPredOutput5 = """\
        AndPredicate (
        passed  : CountDownPredicate(-1)
                  CountDownPredicate(0)
                  CountDownPredicate(0),

        failed  : ,

        untested: )"""

        self.orPredOutput1 = """\
            OrPredicate (
            passed  : ,

            failed  : ,

            untested: CountDownPredicate(4)
                      CountDownPredicate(3)
                      CountDownPredicate(2))"""

        self.orPredOutput2 = """\
            OrPredicate (
            passed  : ,

            failed  : CountDownPredicate(3)
                      CountDownPredicate(2)
                      CountDownPredicate(1),

            untested: )"""

        self.orPredOutput3 = """\
            OrPredicate (
            passed  : CountDownPredicate(0),

            failed  : CountDownPredicate(2)
                      CountDownPredicate(1),

            untested: )"""

        self.orPredOutput4 = """\
            OrPredicate (
            passed  : CountDownPredicate(0),

            failed  : CountDownPredicate(1),

            untested: CountDownPredicate(0))"""

        self.orPredOutput5 = """\
            OrPredicate (
            passed  : CountDownPredicate(0),

            failed  : ,

            untested: CountDownPredicate(0)
                      CountDownPredicate(0))"""

        self.orPredOutput6 = """\
            OrPredicate (
            passed  : CountDownPredicate(-1),

            failed  : ,

            untested: CountDownPredicate(0)
                      CountDownPredicate(0))"""

        self.preq_timebase1 = (
            0,
            0.1, 0.1, 0.2, 1,
            1.2, 1.2, 1.3, 2,
            2.3, 2.3, 2.4, 3,
            3.1, 3.1, 3.2, 4,
            4.1, 4.1, 4.1, 5,
            5.1, 5.1, 5.1, 6
        )
        '''Time is checked initially, then before and after each contained
        AndPredicate truth test, if AndPredicate fails time is checked twice,
        once before the sleep and again after the sleep.'''

        self.preq_expected_timecalls1 = [
            call.time(),
            call.time(),
            call.time(),
            call.time(),
            call.sleep(0.8),
            call.time(),
            call.time(),
            call.time(),
            call.time(),
            call.sleep(0.7),
            call.time(),
            call.time(),
            call.time(),
            call.time(),
            call.sleep(0.6),
            call.time(),
            call.time(),
            call.time(),
            call.time()
        ]
        '''Expected calls made to time module from Prequisite class for
           test 1.
        '''

        self.preq_expected_timecalls2 = [
            call.time(),
            call.time(),
            call.time(),
            call.time(),
            call.sleep(0.8),
            call.time(),
            call.time(),
            call.time(),
            call.time(),
            call.sleep(0.7),
            call.time(),
        ]
        '''Expected calls made to time module from Prequisite class for
           test 2.
        '''

        self.preq_timebase3 = (
            0,
            0.2, 0.2, 0.4, 2,
            2.2, 2.2, 2.3, 4,
            4.3, 4.3, 4.4, 6,
            6.1, 6.1, 6.2, 8,
            8.1, 8.1, 8.1, 10,
            10.1, 10.1, 10.1, 12
        )
        '''Time is checked initially, then before and after each contained
        AndPredicate truth test, if AndPredicate fails time is checked twice,
        once before the sleep and again after the sleep.'''


        self.preq_timebase4 = (
            0,
            0.2, 0.2, 0.4, 2,
            2.2, 2.2, 2.3, 4,
            4.3, 114.3, 114.4, 116,
            116.1, 116.1, 116.2, 118,
            118.1, 118.1, 118.1, 120,
            120.1, 120.1, 120.1, 122
        )
        '''Time is checked initially, then before and after each contained
        AndPredicate truth test, if AndPredicate fails time is checked twice,
        once before the sleep and again after the sleep.'''



        self.preq_expected_timecalls3 = [
             call.time(),
             call.time(),
             call.time(),
             call.time(),
             call.sleep(1.6),
             call.time(),
             call.time(),
             call.time(),
             call.time(),
             call.sleep(1.7),
             call.time(),
             call.time(),
             call.time(),
             call.time(),
             call.sleep(1.6),
             call.time(),
             call.time(),
             call.time(),
             call.time()
        ]
        '''Expected calls made to time module from Prequisite class for
           test 3.
        '''


        self.preq_expected_loggingcalls3 = [
            call.getLogger(__name__).debug('Prerequisite is checking predicates over 8.0s at 2.0s intervals.'),
             call.getLogger(__name__).debug('Elapsed time [0.2s of 8.0s] '),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: CountDownPredicate(3), <test_predcore.TestPredicatePrerequisite.CountDownPredicate object at 0xf7e13ccc>'),
             call.getLogger(__name__).info('AndPredicate (\npassed  : ,\n\nfailed  : CountDownPredicate(2),\n\nuntested: CountDownPredicate(2)\n          CountDownPredicate(1))'),
             call.getLogger(__name__).debug('Sleeping remaining 1.6 seconds in interval'),
             call.getLogger(__name__).debug('Elapsed time [2.2s of 8.0s] '),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: CountDownPredicate(2), <test_predcore.TestPredicatePrerequisite.CountDownPredicate object at 0xf7e13ccc>'),
             call.getLogger(__name__).info('AndPredicate (\npassed  : ,\n\nfailed  : CountDownPredicate(1),\n\nuntested: CountDownPredicate(2)\n          CountDownPredicate(1))'),
             call.getLogger(__name__).debug('Sleeping remaining 1.7 seconds in interval'),
             call.getLogger(__name__).debug('Elapsed time [4.3s of 8.0s] '),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: CountDownPredicate(1), <test_predcore.TestPredicatePrerequisite.CountDownPredicate object at 0xf7e13ccc>'),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: CountDownPredicate(2), <test_predcore.TestPredicatePrerequisite.CountDownPredicate object at 0xf7e184ac>'),
             call.getLogger(__name__).info('AndPredicate (\npassed  : CountDownPredicate(0),\n\nfailed  : CountDownPredicate(1),\n\nuntested: CountDownPredicate(1))'),
             call.getLogger(__name__).debug('Sleeping remaining 1.6 seconds in interval'),
             call.getLogger(__name__).debug('Elapsed time [6.1s of 8.0s] '),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: CountDownPredicate(1), <test_predcore.TestPredicatePrerequisite.CountDownPredicate object at 0xf7e184ac>'),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: CountDownPredicate(1), <test_predcore.TestPredicatePrerequisite.CountDownPredicate frobject at 0xf7e1848c>')
        ]
        '''Expected calls made to logging module from Prequisite class for
           test 3.
        '''


        self.badArgsExceptionText1 = \
            ('Neither timeout nor iterations were specified.  Please specify at least one.',)

        self.badArgsExceptionText2 = \
            ('timeout and iterations are mutually exclusive, yet they were both specified.',)

        self.badArgsExceptionText3 = \
            ('testFunction must be a callable.',)

        self.predDumpExpectedOutput5_1 = \
            'Prerequisite (max wait time: 8, last elapsed: None)'

        self.predDumpExpectedOutput5_2 = \
            'Prerequisite (max wait time: 8, last elapsed: 6.1, \nAndPredicate (\npassed  : CountDownPredicate(0)\n          CountDownPredicate(0),\n\nfailed  : ,\n\nuntested: ))'

        self.predDumpExpectedOutput5_3 = \
            'Prerequisite (max wait time: 8, last elapsed: 0.2, \nAndPredicate (\npassed  : CountDownPredicate(-1)\n          CountDownPredicate(-1)\n          CountDownPredicate(-1),\n\nfailed  : ,\n\nuntested: ))'

        self.predDumpExpectedOutput2_1 = \
            'PrerequisiteWhile (max wait time: 5, last elapsed: None)'

        self.predDumpExpectedOutput2_2 = \
            'PrerequisiteWhile (max wait time: 5, last elapsed: 4.1, \nAndPredicate (\npassed  : ,\n\nfailed  : NotPredicate (CountDownPredicate(0)),\n\nuntested: NotPredicate (CountDownPredicate(2))\n          NotPredicate (CountDownPredicate(3))))'

        self.preq_expected_timecalls4 = \
            [call.time(),
             call.time(),
             call.time(),
             call.time(),
             call.sleep(0.8),
             call.time(),
             call.time(),
             call.time(),
             call.time(),
             call.sleep(0.7),
             call.time(),
             call.time(),
             call.time(),
             call.time(),
             call.sleep(0.6),
             call.time(),
             call.time(),
             call.time(),
             call.time(),
             call.sleep(0.8),
             call.time()]

        self.preq_expected_loggingcalls2 = \
            [call.getLogger(__name__).debug('PrerequisiteWhile is checking predicates over 5.0s at 1.0s intervals.'),
             call.getLogger(__name__).debug('Elapsed time [0.1s of 5.0s] '),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: NotPredicate (CountDownPredicate(5)), <predcore.NotPredicate object at 0xf7d1d66c>'),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: NotPredicate (CountDownPredicate(6)), <predcore.NotPredicate object at 0xf7d1d0ac>'),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: NotPredicate (CountDownPredicate(7)), <predcore.NotPredicate object at 0xf7c6d0cc>'),
             call.getLogger(__name__).debug('Sleeping remaining 0.8 seconds in interval'),
             call.getLogger(__name__).debug('Elapsed time [1.2s of 5.0s] '),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: NotPredicate (CountDownPredicate(4)), <predcore.NotPredicate object at 0xf7d1d66c>'),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: NotPredicate (CountDownPredicate(5)), <predcore.NotPredicate object at 0xf7d1d0ac>'),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: NotPredicate (CountDownPredicate(6)), <predcore.NotPredicate object at 0xf7c6d0cc>'),
             call.getLogger(__name__).debug('Sleeping remaining 0.7 seconds in interval'),
             call.getLogger(__name__).debug('Elapsed time [2.3s of 5.0s] '),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: NotPredicate (CountDownPredicate(3)), <predcore.NotPredicate object at 0xf7d1d66c>'),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: NotPredicate (CountDownPredicate(4)), <predcore.NotPredicate object at 0xf7d1d0ac>'),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: NotPredicate (CountDownPredicate(5)), <predcore.NotPredicate object at 0xf7c6d0cc>'),
             call.getLogger(__name__).debug('Sleeping remaining 0.6 seconds in interval'),
             call.getLogger(__name__).debug('Elapsed time [3.1s of 5.0s] '),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: NotPredicate (CountDownPredicate(2)), <predcore.NotPredicate object at 0xf7d1d66c>'),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: NotPredicate (CountDownPredicate(3)), <predcore.NotPredicate object at 0xf7d1d0ac>'),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: NotPredicate (CountDownPredicate(4)), <predcore.NotPredicate object at 0xf7c6d0cc>'),
             call.getLogger(__name__).debug('Sleeping remaining 0.8 seconds in interval'),
             call.getLogger(__name__).debug('Elapsed time [4.1s of 5.0s] '),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: NotPredicate (CountDownPredicate(1)), <predcore.NotPredicate object at 0xf7d1d66c>')]

        self.predDumpExpectedOutput2 = \
            'PrerequisiteWhile (max wait time: 5, last elapsed: 4.1, \nAndPredicate (\npassed  : ,\n\nfailed  : NotPredicate (CountDownPredicate(0)),\n\nuntested: NotPredicate (CountDownPredicate(2))\n          NotPredicate (CountDownPredicate(3))))'

        self.expectedFuncResult1 = ('argument1', 'argument2', None, (),
        {'kwarg3': 'kwargument3'})

        self.expectedFuncResult2 = ('argument1', 'argument2', 'wrongargument3',
        (), {'kwarg3': 'kwargument3'})



        self.expectedDumpResult1 = "FunctionCallEqualsPredicate (\n(myFunc1 (arg1='argument1', arg2='argument2', kwargs={'kwarg3': 'kwargument3'}, arg3=None) \n== ('argument1', 'argument2', None, (), {'kwarg3': 'kwargument3'})) , \nNotTestedYet)"

        self.expectedDumpResult1_py2 = "FunctionCallEqualsPredicate (\n(myFunc1 (arg1='argument1', arg2='argument2', args=(), arg3=None, kwargs={'kwarg3': 'kwargument3'}) \n== ('argument1', 'argument2', None, (), {'kwarg3': 'kwargument3'})) , \nNotTestedYet)"

        self.expectedDumpResult2 = "FunctionCallEqualsPredicate (\n(myFunc1 (arg1='argument1', arg2='argument2', kwargs={'kwarg3': 'kwargument3'}, arg3=None) \n== ('argument1', 'argument2', None, (), {'kwarg3': 'kwargument3'})), \nComparisonSucceeded)"
        self.expectedDumpResult2_py2 = "FunctionCallEqualsPredicate (\n(myFunc1 (arg1='argument1', arg2='argument2', args=(), arg3=None, kwargs={'kwarg3': 'kwargument3'}) \n== ('argument1', 'argument2', None, (), {'kwarg3': 'kwargument3'})), \nComparisonSucceeded)"

        self.badFuncCompareExceptionText1 = ("FunctionCallEqualsPredicate (\n(myFunc1 (arg1='argument1', arg2='argument2', arg3='argument3', kwargs={'kwarg3': 'kwargument3'}) \n== ('argument1', 'argument2', 'wrongargument3', (), {'kwarg3': 'kwargument3'})), \nComparisonFailed (actual = ('argument1', 'argument2', 'argument3', (), {'kwarg3': 'kwargument3'})))",)

        self.badFuncCompareExceptionText1_py2 = ("FunctionCallEqualsPredicate (\n(myFunc1 (arg1='argument1', arg2='argument2', arg3='argument3', args=(), kwargs={'kwarg3': 'kwargument3'}) \n== ('argument1', 'argument2', 'wrongargument3', (), {'kwarg3': 'kwargument3'})), \nComparisonFailed (actual = ('argument1', 'argument2', 'argument3', (), {'kwarg3': 'kwargument3'})))",)

        self.allowableRanges = [
            range(2,4),
            range(7,15)
        ]

        if not python3:
            self.allowableXranges = [
            xrange(2,4),
            xrange(7,15)
        ]

        self.allowableNumbers = [2,3,7,8,9]

        self.rangeDump1 = 'InRangePredicate ((78 in (2, 4), (7, 15)), \nNotInRange)'

        self.rangeDump2 = 'InRangePredicate ((7 in (2, 4), (7, 15)) , \nNotTestedYet)'

        self.rangeDump3 = 'InRangePredicate ((7 in (2, 4), (7, 15)), \nInRange)'


        self.rangeExceptionText1 = ('InRangePredicate ((78 in (2, 4), (7, 15)), \nNotInRange)',)



        self.listEqualDumpExpectedOutput1 = 'ListEqualPredicate (\n(test if actual [1, 2, 3] \n== expected [1, 2, 3]), \n{})'

        self.listEqualDumpExpectedOutput2 = 'ListEqualPredicate (\n(test if actual [1, 2, 3, 4] \n== expected [1, 2, 3]), \n{})'

        self.listEqualDumpExpectedOutput3 =  'ListEqualPredicate (\n(test if actual [1, 2, 3, 4] \n== expected [1, 2, 3]), \nAreNotEqual : (\nItemsInActualButNotInExpected : [4]))'

        self.listEqualDumpExpectedOutput4 = 'ListEqualPredicate (\n(test if actual [1, 2, 3] \n== expected [1, 2, 3, 4]), \n{})'

        self.listEqualDumpExpectedOutput5 =  'ListEqualPredicate (\n(test if actual [1, 2, 3] \n== expected [1, 2, 3, 4]), \nAreNotEqual : (\nItemsInExpectedButNotInActual : [4]))'

        self.listEqualDumpExpectedOutput6 = 'ListEqualPredicate (\n(test if actual [1, 2, 3, 5] \n== expected [1, 2, 3, 4]), \n{})'

        self.listEqualDumpExpectedOutput7 =  'ListEqualPredicate (\n(test if actual [1, 2, 3, 5] \n== expected [1, 2, 3, 4]), \nAreNotEqual : (\nItemsInActualButNotInExpected : [5], \nItemsInExpectedButNotInActual : [4]))'

        self.listCompareExceptionText1 = ("actual_iterable is not an iterable",)

        self.listCompareExceptionText2 = ("expected_iterable is not an iterable",)

        self.dictEqualDumpExpectedOutputPattern1 = "AreNotEqual : \(\nItemsInActualButNotInExpected : \['key3'\], \nItemsInExpectedButNotInActual : \['key4'\]\)"

        self.dictEqualDumpExpectedOutputPattern2 = "AreNotEqual : \(\nItemsInActualButNotInExpected : \['key4'\]\)"

        self.dictEqualDumpExpectedOutputPattern3 = "AreNotEqual : \(\nItemsInExpectedButNotInActual : \['key4'\]\)"

        self.dictEqualDumpExpectedOutputPattern4 = "AreNotEqual : \(\nUnexpectedValue \(Item key2 has value value2actual \(expected value2bad\)\)\)"

        self.dictEqualDumpExpectedOutputPattern5 = "AreNotEqual : \(\nItemsInActualButNotInExpected : \['key4'\], \nItemsInExpectedButNotInActual : \['key5'\], \nUnexpectedValue \(Item key2 has value value2actual \(expected value2bad\)\)\)"

        self.dictCompareExceptionText1 = ("actual_dict is not a dictionary",)

        self.dictCompareExceptionText2 = ("expected_dict is not a dictionary",)

        self.subsetDumpExpectedOutput1 = 'IsSubsetPredicate ((test if [2, 4] is a subset of [1, 2, 3, 4, 5, 6]), \n{})'

        self.subsetDumpExpectedOutput2 = 'IsSubsetPredicate ((test if [2, 4, 6] is a subset of [1, 2, 3, 4, 5]), \n{})'

        self.subsetExceptionText1 = ("first_iterable is not an iterable",)

        self.subsetExceptionText2 = ("is_subset_of_iterable is not an iterable",)



        self.supersetDumpExpectedOutput1 = 'IsSupersetPredicate ((test if [1, 2, 3, 4, 5, 6] is a superset of [2, 4]), \n{})'

        self.supersetDumpExpectedOutput2 = 'IsSupersetPredicate ((test if [1, 2, 3, 4, 5] is a superset of [2, 4, 6]), \n{})'

        self.supersetExceptionText1 = ("first_iterable is not an iterable",)

        self.supersetExceptionText2 = ("is_superset_of_iterable is not an iterable",)


        self.sequenceDiffDumpExpectedOutput1 = 'IsSequenceEqualDiffPredicate (\n(test if actual [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] \n== expected [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), \n{})'

        self.sequenceDiffDumpExpectedOutput2 = 'IsSequenceEqualDiffPredicate (\n(test if actual [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] \n== expected [1, 2, 5, 4, 3, 6, 7, 8, 9, 20, 10]), \nAreNotEqual : (\n@@ -[1:2], +[1:2] @@\n [2]\n+[5, 4]\n [3]\n-[4, 5]\n [6]\n@@ -[8:9], +[8:9] @@\n [9]\n+[20]\n [10]\n))'

        self.sequenceDiffDumpExpectedOutput3 = 'IsSequenceEqualDiffPredicate (\n(test if actual [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] \n== expected [1, 2, 5, 4, 3, 6, 7, 8, 9, 20, 10, 15, 16, 17, 18]), \nAreNotEqual : (\n@@ -[0:2], +[0:2] @@\n [1, 2]\n+[5, 4]\n [3]\n-[4, 5]\n [6, 7, 8, 9]\n+[20]\n [10]\n-[11, 12, 13, 14]\n+[15, 16, 17, 18]\n))'

        self.sequenceDiffDumpExpectedOutput4 = 'IsSequenceEqualDiffPredicate (\n(test if actual [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] \n== expected [1, 2, 5, 4, 3, 6, 7, 8, 9, 20, 10, 15, 16, 17, 18]), \nAreNotEqual : (\n [1, 2]\n+[5, 4]\n [3]\n-[4, 5]\n [6, 7, 8, 9]\n+[20]\n [10]\n-[11, 12, 13, 14]\n+[15, 16, 17, 18]\n))'

        self.sequenceDiffExceptionText1 = ("actual_sequence is not a sequence",)

        self.sequenceDiffExceptionText2 = ("expected_sequence is not a sequence",)



        self.preq_expected_timecalls5 = [
             call.time(),
             call.time(),
             call.time(),
             call.time(),
             call.sleep(2.6),
             call.time(),
        ]
        '''Expected calls made to time module from Prequisite class for
           test_prereq_pred_faketime9.
        '''

        self.preq_expected_loggingcalls4 = \
            [call.getLogger(__name__).warning('The timeout was specified as 1, which being less than the interval value 3 could lead to unnecessary waiting.'),
             call.getLogger(__name__).debug('Prerequisite is checking predicates over 1.0s at 3.0s intervals.'),
             call.getLogger(__name__).debug('Elapsed time [0.2s of 1.0s] '),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: CountDownPredicate(3), <test_predcore.TestPredicatePrerequisite.CountDownPredicate object at 0xf7d4c5ac>'),
             call.getLogger(__name__).info('AndPredicate (\npassed  : ,\n\nfailed  : CountDownPredicate(2),\n\nuntested: CountDownPredicate(2)\n          CountDownPredicate(1))'),
             call.getLogger(__name__).debug('Sleeping remaining 2.6 seconds in interval')]




        self.preq_expected_timecalls6 = [
             call.time(),
             call.time(),
             call.time(),
             call.time(),
             call.sleep(0.6),
             call.time(),
        ]
        '''Expected calls made to time module from Prequisite class for
           test_prereq_pred_faketime9.
        '''

        self.preq_expected_loggingcalls5 = \
            [call.getLogger(__name__).warning('The timeout was specified as 1, which being less than the interval value 2 could lead to unnecessary waiting.'),
             call.getLogger(__name__).warning('Reassigning the default interval value to 1.'),
             call.getLogger(__name__).debug('Prerequisite is checking predicates over 1.0s at 1.0s intervals.'),
             call.getLogger(__name__).debug('Elapsed time [0.2s of 1.0s] '),
             call.getLogger(__name__).debug('AndPredicate is checking predicate: CountDownPredicate(3), <test_predcore.TestPredicatePrerequisite.CountDownPredicate object at 0xf7d4c5ac>'),
             call.getLogger(__name__).info('AndPredicate (\npassed  : ,\n\nfailed  : CountDownPredicate(2),\n\nuntested: CountDownPredicate(2)\n          CountDownPredicate(1))'),
             call.getLogger(__name__).debug('Sleeping remaining 0.6 seconds in interval')]













    def test_base_pred_truth(self):
        'Ensure that the base predicate class tests False'
        p1 = Predicate()
        self.assertFalse(p1)

    def test_base_pred_truth_callable(self):
        'Ensure that the base predicate class tests False'
        p1 = Predicate()
        self.assertFalse(p1())

    def test_base_pred_asserts(self):
        '''Ensure that the base predicate class raises an exception when
        assert_test is called on it.
        Test proper behavior whether or not user specifies a message,
        '''
        p1 = Predicate()
        with self.assertRaises(PredicateTestedFalseSignal) as cm:
            p1.assert_test()
        self.assertEqual(cm.exception.args, ('Predicate (last_result = False)',))

        with self.assertRaises(PredicateTestedFalseSignal) as cm:
            p1.assert_test("This is a test")
        self.assertEqual(cm.exception.args,
            ('This is a test\nPredicate (last_result = False)',))

        with self.assertRaises(PredicateTestedFalseSignal) as cm:
            p1.assert_test("This is a test", "Another test")
        self.assertEqual(cm.exception.args,
            ('This is a test\nAnother test\nPredicate (last_result = False)',))

    def test_subclass_pred_truth(self):
        'Ensure that a derived predicate class tests True or False as expected'
        myPredFalseInstance = self.IsEvenPredicate(1)
        myPredTrueInstance = self.IsEvenPredicate(2)
        self.assertFalse(myPredFalseInstance)
        self.assertTrue(myPredTrueInstance)

    def test_subclass_pred_asserts(self):
        '''Ensure that a derived predicate class raises an exception when
        assert_test is called on it.
        Test proper behavior whether or not user specifies a message,
        '''
        myPredFalseInstance = self.IsEvenPredicate(1)
        with self.assertRaises(PredicateTestedFalseSignal) as cm:
            myPredFalseInstance.assert_test()
        self.assertEqual(cm.exception.args, ('IsEvenPredicate(1)',))

        with self.assertRaises(PredicateTestedFalseSignal) as cm:
            myPredFalseInstance.assert_test("This is a test")
        self.assertEqual(cm.exception.args,
            ('This is a test\nIsEvenPredicate(1)',))


    def test_and_pred_truth(self):
        '''Do truth testing on AndPredicate,
           which wraps a list of other simple objects that are tested
           for truth.
        '''
        ap = AndPredicate(1,1)
        self.assertEqual(ap.dump(),
        'AndPredicate (\npassed  : ,\n\nfailed  : ,\n\nuntested: 1\n          1)')
        self.assertTrue(ap)

        self.assertEqual(ap.dump(),
        'AndPredicate (\npassed  : 1\n          1,\n\nfailed  : ,\n\nuntested: )')

        ap = AndPredicate(1,0)
        self.assertFalse(ap)

        self.assertEqual(ap.dump(),
        'AndPredicate (\npassed  : 1,\n\nfailed  : 0,\n\nuntested: )')

        ap = AndPredicate(0,1)
        self.assertFalse(ap)

        self.assertEqual(ap.dump(),
        'AndPredicate (\npassed  : ,\n\nfailed  : 0,\n\nuntested: 1)')

        ap = AndPredicate(0,0)
        self.assertFalse(ap)

        self.assertEqual(ap.dump(),
        'AndPredicate (\npassed  : ,\n\nfailed  : 0,\n\nuntested: 0)')

    def test_and_pred_input_pred_truth(self):
        '''Do truth testing on AndPredicate,
           which wraps a list of other predicates.
           Ensure predicates are tested in the same order specified by the
           user.  Also test flattening.
        '''
        ap = AndPredicate(self.CountDownPredicate(3),
                           (self.CountDownPredicate(2),
                           self.CountDownPredicate(1)))
        self.assertEqual(ap.dump(), dedent(self.andPredOutput1))
        self.assertFalse(ap)
        self.assertEqual(ap.dump(), dedent(self.andPredOutput2))
        self.assertFalse(ap)
        self.assertEqual(ap.dump(), dedent(self.andPredOutput3))
        self.assertFalse(ap)
        self.assertEqual(ap.dump(), dedent(self.andPredOutput4))
        self.assertTrue(ap)
        self.assertEqual(ap.dump(), dedent(self.andPredOutput5))

    def test_and_pred_asserts(self):
        '''Ensure that a AndPredicate object raises an exception when
        assert_test is called on it.
        Test proper behavior whether or not user specifies a message,
        '''
        myPredFalseInstance = AndPredicate(1,0)
        with self.assertRaises(PredicateTestedFalseSignal) as cm:
            myPredFalseInstance.assert_test()
        self.assertEqual(cm.exception.args, \
            ('AndPredicate (\npassed  : 1,\n\nfailed  : 0,\n\nuntested: )',))

        with self.assertRaises(PredicateTestedFalseSignal) as cm:
            myPredFalseInstance.assert_test("This is a test")
        self.assertEqual(cm.exception.args,
            ('This is a test\n'
             'AndPredicate (\npassed  : 1,\n\nfailed  : 0,\n\nuntested: )',))


    def test_or_pred_truth(self):
        '''Do truth testing on OrPredicate,
           which wraps a list of other simple objects that are tested
           for truth.
        '''
        op = OrPredicate(1,1)
        self.assertEqual(op.dump(),
        'OrPredicate (\npassed  : ,\n\nfailed  : ,\n\nuntested: 1\n          1)')
        self.assertTrue(op)

        self.assertEqual(op.dump(),
        'OrPredicate (\npassed  : 1,\n\nfailed  : ,\n\nuntested: 1)')

        op = OrPredicate(1,0)
        self.assertTrue(op)

        self.assertEqual(op.dump(),
        'OrPredicate (\npassed  : 1,\n\nfailed  : ,\n\nuntested: 0)')

        op = OrPredicate(0,1)
        self.assertTrue(op)

        self.assertEqual(op.dump(),
        'OrPredicate (\npassed  : 1,\n\nfailed  : 0,\n\nuntested: )')

        op = OrPredicate(0,0)
        self.assertFalse(op)

        self.assertEqual(op.dump(),
        'OrPredicate (\npassed  : ,\n\nfailed  : 0\n          0,\n\nuntested: )')


    def test_or_pred_input_pred_truth(self):
        '''Do truth testing on OrPredicate,
           which wraps a list of other predicates.
           Ensure predicates are tested in the same order specified by the
           user.  Also test flattening.
        '''
        op = OrPredicate((self.CountDownPredicate(4),
                         (self.CountDownPredicate(3),
                         self.CountDownPredicate(2))))
        self.assertEqual(op.dump(), dedent(self.orPredOutput1))
        self.assertFalse(op)
        self.assertEqual(op.dump(), dedent(self.orPredOutput2))
        self.assertTrue(op)
        self.assertEqual(op.dump(), dedent(self.orPredOutput3))
        self.assertTrue(op)
        self.assertEqual(op.dump(), dedent(self.orPredOutput4))
        self.assertTrue(op)
        self.assertEqual(op.dump(), dedent(self.orPredOutput5))
        self.assertTrue(op)
        self.assertEqual(op.dump(), dedent(self.orPredOutput6))



    def test_in_pred_truth(self):
        '''Do truth testing on InPredicate, which tests if an object is
           a member of a sequence.
        '''
        ip = InPredicate(1, (4,3,2,1))
        self.assertEqual(ip.dump(), 'InPredicate (1, (4, 3, 2, 1))')
        self.assertTrue(ip)

        ip = InPredicate(5, (4,3,2,1))
        self.assertEqual(ip.dump(), 'InPredicate (5, (4, 3, 2, 1))')
        self.assertFalse(ip)

    def test_prereq_pred_message(self):
        ''' Given a set of predicate, if the first one pass, and the rest fails
        we expect to see into the passed section the passed predicate
        '''
        time_mock.reset_mock()
        time_mock.time.side_effect = self.preq_timebase1
        prereq = Prerequisite(self.IsEvenPredicate(0),
                              self.IsEvenPredicate(1),
                              timeout=2)

        expected = ('Prerequisite (max wait time: 2, '\
                    'last elapsed: 2.0, \nAndPredicate '\
                    '(\npassed  : ,\n\nfailed  : IsEvenPredicate(1),'\
                    '\n\nuntested: ))',)
        with self.assertRaises(PredicateTestedFalseSignal) as cm:
            prereq.assert_test()
        self.assertEqual(cm.exception.args, expected)

    def test_prereq_pred_message_extra(self):
        ''' Given a set of predicate, if the first one pass, and the rest fails
        we expect to see into the passed section the passed predicate. Also
        if an extra message was given, we expect to see it first
        '''
        time_mock.reset_mock()
        time_mock.time.side_effect = self.preq_timebase1
        prereq = Prerequisite(self.IsEvenPredicate(0),
                              self.IsEvenPredicate(1),
                              timeout=2)

        expected = ('Extra message\nPrerequisite (max wait time: 2, '\
                    'last elapsed: 2.0, \nAndPredicate '\
                    '(\npassed  : ,\n\nfailed  : IsEvenPredicate(1),'\
                    '\n\nuntested: ))',)
        with self.assertRaises(PredicateTestedFalseSignal) as cm:
            prereq.assert_test('Extra message')
        self.assertEqual(cm.exception.args, expected)

    def test_prereq_pred_faketime1 (self):
      '''Redefine time in order to quickly test Prequisite class.
         Ensure predicate tests ``True`` if it is given enough time for all
         the contained predicates to test ``True``.
      '''
      time_mock.reset_mock()
      time_mock.time.side_effect = self.preq_timebase1
      prereq = Prerequisite(self.CountDownPredicate(3),
                            self.CountDownPredicate(2),
                            self.CountDownPredicate(1),
                            iterations=10, interval=1)
      self.assertTrue(prereq)
      self.assertTrue(self.call_lists_are_equal(
        time_mock.mock_calls, self.preq_expected_timecalls1))


    def test_prereq_pred_faketime2 (self):
      '''Redefine time in order to quickly test Prequisite class.
         Ensure predicate tests ``False`` on timeout when not all
         contained predicates test ``True``.
      '''
      time_mock.reset_mock()
      time_mock.time.side_effect = self.preq_timebase1
      prereq = Prerequisite(self.CountDownPredicate(3),
                            self.CountDownPredicate(2),
                            self.CountDownPredicate(1),
                            iterations=3, interval=1)
      self.assertFalse(prereq)
      self.assertTrue(self.call_lists_are_equal(
        time_mock.mock_calls, self.preq_expected_timecalls2))


    def test_prereq_pred_faketime3 (self):
      '''Redefine time in order to quickly test Prequisite class.
         Test default interval and logging.
      '''
      logging_mock.reset_mock()
      time_mock.reset_mock()
      time_mock.time.side_effect = self.preq_timebase3
      prereq = Prerequisite(self.CountDownPredicate(3),
                            self.CountDownPredicate(2),
                            self.CountDownPredicate(1),
                            iterations=4)
      self.assertTrue(prereq)
      self.assertTrue(self.call_lists_are_equal(
        time_mock.mock_calls, self.preq_expected_timecalls3))

      self.assertTrue(self.call_lists_are_equal(
        logging_mock.mock_calls, self.preq_expected_loggingcalls3))


    def test_prereq_pred_faketime4 (self):
      '''Redefine time in order to quickly test Prequisite class.
         Test failure on timeout.  Increase timeout and test for success.
         Have the prerequisite wake up late (past its timeout) and ensure
         the time remaining is properly reported.
      '''
      time_mock.reset_mock()
      time_mock.time.side_effect = self.preq_timebase3
      prereq = Prerequisite(self.CountDownPredicate(3),
                            self.CountDownPredicate(2),
                            self.CountDownPredicate(1),
                            timeout=6)
      self.assertFalse(prereq)

      time_mock.reset_mock()
      time_mock.time.side_effect = self.preq_timebase3
      prereq = Prerequisite(self.CountDownPredicate(3),
                            self.CountDownPredicate(2),
                            self.CountDownPredicate(1),
                            timeout=7)
      self.assertTrue(prereq)
      self.assertTrue(self.call_lists_are_equal(
        time_mock.mock_calls, self.preq_expected_timecalls3))

      time_mock.reset_mock()
      time_mock.time.side_effect = self.preq_timebase3
      prereq = Prerequisite(self.CountDownPredicate(3),
                            self.CountDownPredicate(2),
                            self.CountDownPredicate(2),
                            timeout=7)
      self.assertFalse(prereq)
      self.assertEqual("{:.1f}".format(prereq.time_remaining), '0.0')



    def test_prereq_pred_faketime5 (self):
      '''Redefine time in order to quickly test Prequisite class.
         Test flattening, time remaining, and dump() contents.
         Re-test the predicate and ensure all contained objects
         are re-tested.
      '''
      time_mock.reset_mock()
      time_mock.time.side_effect = self.preq_timebase3
      prereq = Prerequisite((self.CountDownPredicate(3),
                            (self.CountDownPredicate(2),
                            self.CountDownPredicate(1))),
                            iterations=4)
      self.assertEqual("{:.1f}".format(prereq.time_remaining), '8.0')
      self.assertEqual(prereq.dump(), self.predDumpExpectedOutput5_1)
      self.assertTrue(prereq)
      self.assertEqual("{:.1f}".format(prereq.time_remaining), '1.9')
      self.assertTrue(self.call_lists_are_equal(
        time_mock.mock_calls, self.preq_expected_timecalls3))
      self.assertEqual(prereq.dump(), self.predDumpExpectedOutput5_2)

      time_mock.time.side_effect = self.preq_timebase3
      self.assertTrue(prereq)
      self.assertEqual("{:.1f}".format(prereq.time_remaining), '7.8')
      self.assertEqual(prereq.dump(), self.predDumpExpectedOutput5_3)



    def test_prereq_pred_faketime6 (self):
      '''Redefine time in order to quickly test Prequisite class.
         Test the case where the test takes an extraordinarily long time
         to complete, causing the timeout to be exceeded and iteration to
         stop.  In this case, the predicates are not tested enough times to
         allow the prerequisite to pass.
      '''
      time_mock.reset_mock()
      time_mock.time.side_effect = self.preq_timebase4
      prereq = Prerequisite((self.CountDownPredicate(3),
                            (self.CountDownPredicate(2),
                            self.CountDownPredicate(1))),
                            iterations=4)
      self.assertEqual("{:.1f}".format(prereq.time_remaining), '8.0')
      self.assertEqual(prereq.dump(), self.predDumpExpectedOutput5_1)
      self.assertFalse(prereq)
      self.assertEqual("{:.1f}".format(prereq.time_remaining), '0.0')


    def test_prereq_pred_faketime7 (self):
      '''Redefine time in order to quickly test Prequisite class.
         Test the case where the test takes an extraordinarily long time
         to complete, causing the timeout to be exceeded and iteration to
         stop.  In this case, the predicates are tested enough times to
         allow the prerequisite to pass because the maximum timeout is
         extended.
      '''
      time_mock.reset_mock()
      time_mock.time.side_effect = self.preq_timebase4
      prereq = Prerequisite((self.CountDownPredicate(3),
                            (self.CountDownPredicate(2),
                            self.CountDownPredicate(1))),
                            timeout=120)
      self.assertEqual("{:.1f}".format(prereq.time_remaining), '120.0')
      self.assertTrue(prereq)
      self.assertEqual("{:.1f}".format(prereq.time_remaining), '3.9')




    def test_prereq_pred_faketime8 (self):
      '''Redefine time in order to quickly test Prequisite class.
         Test the case where the sleep takes an extraordinarily long time
         to complete, causing the timeout to be exceeded and iteration to
         stop.  In this case, the predicates are not tested enough times to
         allow the prerequisite to pass.  This could occur, for example,
         if the user was using pdb to debug by setting breakpoints.
      '''
      time_mock.reset_mock()
      time_mock.time.side_effect = self.preq_timebase4
      prereq = Prerequisite((self.CountDownPredicate(3),
                            (self.CountDownPredicate(2),
                            self.CountDownPredicate(1))),
                            iterations=4)
      self.assertEqual("{:.1f}".format(prereq.time_remaining), '8.0')
      self.assertEqual(prereq.dump(), self.predDumpExpectedOutput5_1)
      self.assertFalse(prereq)
      self.assertEqual("{:.1f}".format(prereq.time_remaining), '0.0')


    def test_prereq_pred_faketime9 (self):
      '''Redefine time in order to quickly test Prequisite class.
         Test warning is raised when timeout is specified less than a
         non-default interval.
      '''
      logging_mock.reset_mock()
      time_mock.reset_mock()
      time_mock.time.side_effect = self.preq_timebase3
      prereq = Prerequisite(self.CountDownPredicate(3),
                            self.CountDownPredicate(2),
                            self.CountDownPredicate(1),
                            timeout=1, interval=3)
      self.assertFalse(prereq)

      self.assertTrue(self.call_lists_are_equal(
        time_mock.mock_calls, self.preq_expected_timecalls5))

      self.assertTrue(self.call_lists_are_equal(
        logging_mock.mock_calls, self.preq_expected_loggingcalls4))


    def test_prereq_pred_faketime10 (self):
      '''Redefine time in order to quickly test Prequisite class.
         Test warning is raised when timeout is specified less than the
         default interval.
      '''
      logging_mock.reset_mock()
      time_mock.reset_mock()
      time_mock.time.side_effect = self.preq_timebase3
      prereq = Prerequisite(self.CountDownPredicate(3),
                            self.CountDownPredicate(2),
                            self.CountDownPredicate(1),
                            timeout=1)
      self.assertFalse(prereq)

      self.assertTrue(self.call_lists_are_equal(
        time_mock.mock_calls, self.preq_expected_timecalls6))

      self.assertTrue(self.call_lists_are_equal(
        logging_mock.mock_calls, self.preq_expected_loggingcalls5))




    def test_prereq_pred_badargs (self):
      '''Test that ValueError exception is raised when neither time nor
         iterations are specified.
      '''
      with self.assertRaises(ValueError) as cm:
          prereq = Prerequisite(self.CountDownPredicate(3),
                                self.CountDownPredicate(2),
                                self.CountDownPredicate(1))
      self.assertEqual(cm.exception.args, self.badArgsExceptionText1)

      with self.assertRaises(ValueError) as cm:
          prereq = Prerequisite(self.CountDownPredicate(3),
                                self.CountDownPredicate(2),
                                self.CountDownPredicate(1),
                                timeout=10, iterations=3)

      self.assertEqual(cm.exception.args, self.badArgsExceptionText2)


    def test_prereq_while_faketime1 (self):
      '''Test the PrerequisiteWhile class by giving it a list of predicates
         that remain True for a length of time and then become False.
         Ensure that the predicate tests True if all contained predicates
         remain True.
      '''
      time_mock.reset_mock()
      time_mock.time.side_effect = self.preq_timebase1
      prereq = PrerequisiteWhile(NotPredicate(self.CountDownPredicate(5)),
                                 NotPredicate(self.CountDownPredicate(6)),
                                 NotPredicate(self.CountDownPredicate(7)),
                                 iterations=4, interval=1)
      self.assertTrue(prereq)
      self.assertTrue(self.call_lists_are_equal(
        time_mock.mock_calls, self.preq_expected_timecalls1))


    def test_prereq_while_faketime2 (self):
      '''Test the PrerequisiteWhile class by giving it a list of predicates
         that remain True for a length of time and then become False.
         Ensure that the predicate tests False if one of the contained
         predicates becomes False.  Test dump() contents.
      '''
      logging_mock.reset_mock()
      time_mock.reset_mock()
      time_mock.time.side_effect = self.preq_timebase1
      prereq = PrerequisiteWhile(NotPredicate(self.CountDownPredicate(5)),
                                 NotPredicate(self.CountDownPredicate(6)),
                                 NotPredicate(self.CountDownPredicate(7)),
                                 iterations=5, interval=1)
      self.assertEqual(prereq.dump(), self.predDumpExpectedOutput2_1)
      self.assertFalse(prereq)
      self.assertTrue(self.call_lists_are_equal(
        logging_mock.mock_calls, self.preq_expected_loggingcalls2))
      self.assertEqual(prereq.dump(), self.predDumpExpectedOutput2_2)


    def test_timed_iterate_non_callable(self):
        '''Test that timed_iterate throws a ValueError if a callable is not
           provided to it.
        '''

        class MyBogusClass(TimedPredicate):

            def test (self):
                try:
                    return self.timed_iterate(
                        testFunction         = 1,
                        valToReturnOnTimeout = False)
                except PredicateTestedFalseSignal:
                    return True


        with self.assertRaises(ValueError) as cm:
            myObj = MyBogusClass(timeout=10)
            myObj.test()

        self.assertEqual(cm.exception.args, self.badArgsExceptionText3)


    @staticmethod
    def myFunc1 (arg1, arg2, arg3=None, *args,
            **kwargs):
      return (arg1, arg2, arg3, args, kwargs)

    def test_func_pred_1 (self):
        '''Test FunctionCallEqualsPredicate matches successfully and has
           expected dump output.
        '''
        funcPred = FunctionCallEqualsPredicate(self.myFunc1,
           self.expectedFuncResult1,
          'argument1', 'argument2',
          kwarg3='kwargument3')

        if python3:
            self.assertEqual(funcPred.dump(), self.expectedDumpResult1)
        else:
            self.assertEqual(funcPred.dump(), self.expectedDumpResult1_py2)

        funcPred.assert_test()

        if python3:
            self.assertEqual(funcPred.dump(), self.expectedDumpResult2)
        else:
            self.assertEqual(funcPred.dump(), self.expectedDumpResult2_py2)

    def test_func_pred_2 (self):
        '''Test FunctionCallEqualsPredicate failure to match.
        '''
        self.maxDiff = None
        funcPred = FunctionCallEqualsPredicate(self.myFunc1,
           self.expectedFuncResult2,
          'argument1', 'argument2', 'argument3',
          kwarg3='kwargument3')

        with self.assertRaises(PredicateTestedFalseSignal) as cm:
            funcPred.assert_test()

        if python3:
            self.assertEqual(cm.exception.args,
                             self.badFuncCompareExceptionText1)
        else:
            self.assertEqual(cm.exception.args,
                             self.badFuncCompareExceptionText1_py2)


    def test_range_pred_1 (self):
        '''Test InRangePredicate dump text, failure and success for single
           values.
        '''

        rangePred = InRangePredicate (78, *self.allowableRanges)

        with self.assertRaises(PredicateTestedFalseSignal) as cm:
            rangePred.assert_test()

        self.assertEqual(cm.exception.args, self.rangeExceptionText1)


        rangePred = InRangePredicate (7, *self.allowableRanges)
        self.assertEqual(rangePred.dump(), self.rangeDump2)

        rangePred.assert_test()
        self.assertEqual(rangePred.dump(), self.rangeDump3)


    def test_range_pred_2 (self):
        '''Use InRangePredicate to filter multiple values.
        '''

        allowableNumbers = []
        for number in range(1,10):
            pred = InRangePredicate (number, *self.allowableRanges)
            if pred:
                allowableNumbers.append(number)

        self.assertEqual(allowableNumbers, self.allowableNumbers)



    def test_range_pred_3 (self):
        '''Use InRangePredicate to filter multiple values using xranges.
        '''

        if not python3:
            allowableNumbers = []
            for number in range(1,10):
                pred = InRangePredicate (number, *self.allowableXranges)
                if pred:
                    allowableNumbers.append(number)

            self.assertEqual(allowableNumbers, self.allowableNumbers)


    def test_listcompare_pred_1 (self):
        '''Test successful set-based list comparison
        '''
        pred = ListEqualPredicate([1,2,3], [3,2,1])
        self.assertEqual(pred.dump(),
            self.listEqualDumpExpectedOutput1.format("NotTestedYet"))
        self.assertTrue(pred)
        self.assertEqual(pred.dump(),
            self.listEqualDumpExpectedOutput1.format("AreEqual"))



    def test_listcompare_pred_2 (self):
        '''Test failing set-based list comparison where actual list has an
           extra item.
        '''
        pred = ListEqualPredicate([1,2,3,4], [3,2,1])
        self.assertEqual(pred.dump(),
            self.listEqualDumpExpectedOutput2.format("NotTestedYet"))
        self.assertFalse(pred)
        self.assertEqual(pred.dump(),
            self.listEqualDumpExpectedOutput3)




    def test_listcompare_pred_3 (self):
        '''Test failing set-based list comparison where expected list has an
           extra item.
        '''
        pred = ListEqualPredicate([1,2,3], [4,3,2,1])
        self.assertEqual(pred.dump(),
            self.listEqualDumpExpectedOutput4.format("NotTestedYet"))
        self.assertFalse(pred)
        self.assertEqual(pred.dump(),
            self.listEqualDumpExpectedOutput5)




    def test_listcompare_pred_4 (self):
        '''Test failing set-based list comparison where both actual and
           expected lists have an extra item.
        '''
        pred = ListEqualPredicate([1,2,3,5], [4,3,2,1])
        self.assertEqual(pred.dump(),
            self.listEqualDumpExpectedOutput6.format("NotTestedYet"))
        self.assertFalse(pred)
        self.assertEqual(pred.dump(),
            self.listEqualDumpExpectedOutput7)



    def test_listcompare_pred_5 (self):
        '''Test ValueError is raised for non-iterable input parameters.
        '''
        with self.assertRaises(ValueError) as cm:
            pred = ListEqualPredicate(1, [4,3,2,1])
        self.assertEqual(cm.exception.args, self.listCompareExceptionText1)

        with self.assertRaises(ValueError) as cm:
            pred = ListEqualPredicate([1,2,3,5], 1)
        self.assertEqual(cm.exception.args, self.listCompareExceptionText2)


    def test_listcompare_pred_6 (self):
        '''Test successful set-based list comparison, and flattening.
        '''
        pred = ListEqualPredicate([1,[2,3]], ((3,(2,1))))
        self.assertEqual(pred.dump(),
            self.listEqualDumpExpectedOutput1.format("NotTestedYet"))
        self.assertTrue(pred)
        self.assertEqual(pred.dump(),
            self.listEqualDumpExpectedOutput1.format("AreEqual"))




    def test_dictcompare_pred_1 (self):
        '''Test successful dictionary comparison.
        '''
        actualDict = {'key1' : 'value1', 'key2' : 'value2', 'key3' : 'value3'}
        pred = DictEqualPredicate(actualDict, actualDict)
        self.assertTrue(pred)


    def test_dictcompare_pred_2 (self):
        '''Test failing dictionary comparison with nonmatching items in each
           dict .
        '''
        actualDict = {'key1' : 'value1', 'key2' : 'value2', 'key3' : 'value3'}
        expectedDict = {'key1' : 'value1', 'key2' : 'value2', 'key4' : 'value4'}
        pred = DictEqualPredicate(actualDict, expectedDict)
        self.assertFalse(pred)
        self.assertTrue(re.findall(\
            self.dictEqualDumpExpectedOutputPattern1, pred.dump()), pred.dump())


    def test_dictcompare_pred_3 (self):
        '''Test failing dictionary comparison with nonmatching item in actual
           dict.
        '''
        actualDict = {'key1' : 'value1', 'key2' : 'value2', 'key3' : 'value3',
            'key4' : 'value4'}
        expectedDict = {'key1' : 'value1', 'key2' : 'value2', 'key3' : 'value3'}
        pred = DictEqualPredicate(actualDict, expectedDict)
        self.assertFalse(pred)
        self.assertTrue(re.findall(\
            self.dictEqualDumpExpectedOutputPattern2, pred.dump()), pred.dump())



    def test_dictcompare_pred_4 (self):
        '''Test failing dictionary comparison with nonmatching item in expected
           dict.
        '''
        actualDict = {'key1' : 'value1', 'key2' : 'value2', 'key3' : 'value3'}
        expectedDict = {'key1' : 'value1', 'key2' : 'value2', 'key3' : 'value3',
            'key4' : 'value4'}
        pred = DictEqualPredicate(actualDict, expectedDict)
        self.assertFalse(pred)
        self.assertTrue(re.findall(\
            self.dictEqualDumpExpectedOutputPattern3, pred.dump()), pred.dump())





    def test_dictcompare_pred_5 (self):
        '''Test dictionary comparison where one key's value differs.
        '''
        actualDict = \
            {'key1' : 'value1', 'key2' : 'value2actual', 'key3' : 'value3'}
        expectedDict = \
            {'key1' : 'value1', 'key2' : 'value2bad', 'key3' : 'value3'}
        pred = DictEqualPredicate(actualDict, expectedDict)
        self.assertFalse(pred)
        self.assertTrue(re.findall(\
            self.dictEqualDumpExpectedOutputPattern4, pred.dump()), pred.dump())


    def test_dictcompare_pred_6 (self):
        '''Test dictionary comparison where two key values differ.
        '''
        actualDict = \
            {'key1' : 'value1', 'key2' : 'value2actual', 'key3':'value3actual'}
        expectedDict = \
            {'key1' : 'value1', 'key2' : 'value2bad', 'key3':'value3bad'}
        pred = DictEqualPredicate(actualDict, expectedDict)
        self.assertFalse(pred)


    def test_dictcompare_pred_7 (self):
        '''Test dictionary comparison where one key value differs and an extra
           key exists in both dictionaries.
        '''
        actualDict = \
            {'key1' : 'value1', 'key2' : 'value2actual', 'key3':'value3',
             'key4' : 'value4'}
        expectedDict = \
            {'key1' : 'value1', 'key2' : 'value2bad', 'key3':'value3',
             'key5' : 'value5'}
        pred = DictEqualPredicate(actualDict, expectedDict)
        self.assertFalse(pred)
        self.assertTrue(re.findall(\
            self.dictEqualDumpExpectedOutputPattern5, pred.dump()), pred.dump())


    def test_dictcompare_pred_8 (self):
        '''Test ValueError is raised for non-mapping input parameters.
        '''
        goodDict = {'key1' : 'value1', 'key2' : 'value2', 'key3' : 'value3'}
        with self.assertRaises(ValueError) as cm:
            pred = DictEqualPredicate(1, goodDict)
        self.assertEqual(cm.exception.args, self.dictCompareExceptionText1)

        with self.assertRaises(ValueError) as cm:
            pred = DictEqualPredicate(goodDict, 1)
        self.assertEqual(cm.exception.args, self.dictCompareExceptionText2)


    def test_subset_pred_1 (self):
        '''Test success path of subset predicate.
        '''
        pred = IsSubsetPredicate ((2,4), (1,2,3,4,5,6))
        self.assertEqual(pred.dump(), \
            self.subsetDumpExpectedOutput1.format('NotTestedYet'))
        self.assertTrue(pred)
        self.assertEqual(pred.dump(), \
            self.subsetDumpExpectedOutput1.format('IsSubset'))


    def test_subset_pred_2 (self):
        '''Test failure path of subset predicate, and flattening.
        '''
        pred = IsSubsetPredicate ((2,4,6), (1,(2,3),4,5))
        self.assertFalse(pred)
        self.assertEqual(pred.dump(), \
            self.subsetDumpExpectedOutput2.format('IsNotSubset'))


    def test_subset_pred_3 (self):
        '''Test ValueError is raised for non-iterable input parameters.
        '''
        goodIterable = [1,2,3]
        badIterable = 1
        with self.assertRaises(ValueError) as cm:
            pred = IsSubsetPredicate(badIterable, goodIterable)
        self.assertEqual(cm.exception.args, self.subsetExceptionText1)

        with self.assertRaises(ValueError) as cm:
            pred = IsSubsetPredicate(goodIterable, badIterable)
        self.assertEqual(cm.exception.args, self.subsetExceptionText2)



    def test_superset_pred_1 (self):
        '''Test success path of superset predicate.
        '''
        pred = IsSupersetPredicate ((1,2,3,4,5,6), (2,4))
        self.assertEqual(pred.dump(), \
            self.supersetDumpExpectedOutput1.format('NotTestedYet'))
        self.assertTrue(pred)
        self.assertEqual(pred.dump(), \
            self.supersetDumpExpectedOutput1.format('IsSuperset'))


    def test_superset_pred_2 (self):
        '''Test failure path of superset predicate, and flattening.
        '''
        pred = IsSupersetPredicate ((1,(2,3),4,5),(2,4,6))
        self.assertFalse(pred)
        self.assertEqual(pred.dump(), \
            self.supersetDumpExpectedOutput2.format('IsNotSuperset'))


    def test_superset_pred_3 (self):
        '''Test ValueError is raised for non-iterable input parameters.
        '''
        goodIterable = [1,2,3]
        badIterable = 1
        with self.assertRaises(ValueError) as cm:
            pred = IsSupersetPredicate(badIterable, goodIterable)
        self.assertEqual(cm.exception.args, self.supersetExceptionText1)

        with self.assertRaises(ValueError) as cm:
            pred = IsSupersetPredicate(goodIterable, badIterable)
        self.assertEqual(cm.exception.args, self.supersetExceptionText2)



    def test_sequence_pred_1 (self):
        '''Test success path of superset predicate, and flattening.
        '''
        pred = IsSequenceEqualDiffPredicate ( \
            [1,2,3,4,5,(6,(7,8,9),10)],
            [1,2,3,4,5,(6,(7,8,9),10)])
        self.assertEqual(pred.dump(), \
            self.sequenceDiffDumpExpectedOutput1.format("NotTestedYet"))
        self.assertTrue(pred)
        self.assertEqual(pred.dump(), \
            self.sequenceDiffDumpExpectedOutput1.format("AreEqual"))


    def test_sequence_pred_2 (self):
        '''Test failure path of superset predicate with flatting and default
           context_lines.
        '''
        pred = IsSequenceEqualDiffPredicate ( \
            [1,2,3,4,5,(6,(7,8,9),10)],
            [1,2,5,4,3,6,7,8,9,20,10])
        self.assertFalse(pred)
        self.assertEqual(pred.dump(), self.sequenceDiffDumpExpectedOutput2)



    def test_sequence_pred_2 (self):
        '''Test failure path of superset predicate with flatting and default
           context_lines.
        '''
        pred = IsSequenceEqualDiffPredicate ( \
            [1,2,3,4,5,(6,(7,8,9),10,11,12,13,14)],
            [1,2,5,4,3,6,7,8,9,20,10,15,16,17,18],
            context_lines=20)
        self.assertFalse(pred)
        self.assertEqual(pred.dump(), self.sequenceDiffDumpExpectedOutput3)




    def test_sequence_pred_3 (self):
        '''Test failure path of superset predicate with flatting and zero
           context_lines.
        '''
        pred = IsSequenceEqualDiffPredicate ( \
            [1,2,3,4,5,(6,(7,8,9),10,11,12,13,14)],
            [1,2,5,4,3,6,7,8,9,20,10,15,16,17,18],
            context_lines=0)
        self.assertFalse(pred)
        self.assertEqual(pred.dump(), self.sequenceDiffDumpExpectedOutput4)



    def test_sequence_pred_4 (self):
        '''Test ValueError is raised for non-sequence input parameters.
        '''
        goodSequence = [1,2,3,4]
        badSequence = {'key1' : 'value1', 'key2' : 'value2', 'key3' : 'value3'}
        with self.assertRaises(ValueError) as cm:
            pred = IsSequenceEqualDiffPredicate(badSequence, goodSequence)
        self.assertEqual(cm.exception.args, self.sequenceDiffExceptionText1)

        with self.assertRaises(ValueError) as cm:
            pred = IsSequenceEqualDiffPredicate(goodSequence, badSequence)
        self.assertEqual(cm.exception.args, self.sequenceDiffExceptionText2)

