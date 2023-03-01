#!/usr/bin/env python

# Import unittest module
import unittest
from unittest.mock import Mock
import inspect

from genie.conf.base.cli import CliConfigBuilder

class test_CliConfigBuilder(unittest.TestCase):

    def test_append_line(self):

        for unconfig in (True, False):
            with self.subTest(unconfig=unconfig):
                configurations = CliConfigBuilder(unconfig=unconfig)

                configurations.append_line('outer1')
                configurations.append_line('outer2')
                configurations.append_line('outer3', unconfig_cmd='custom3')
                configurations.append_line('raw4', unconfig_cmd='ignored', raw=True)

                if unconfig:
                    l = [
                        'no outer1',
                        'no outer2',
                        'custom3',
                        'raw4',
                    ]
                else:
                    l = [
                        'outer1',
                        'outer2',
                        'outer3',
                        'raw4',
                    ]

                self.assertSequenceEqual(configurations, l)
                self.assertEqual(str(configurations), '\n'.join(l))

    def test_append_block(self):

        for indent in (None, True, ' ', '>>> '):
            for unconfig in (True, False):
                with self.subTest(unconfig=unconfig):
                    configurations = CliConfigBuilder(unconfig=unconfig)

                    sub_configurations = CliConfigBuilder()
                    sub_configurations.append_line('sub1')
                    sub_configurations.append_line('sub2')
                    configurations.append_block(sub_configurations, indent=indent)

                    configurations.append_block('string1', indent=indent)
                    configurations.append_block('stringlines1\nstringlines2', indent=indent)

                    configurations.append_block(['list1', 'list2'], indent=indent)

                    if indent is None:
                        indent = ''
                    elif indent is True:
                        indent = ' '

                    l = [
                        indent + 'sub1',
                        indent + 'sub2',
                        indent + 'string1',
                        indent + 'stringlines1',
                        indent + 'stringlines2',
                        indent + 'list1',
                        indent + 'list2',
                    ]

                    self.assertSequenceEqual(configurations, l)
                    self.assertEqual(str(configurations), '\n'.join(l))

    def test_submode_context(self):

        # not unconfig, usual
        configurations = CliConfigBuilder()
        configurations.append_line('outer1')
        with configurations.submode_context('submode1'):
            configurations.append_line('inner1')
            configurations.append_line('inner2')
        configurations.append_line('outer2')
        l = [
            'outer1',
            'submode1',
            ' inner1',
            ' inner2',
            ' exit',
            'outer2',
        ]
        self.assertSequenceEqual(configurations, l)
        self.assertEqual(str(configurations), '\n'.join(l))

        # exit_cmd
        configurations = CliConfigBuilder()
        configurations.append_line('outer1')
        with configurations.submode_context('submode1', exit_cmd='customexit1'):
            configurations.append_line('inner1')
            configurations.append_line('inner2')
        configurations.append_line('outer2')
        l = [
            'outer1',
            'submode1',
            ' inner1',
            ' inner2',
            ' customexit1',
            'outer2',
        ]
        self.assertSequenceEqual(configurations, l)
        self.assertEqual(str(configurations), '\n'.join(l))

        # if not unconfig, cancel_empty = False
        configurations = CliConfigBuilder()
        configurations.append_line('outer1')
        with configurations.submode_context('submode1'):
            pass
        configurations.append_line('outer2')
        l = [
            'outer1',
            'submode1',
            ' exit',
            'outer2',
        ]
        self.assertSequenceEqual(configurations, l)
        self.assertEqual(str(configurations), '\n'.join(l))

        # not unconfig and not cancel_empty
        configurations = CliConfigBuilder()
        configurations.append_line('outer1')
        with configurations.submode_context('submode1', cancel_empty=False):
            pass
        configurations.append_line('outer2')
        l = [
            'outer1',
            'submode1',
            ' exit',
            'outer2',
        ]
        self.assertSequenceEqual(configurations, l)
        self.assertEqual(str(configurations), '\n'.join(l))

        # not unconfig and cancel_empty
        configurations = CliConfigBuilder()
        configurations.append_line('outer1')
        with configurations.submode_context('submode1', cancel_empty=True):
            pass
        configurations.append_line('outer2')
        l = [
            'outer1',
            'outer2',
        ]
        self.assertSequenceEqual(configurations, l)
        self.assertEqual(str(configurations), '\n'.join(l))

        # unconfig, usual
        configurations = CliConfigBuilder(unconfig=True)
        configurations.append_line('outer1')
        with configurations.submode_context('submode1'):
            configurations.append_line('inner1')
            configurations.append_line('inner2')
        configurations.append_line('outer2')
        l = [
            'no outer1',
            'submode1',
            ' no inner1',
            ' no inner2',
            ' exit',
            'no outer2',
        ]
        self.assertSequenceEqual(configurations, l)
        self.assertEqual(str(configurations), '\n'.join(l))

        # if unconfig, cancel_empty = True
        configurations = CliConfigBuilder(unconfig=True)
        configurations.append_line('outer1')
        with configurations.submode_context('submode1'):
            pass
        configurations.append_line('outer2')
        l = [
            'no outer1',
            'no outer2',
        ]
        self.assertSequenceEqual(configurations, l)
        self.assertEqual(str(configurations), '\n'.join(l))

        # unconfig and not cancel_empty
        configurations = CliConfigBuilder(unconfig=True)
        configurations.append_line('outer1')
        with configurations.submode_context('submode1', cancel_empty=False):
            pass
        configurations.append_line('outer2')
        l = [
            'no outer1',
            'no submode1',
            'no outer2',
        ]
        self.assertSequenceEqual(configurations, l)
        self.assertEqual(str(configurations), '\n'.join(l))

        # unconfig and not cancel_empty w/ unconfig_cmd
        configurations = CliConfigBuilder(unconfig=True)
        configurations.append_line('outer1')
        with configurations.submode_context('submode1', cancel_empty=False, unconfig_cmd='custom1'):
            pass
        configurations.append_line('outer2')
        l = [
            'no outer1',
            'custom1',
            'no outer2',
        ]
        self.assertSequenceEqual(configurations, l)
        self.assertEqual(str(configurations), '\n'.join(l))

        # unconfig and cancel_empty
        configurations = CliConfigBuilder(unconfig=True)
        configurations.append_line('outer1')
        with configurations.submode_context('submode1', cancel_empty=True):
            pass
        configurations.append_line('outer2')
        l = [
            'no outer1',
            'no outer2',
        ]
        self.assertSequenceEqual(configurations, l)
        self.assertEqual(str(configurations), '\n'.join(l))

    def test_submode_cancel(self):

        for unconfig in (True, False):
            # unconfig has no effect
            with self.subTest(unconfig=unconfig):

                # must be within a submode_context
                configurations = CliConfigBuilder(unconfig=unconfig)
                with self.assertRaises(RuntimeError):
                    configurations.submode_cancel()

                for cancel_empty in (None, True, False):
                    # cancel_empty has no effect
                    with self.subTest(cancel_empty=cancel_empty):

                        configurations = CliConfigBuilder(unconfig=unconfig)
                        configurations.append_line('outer1', raw=True)
                        reached1 = False
                        with configurations.submode_context('submode1', cancel_empty=cancel_empty):
                            configurations.append_line('never seen')
                            reached1 = True
                            configurations.submode_cancel()
                            raise AssertionError("never reached")
                        self.assertTrue(reached1)
                        configurations.append_line('outer2', raw=True)
                        l = [
                            'outer1',
                            'outer2',
                        ]
                        self.assertSequenceEqual(configurations, l)
                        self.assertEqual(str(configurations), '\n'.join(l))

    def test_submode_unconfig(self):

        for unconfig in (True, False):
            with self.subTest(unconfig=unconfig):

                # must be within a submode_context, unconfig or not
                configurations = CliConfigBuilder(unconfig=unconfig)
                with self.assertRaises(RuntimeError):
                    configurations.submode_unconfig()

                for cancel_empty in (None, True, False):
                    # cancel_empty has no effect
                    with self.subTest(cancel_empty=cancel_empty):

                        if not unconfig:

                            # must be in unconfig mode
                            configurations = CliConfigBuilder(unconfig=unconfig)
                            with configurations.submode_context('submoe1'):
                                with self.assertRaises(RuntimeError):
                                    configurations.submode_unconfig()

                            break

                        configurations = CliConfigBuilder(unconfig=unconfig)
                        configurations.append_line('outer1', raw=True)
                        reached1 = False
                        with configurations.submode_context('submode1', cancel_empty=cancel_empty):
                            configurations.append_line('never seen')
                            reached1 = True
                            configurations.submode_unconfig()
                            raise AssertionError("never reached")
                        self.assertTrue(reached1)
                        configurations.append_line('outer2', raw=True)
                        l = [
                            'outer1',
                            'no submode1',
                            'outer2',
                        ]
                        self.assertSequenceEqual(configurations, l)
                        self.assertEqual(str(configurations), '\n'.join(l))

                        configurations = CliConfigBuilder(unconfig=unconfig)
                        configurations.append_line('outer1', raw=True)
                        reached1 = False
                        with configurations.submode_context('submode1', cancel_empty=cancel_empty, unconfig_cmd='custom1'):
                            configurations.append_line('never seen')
                            reached1 = True
                            configurations.submode_unconfig()
                            raise AssertionError("never reached")
                        self.assertTrue(reached1)
                        configurations.append_line('outer2', raw=True)
                        l = [
                            'outer1',
                            'custom1',
                            'outer2',
                        ]
                        self.assertSequenceEqual(configurations, l)
                        self.assertEqual(str(configurations), '\n'.join(l))

if __name__ == '__main__':
    unittest.main()
