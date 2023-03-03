import os
import sys
import copy
import unittest
import functools
import importlib
import pkg_resources
from collections import OrderedDict
from pkg_resources import load_entry_point
from pkg_resources import iter_entry_points
from unittest.mock import patch

from pyats import aetest
from pyats import results
from pyats.aetest import runtime, CommonSetup, CommonCleanup
from pyats.aetest.sections import Subsection, TestSection
from pyats.aetest.signals import ResultSignal
from pyats.datastructures.logic import And, Not, Or
from pyats.aetest.signals import AEtestSkippedSignal
from pyats import configuration as cfg

from genie.conf.base import Testbed, Device

from genie.harness.script import TestScript
from genie.harness.discovery import GenieScriptDiscover, \
    GenieCommonSetupDiscover, \
    GenieCommonCleanupDiscover, \
    GenieTestcasesDiscover, \
    _load_processors
from genie.tests.harness.script.triggers import TriggerShutNoShutBgp, \
    TriggerShutNoShutOspf, \
    TriggerBgpNoSetupCleanup, \
    TriggerOspfWtSetupCleanup, \
    TriggerHsrpWtSetup, \
    TriggerVlanWtCleanup, \
    TriggerIsisBasic
from genie.tests.harness.script.verifications import VerifyOps, \
    a_callable, \
    a_error_callable, \
    a_failing_callable, \
    a_callable_always_same, \
    a_missing_arg_callable

from genie.libs.sdk.triggers.template.devicenotfound import TriggerDeviceNotFound

sys.path.append(os.path.dirname(__file__))
from script.triggers import TriggerAetestLoop, TriggerAetestLoopParams
from genie.harness.discovery_helper import Verifications

# Entrypoint group to extend genie libraries (e.g. in genielibs.cisco)
TRIGGER_ENTRY_POINT = 'genie.libs.sdk.triggers'
# Pyats config path to specify which local/external pkg to look in for triggers
PYATS_EXT_TRIGGER_CFG_PATH = 'pyats.libs.external.trigger'


class MockDevice(object):
    def __init__(self, testbed, name, os):
        self.testbed = testbed
        self.name = name
        self.os = os


class TestTestScriptDiscovery(unittest.TestCase):
    triggers1 = {'TriggerShutNoShutBgp':
                     {'source': {'class': 'genie.tests.harness.script.triggers.TriggerShutNoShutBgp'},
                      'name': 'trigger', 'banana': 'yellow',
                      'groups': ['L2'],
                      'devices': ['PE1'],
                      },
                 'TriggerShutNoShutOspf':
                     {'source': {'class': 'genie.tests.harness.script.triggers.TriggerShutNoShutOspf'},
                      'groups': ['L2'],
                      'name': 'test', 'var1': 'value',
                      'devices': ['PE1'],
                      },
                 'order': ['TriggerShutNoShutBgp', 'TriggerShutNoShutOspf'],
                 }

    trigger_local1 = {'TriggerShutNoShutBgp':
                          {'source': {'class': 'genie.tests.harness.script.triggers.TriggerShutNoShutBgp'},
                           'name': 'trigger', 'banana': 'yellow',
                           'groups': ['L2'],
                           'devices': ['PE1'],
                           'verifications': {'a_callable_always_same': {'devices': ['PE1']},
                                             'a_callable': {'devices': ['PE1']}}
                           },
                      'TriggerShutNoShutOspf':
                          {'source': {'class': 'genie.tests.harness.script.triggers.TriggerShutNoShutOspf'},
                           'groups': ['L2'],
                           'name': 'test', 'var1': 'value',
                           'devices': ['PE1'],
                           'verifications': {'a_callable_always_same': {'devices': ['PE1']},
                                             'a_callable': {'devices': ['PE1']}},
                           },
                      'order': ['TriggerShutNoShutBgp', 'TriggerShutNoShutOspf'],
                      }

    trigger_local2 = {'TriggerShutNoShutBgp':
                          {'source': {'class': 'genie.tests.harness.script.triggers.TriggerShutNoShutBgp'},
                           'name': 'trigger', 'banana': 'yellow',
                           'groups': ['L2'],
                           'devices': ['PE1'],
                           },
                      'TriggerShutNoShutOspf':
                          {'source': {'class': 'genie.tests.harness.script.triggers.TriggerShutNoShutOspf'},
                           'groups': ['L2'],
                           'verifications': {'blabla': {'devices': ['PE1']},
                                             'a_callable': {'devices': ['PE1']}},
                           },
                      'order': ['TriggerShutNoShutBgp', 'TriggerShutNoShutOspf'],
                      }

    trig_no_loc = {'TriggerShutNoShutBgp': {'devices': ['PE1']}}

    wrong_local = {'TriggerShutNoShutBgp':
                       {'devices': ['PE1'],
                        'source': 'all.wrong'}}

    wrong_local2 = {'TriggerShutNoShutBgp':
                        {'devices': ['PE1'],
                         'source': {'class': 'all.bad'}}}

    no_device = {'TriggerShutNoShutBgp':
                     {'source': {'class': 'genie.tests.harness.script.triggers.TriggerShutNoShutBgp'}}}

    wrong_veri = {'Wrong':
                      {'source': {'class': 'genie.tests.harness.script.verifications.Wrong'},
                       'devices': ['PE1']}}

    wrong_trigger = {'Wrong':
                         {'source': {'class': 'genie.tests.harness.script.triggers.Wrong'},
                          'devices': ['PE1']}}

    triggers2 = {'TriggerShutNoShutBgp':
                     {'source': {'class': 'genie.tests.harness.script.triggers.TriggerShutNoShutBgp'},
                      'name': 'trigger', 'banana': 'yellow',
                      'groups': ['L2'],
                      'devices': ['PE1'],
                      },
                 'TriggerShutNoShutOspf':
                     {'source': {'class': 'genie.tests.harness.script.triggers.TriggerShutNoShutOspf'},
                      'groups': ['L2'],
                      'name': 'test', 'var1': 'value',
                      'devices': ['PE1'],
                      },
                 'order': ['TriggerShutNoShutOspf', 'TriggerShutNoShutBgp'],
                 }

    no_order = {'TriggerShutNoShutBgp':
                    {'source': {'class': 'genie.tests.harness.script.triggers.TriggerShutNoShutBgp'},
                     'name': 'trigger', 'banana': 'yellow',
                     'groups': ['L2'],
                     'devices': ['PE1'],
                     },
                'TriggerShutNoShutOspf':
                    {'source': {'class': 'genie.tests.harness.script.triggers.TriggerShutNoShutOspf'},
                     'groups': ['L2'],
                     'name': 'test', 'var1': 'value',
                     'devices': ['PE1'],
                     },
                }

    bad_triggers = {'Bad':
                        {'source': 'genie.tests.harness.script.triggers.Bad',
                         'extra_args': {'name': 'trigger', 'banana': 'yellow'},
                         'groups': ['L2'],
                         'devices': ['PE1'],
                         },
                    'TriggerShutNoShutOspf':
                        {'source': 'genie.tests.harness.script.triggers.TriggerShutNoShutOspf',
                         'groups': ['L2'],
                         'extra_args': {'name': 'test', 'var1': 'value'},
                         'devices': ['PE1'],
                         },
                    'order': ['TriggerShutNoShutBgp', 'TriggerShutNoShutOspf'],
                    }

    # And verifications
    veri1 = {'a_callable':
                 {'source': {'class': 'genie.tests.harness.script.verifications.a_callable'},
                  'name': 'trigger', 'var1': 'yellow',
                  'groups': ['L2'],
                  'devices': ['PE1'],
                  },
             'a_callable_always_same':
                 {'source': {'class': 'genie.tests.harness.script.verifications.a_callable_always_same'},
                  'groups': ['L2'],
                  'var1': 5,
                  'name': 'test',
                  'devices': ['PE1'],
                  },
             'order': ['a_callable', 'a_callable_always_same']
             }

    veri2 = {'a_callable':
                 {'source': {'class': 'genie.tests.harness.script.verifications.a_callable'},
                  'name': 'trigger', 'var1': 'yellow',
                  'groups': ['L2'],
                  'devices': ['PE1'],
                  },
             'a_callable_always_same':
                 {'source': {'class': 'genie.tests.harness.script.verifications.a_callable_always_same'},
                  'groups': ['L2'],
                  'name': 'test',
                  'var1': 5,
                  'devices': ['PE1'],
                  },
             'order': ['a_callable_always_same', 'a_callable']
             }

    veri_no_order = {'a_callable':
                         {'source': {'class': 'genie.tests.harness.script.verifications.a_callable'},
                          'name': 'trigger', 'var1': 'yellow',
                          'groups': ['L2'],
                          'devices': ['PE1'],
                          },
                     'a_callable_always_same':
                         {'source': {'class': 'genie.tests.harness.script.verifications.a_callable_always_same'},
                          'groups': ['L2'],
                          'name': 'test',
                          'var1': 5,
                          'devices': ['PE1'],
                          },
                     }

    bad_veri = {'Bad':
                    {'source': {'class': 'genie.tests.harness.script.verifications.bad'},
                     'extra_args': {'name': 'trigger', 'banana': 'yellow'},
                     'groups': ['L2']
                     }}

    veri_no_loc = {'VerifyUp': {}}
    veri_ops = {'VerifyOpsName':
                    {'source': {'class': 'genie.tests.harness.script.verifications.VerifyOps'},
                     'some_args': 'trigger', 'var1': 'yellow',
                     'groups': ['L2'],
                     'devices': ['PE1'],
                     },
                'a_callable_always_same':
                    {'source': {'class': 'genie.tests.harness.script.verifications.a_callable_always_same'},
                     'groups': ['L2'],
                     'name': 'test',
                     'var1': 5,
                     'devices': ['PE1'],
                     },
                }

    triggers3 = {'TriggerBgpNoSetupCleanup':
                     {'source': {'class': 'genie.tests.harness.script.triggers.TriggerBgpNoSetupCleanup'},
                      'name': 'NoSetupCleanup', 'banana': 'yellow',
                      'groups': ['L2'],
                      'devices': ['PE1'],
                      'verifications': {'a_callable_always_same': {'devices': ['PE1']},
                                        'a_callable': {'devices': ['PE1']}},
                      },
                 'TriggerOspfWtSetupCleanup':
                     {'source': {'class': 'genie.tests.harness.script.triggers.TriggerOspfWtSetupCleanup'},
                      'groups': ['L2'],
                      'name': 'WtSetupCleanup', 'var1': 'value',
                      'devices': ['PE1'],
                      'verifications': {'a_callable_always_same': {'devices': ['PE1']},
                                        'a_callable': {'devices': ['PE1']}},
                      },
                 'TriggerHsrpWtSetup':
                     {'source': {'class': 'genie.tests.harness.script.triggers.TriggerHsrpWtSetup'},
                      'name': 'WtSetup', 'banana': 'yellow',
                      'groups': ['L2'],
                      'devices': ['PE1'],
                      'verifications': {'a_callable_always_same': {'devices': ['PE1']},
                                        'a_callable': {'devices': ['PE1']}},
                      },
                 'TriggerVlanWtCleanup':
                     {'source': {'class': 'genie.tests.harness.script.triggers.TriggerVlanWtCleanup'},
                      'groups': ['L2'],
                      'name': 'WtCleanup', 'var1': 'value',
                      'devices': ['PE1'],
                      'verifications': {'a_callable_always_same': {'devices': ['PE1']},
                                        'a_callable': {'devices': ['PE1']}},
                      },
                 'TriggerIsisBasic':
                     {'source': {'class': 'genie.tests.harness.script.triggers.TriggerIsisBasic'},
                      'name': 'Basic', 'banana': 'yellow',
                      'groups': ['L2'],
                      'devices': ['PE1'],
                      },
                 'TriggerWtJustSetupCleanup':
                     {'source': {'class': 'genie.tests.harness.script.triggers.TriggerWtJustSetupCleanup'},
                      'name': 'Basic', 'banana': 'yellow',
                      'groups': ['L2'],
                      'devices': ['PE1'],
                      'verifications': {'a_callable_always_same': {'devices': ['PE1']},
                                        'a_callable': {'devices': ['PE1']}},
                      },
                 'TriggerMixedOrder':
                     {'source': {'class': 'genie.tests.harness.script.triggers.TriggerMixedOrder'},
                      'name': 'Basic', 'banana': 'yellow',
                      'groups': ['L2'],
                      'devices': ['PE1'],
                      'verifications': {'a_callable_always_same': {'devices': ['PE1']},
                                        'a_callable': {'devices': ['PE1']}},
                      },
                 'TriggerNoDecorator':
                     {'source': {'class': 'genie.tests.harness.script.triggers.TriggerNoDecorator'},
                      'name': 'Basic', 'banana': 'yellow',
                      'groups': ['L2'],
                      'devices': ['PE1'],
                      'verifications': {'a_callable_always_same': {'devices': ['PE1']},
                                        'a_callable': {'devices': ['PE1']}},
                      },
                 'order': ['TriggerIsisBasic', 'TriggerBgpNoSetupCleanup',
                           'TriggerHsrpWtSetup', 'TriggerVlanWtCleanup',
                           'TriggerOspfWtSetupCleanup',
                           'TriggerWtJustSetupCleanup', 'TriggerMixedOrder',
                           'TriggerNoDecorator', ],
                 }
    subsections1 = {
        'setup':
            {'sections':
                 {'paramed_subsection':
                      {'method': 'genie.tests.harness.script.subsections.with_param',
                       'parameters':
                           {'param1': 'a', 'param2': 'b'}},
                  'no_paramed_subsection':
                      {'method': 'genie.tests.harness.script.subsections.without_param', }},
             'order': ['no_paramed_subsection', 'paramed_subsection', ]},
        'cleanup':
            {'sections':
                 {'with_param':
                      {'method': 'genie.tests.harness.script.subsections.with_param', },
                  'without_param':
                      {'method': 'genie.tests.harness.script.subsections.without_param', }},
             'order': ['without_param', 'with_param']},
    }

    subsections2 = {
        'setup':
            {'sections':
                 {'paramed_subsection':
                      {'method': 'genie.tests.harness.script.subsections.with_param',
                       'parameters':
                           {'param1': 'a', 'param2': 'b'},
                       'processors': {
                           'pre': {'a_processor': {
                               'method': 'genie.tests.harness.script.triggers.prepostprocessor'},
                               'b_processor': {
                                   'method': 'genie.tests.harness.script.triggers.processorwithparam',
                                   'parameters': {'param1': 'lalala'}},
                               'c_processor': {
                                   'method': 'genie.tests.harness.script.triggers.exceptionprocessor'},
                               'order': ['c_processor', 'a_processor']}},
                       },
                  'no_paramed_subsection':
                      {'method': 'genie.tests.harness.script.subsections.without_param', }},
             'order': ['no_paramed_subsection', 'paramed_subsection', ]},
        'cleanup':
            {'sections':
                 {'with_param':
                      {'method': 'genie.tests.harness.script.subsections.cleanup_with_param',
                       'processors': {
                           'pre': {'a_processor': {
                               'method': 'genie.tests.harness.script.triggers.prepostprocessor'},
                               'b_processor': {
                                   'method': 'genie.tests.harness.script.triggers.processorwithparam',
                                   'parameters': {'param1': 'lalala'}},
                               'c_processor': {
                                   'method': 'genie.tests.harness.script.triggers.exceptionprocessor'},
                               'order': ['c_processor', 'a_processor']}},
                       },
                  'without_param':
                      {'method': 'genie.tests.harness.script.subsections.cleanup_without_param', }},
             'order': ['without_param', 'with_param']},
    }

    subsections3 = {
        'setup':
            {'sections':
                 {'check_config':
                      {'method': 'genie.tests.harness.script.subsections.with_param',
                       'parameters':
                           {'param1': 'a', 'param2': 'b'}}}},
        'cleanup':
            {'sections':
                 {'check_post_config':
                      {'method': 'genie.harness.commons.check_post_config', }}}
    }

    subsections4 = {
        'setup':
            {'sections':
                 {'check_config':
                      {'method': 'invalid.with_param',
                       'parameters':
                           {'param1': 'a', 'param2': 'b'}}},
             'order': ['check_config'],
        },
        'cleanup':
            {'sections':
                 {'check_post_config':
                      {'method': 'invalid.check_post_config', }},
            'order': ['check_post_config']
        },
    }

    triggers4 = {'TriggerBgpNoSetupCleanup':
                     {'source': {'class': 'genie.tests.harness.script.triggers.TriggerBgpNoSetupCleanup'},
                      'name': 'NoSetupCleanup', 'banana': 'yellow',
                      'groups': ['L2'],
                      'devices': ['PE1'],
                      'verifications': {'callable_verification': {'devices': ['PE1'],
                                                                  'parameters': {'missing': 'None'}},
                                        'VerifyOpsParameters': {'devices': ['PE1'],
                                                                'parameters': {'missing': 'None'}}},
                      },
                 }

    triggers5 = {'TriggerBgpNoSetupCleanup':
                     {'source': {'class': 'genie.tests.harness.script.triggers.TriggerBgpNoSetupCleanup'},
                      'name': 'NoSetupCleanup', 'banana': 'yellow',
                      'groups': ['L2'],
                      'devices': ['PE1'],
                      'processors': {
                          'pre': {'a_processor': {
                              'method': 'genie.tests.harness.script.triggers.prepostprocessor'}},
                          'post': {'b_processor': {
                              'method': 'genie.tests.harness.script.triggers.processorwithparam',
                              'parameters': {'param1': 'abc'}}},
                          'exception': {'c_processor': {
                              'method': 'genie.tests.harness.script.triggers.exceptionprocessor'}},
                      },
                      'verifications': {'callable_verification': {'devices': ['PE1'],
                                                                  'parameters': {'missing': 'None'}},
                                        'VerifyOpsParameters': {'devices': ['PE1'],
                                                                'parameters': {'missing': 'None'}}},
                      },
                 }

    veri5 = {'a_callable':
                 {'source': {'class': 'genie.tests.harness.script.verifications.a_callable'},
                  'name': 'trigger', 'var1': 'yellow',
                  'groups': ['L2'],
                  'devices': ['PE1'],
                  'processors': {
                      'pre': {'a_processor': {
                          'method': 'genie.tests.harness.script.triggers.prepostprocessor'}},
                      'post': {'b_processor': {
                          'method': 'genie.tests.harness.script.triggers.processorwithparam',
                          'parameters': {'param1': 'abc'}}},
                      'exception': {'c_processor': {
                          'method': 'genie.tests.harness.script.triggers.exceptionprocessor'}},
                  },
                  },
             }

    triggers6 = {'TriggerIsisBasic': {
        'source': {
            'class': 'genie.tests.harness.script.triggers.TriggerBgpNoSetupCleanup'},
        'name': 'NoSetupCleanup', 'banana': 'yellow',
        'groups': ['L2'],
        'devices': ['PE1'],
        'processors': {
            'pre': {'a_processor': {
                'method': 'genie.tests.harness.script.triggers.prepostprocessor'},
                'b_processor': {
                    'method': 'genie.tests.harness.script.triggers.processorwithparam',
                    'parameters': {'param1': 'lalala'}},
                'c_processor': {
                    'method': 'genie.tests.harness.script.triggers.exceptionprocessor'},
                'order': ['c_processor', 'a_processor']},
        }
    },
    }

    triggers7 = {'TriggerBgpNoSetupCleanup':
                     {'source': {'class': 'genie.tests.harness.script.triggers.TriggerBgpNoSetupCleanup'},
                      'name': 'NoSetupCleanup', 'banana': 'yellow',
                      'groups': ['L2'],
                      'devices': ['PE1'],
                      'processors': {
                          'pre': {'a_processor': {
                              'method': 'genie.tests.harness.script.triggers.prepostprocessor'}},
                          'post': {'b_processor': {
                              'method': 'genie.tests.harness.script.triggers.processorwithparam',
                              'parameters': {'param1': 'abc'}},
                              'd_processor': {
                                  'method': 'genie.tests.harness.script.triggers.processorwithparam',
                                  'parameters': {'param1': '123'}}},
                          'exception': {'c_processor': {
                              'method': 'genie.tests.harness.script.triggers.exceptionprocessor'}},
                      },
                      'verifications': {'callable_verification': {'devices': ['PE1'],
                                                                  'parameters': {'missing': 'None'}},
                                        'VerifyOpsParameters': {'devices': ['PE1'],
                                                                'parameters': {'missing': 'None'}}},
                      },
                 }

    triggers_with_processor = {'TriggerBgpNoSetupCleanup':
                                   {'source': {'class': 'genie.tests.harness.script.triggers.TriggerBgpNoSetupCleanup'},
                                    'name': 'NoSetupCleanup', 'banana': 'yellow',
                                    'groups': ['L2'],
                                    'devices': ['PE1'],
                                    'processors': {
                                        'pre': {'a_processor': {
                                            'method': 'genie.tests.harness.script.triggers.prepostprocessor',
                                            'parameters': {'parama': 'locala'}}},
                                        'post': {'b_processor': {
                                            'method': 'genie.tests.harness.script.triggers.processorwithparam',
                                            'parameters': {'paramb': ['uut']}},
                                            'c_processor': {
                                                'method': 'genie.tests.harness.script.triggers.processorwithparam',
                                                'parameters': {'paramc': 1}},
                                            'order': ['c_processor', 'b_processor']},
                                    },
                                    },
                               }

    triggers_without_processor = {'TriggerBgpNoSetupCleanup':
                                      {'source': {
                                          'class': 'genie.tests.harness.script.triggers.TriggerBgpNoSetupCleanup'},
                                       'name': 'NoSetupCleanup', 'banana': 'yellow',
                                       'groups': ['L2'],
                                       'devices': ['PE1'],
                                       },
                                  }

    global_processor = {'global_processors': {
        'pre': {'a_processor': {
            'method': 'genie.tests.harness.script.triggers.prepostprocessor',
            'parameters': {'parama': 'globala'}}},
        'post': {'b_processor': {
            'method': 'genie.tests.harness.script.triggers.processorwithparam',
            'parameters': {'paramb': ['uut', 'P1']}},
            'c_processor': {
                'method': 'genie.tests.harness.script.triggers.processorwithparam',
                'parameters': {'paramc': 'globalc'}},
            'd_processor': {
                'method': 'genie.tests.harness.script.triggers.processorwithparam',
                'parameters': {'paramd': 2}},
            'order': ['b_processor', 'd_processor', 'c_processor']},
    },
    }

    triggers_for_global_local_processor = {
        'TriggerBgpNoSetupCleanup': {
            'source': {'class': 'genie.tests.harness.script.triggers.TriggerBgpNoSetupCleanup'},
            'name': 'NoSetupCleanup', 'banana': 'yellow',
            'groups': ['L2'],
            'devices': ['PE1'],
            'processors': {
                'post': {'b_processor': {
                    'method': 'genie.tests.harness.script.triggers.processorwithparam',
                    'parameters': {'paramb': ['uut']}},
                    'c_processor': {
                        'method': 'genie.tests.harness.script.triggers.processorwithparam',
                        'parameters': {'paramc': 1}},
                    'order': ['c_processor', 'b_processor']},
            },
        },
        'TriggerOspfWtSetupCleanup': {
            'source': {'class': 'genie.tests.harness.script.triggers.TriggerOspfWtSetupCleanup'},
            'name': 'WtSetupCleanup', 'var1': 'value',
            'groups': ['L2'],
            'devices': ['PE1'],
            'processors': {
                'post': {'b_processor': {
                    'method': 'genie.tests.harness.script.triggers.processorwithparam',
                    'parameters': {'paramb2': ['P1']}},
                    'c_processor': {
                        'method': 'genie.tests.harness.script.triggers.processorwithparam',
                        'parameters': {'paramc': 2}},
                    'order': ['b_processor', 'c_processor']},
            },
        },
        'global_processors': {
            'post': {'b_processor': {
                'method': 'genie.tests.harness.script.triggers.processorwithparam',
                'parameters': {'paramb': ['uut', 'P1']}},
                'c_processor': {
                    'method': 'genie.tests.harness.script.triggers.processorwithparam',
                    'parameters': {'paramc': 'globalc'}},
                'd_processor': {
                    'method': 'genie.tests.harness.script.triggers.processorwithparam',
                    'parameters': {'paramd': 2}},
                'order': ['b_processor', 'd_processor', 'c_processor']
            },
        },
    }

    triggers8 = {'TriggerShutNoShutBgp':
                     {'source': {'class': 'genie.tests.harness.script.triggers.TriggerShutNoShutBgp'},
                      'name': 'trigger', 'banana': 'yellow',
                      'groups': ['bgp'],
                      'devices': ['PE1'],
                      },
                 'TriggerShutNoShutOspf':
                     {'source': {'class': 'genie.tests.harness.script.triggers.TriggerShutNoShutOspf'},
                      'groups': ['ospf'],
                      'name': 'test', 'var1': 'value',
                      'devices': ['PE1'],
                      },
                 'order': ['TriggerShutNoShutBgp', 'TriggerShutNoShutOspf'],
                 }

    triggers_with_sections = {
        'TriggerShutNoShutOspf': {
            'source': {
                'class':
                'genie.tests.harness.script.triggers.TriggerShutNoShutOspf'
            },
            'groups': ['L2'],
            'devices': ['PE1'],
            'sections': {
                'test1': {
                    'processors': {
                        'pre': {
                            'a_processor': {
                                'method':
                                'genie.tests.harness.script.triggers.prepostprocessor',
                                'parameters': {
                                    'parama': 'locala'
                                }
                            }
                        },
                        'post': {
                            'b_processor': {
                                'method':
                                'genie.tests.harness.script.triggers.processorwithparam',
                                'parameters': {
                                    'paramb': ['uut']
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    triggers_with_section_parameters = {
            'TriggerSectionWithParameters': {
                'source': {
                    'class':'genie.tests.harness.script.triggers.TriggerSectionWithParameters'
                },
                'groups': ['L2'],
                'devices': ['PE1'],
                'val': 'This should be overridden',
                'val2': 'This should also be overridden',
                'sections': {
                    'test': {
                        'parameters': {
                            'val': 'This should override',
                        },
                    'test3': {
                        'parameters': {
                            'val2': 'This should override',
                        },
                    },
                },
            },
        }
    }

    triggers_external_override = {
        'TriggerSleep': {
            'source': {
                'pkg': 'genie.libs.sdk',
                'class':'triggers.sleep.sleep.TriggerSleep'
            },
            'devices': ['PE1']
        },
        'DummyTrigger': {
            'source': {
                'pkg': 'genie.libs.sdk',
                'class':'triggers.dummy_trigger.dummy_trigger.DummyTrigger'
            },
            'devices': ['PE1']
        }
    }

    trigger_aetest_loop_params  = {
                    'TriggerAetestLoopParams':
                        {'source': {'class': 'genie.tests.harness.script.triggers.TriggerAetestLoopParams'},
                         'groups': ['L2'],
                         'devices': ['PE1'],
                         },
                    'order': ['TriggerAetestLoopParams'],
                 }

    trigger_sleep = {
        'TriggerSleep': {
            'source': {
                'pkg': 'genie.libs.sdk',
                'class':'triggers.sleep.sleep.TriggerSleep'
            },
            'groups': ['L2'],
            'devices': ['PE1'],
        }
    }

    triggers_order_dict = {
        'extends': [],
        'variables': {},
        'parameters': {},
        'uids': [],
        'groups': [],
        'global_processors': {},
        'TriggerShutNoShutBgp': {
            'source': {
                'class': 'genie.tests.harness.script.triggers.TriggerShutNoShutBgp'
            },
            'name': 'trigger',
            'banana': 'yellow',
            'groups': ['L2'],
            'devices': ['PE1'],
        },
        'TriggerShutNoShutOspf': {
            'source': {
                'class': 'genie.tests.harness.script.triggers.TriggerShutNoShutOspf'
            },
            'groups': ['L2'],
            'name': 'test',
            'var1': 'value',
            'devices': ['PE1'],
        },
        'order': [{
            'TriggerShutNoShutBgp': {
                'devices': ['PE2']
            }
        }, {
            'TriggerShutNoShutOspf': {
                'devices': ['PE2']
            }
        }],
    }

    triggers_order_dict_multiple = {
        'TriggerShutNoShutBgp': {
            'source': {
                'class': 'genie.tests.harness.script.triggers.TriggerShutNoShutBgp'
            },
            'name': 'trigger',
            'banana': 'yellow',
            'groups': ['L2'],
            'devices': ['PE1'],
        },
        'order': [{
            'TriggerShutNoShutBgp': {
                'devices': ['PE2']
            }
        },
        'TriggerShutNoShutBgp'],
    }

    # parallel verifications
    parallel_verf = {
        'Verify_1': {
            'source': {'class': 'genie.tests.harness.script.verifications.a_callable_always_same'},
            'exclude': [],
            'devices': ['PE1', 'PE2'],
            'groups': ['L2'],
            'parallel_verifications': True
        },
        'Verify_2': {
            'source': {'class': 'genie.tests.harness.script.verifications.a_callable_always_same'},
            'exclude': [],
            'devices': ['PE1', 'PE2'],
            'groups': ['L2'],
            'parallel_verifications': True
        },
    }

    @classmethod
    def setUpClass(cls):
        # To be modified if the genie testscript ever move
        cls.testbed = Testbed()

        cls.dev1 = Device(testbed=cls.testbed, name='PE1', os='iosxr')
        cls.dev1.custom = {'abstraction': {'order': ['os'], 'context': 'yang'}}
        cls.dev2 = Device(testbed=cls.testbed, name='PE2', os='iosxr')
        cls.dev2.custom = {'abstraction': {'order': ['os'], 'context': 'yang'}}
        cls.test_module = importlib.import_module('genie.harness.genie_testscript')

    def setUp(self):
        self.script = TestScript(self.test_module)
        self.script.parameters['testbed'] = self.testbed
        self.script.mapping_data = {
            'devices': {'PE1': {'context': 'cli', 'mapping': {'cli': 'vty'}, 'label': 'helper'}}}
        self.discoverer = GenieScriptDiscover(self.script)
        # Default datafile outputs for trigger and verification
        self.script.triggers = {}
        self.script.verifications = {}
        runtime.discoverer.testcase = GenieTestcasesDiscover
        aetest.CommonSetup.discoverer = GenieCommonSetupDiscover
        aetest.CommonCleanup.discoverer = GenieCommonCleanupDiscover
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')

    # So far,  that's all to test.
    # They got nothing else!
    def test_init(self):
        self.assertEqual(self.discoverer.target, self.script)
        self.assertEqual(self.discoverer.target.module, self.script.module)

    def test_load(self):
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        for expected, item in zip([CommonSetup, items[1], CommonCleanup], items):
            try:
                self.assertTrue(isinstance(item, expected))
            except TypeError:
                pass

        # Check what is inside each items
        # In expected order
        uid_expected = ['no_paramed_subsection', 'paramed_subsection']
        for subsection, uid in zip(items[0], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

        uid_expected = ['without_param', 'with_param']
        for subsection, uid in zip(items[1], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

    def test_triggers(self):
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        # Add triggers information to the script
        self.script.triggers = self.triggers1
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)
        for expected, item in zip([CommonSetup, TriggerShutNoShutBgp,
                                   TriggerShutNoShutOspf, CommonCleanup],
                                  items):
            self.assertTrue(isinstance(item, expected))
        uid_expected = ['no_paramed_subsection', 'paramed_subsection']
        for subsection, uid in zip(items[0], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))
        # Verify extra_args and groups
        tc = items[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'TriggerShutNoShutBgp.PE1')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['banana'], 'yellow')
        uid_expected = ['test1']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))
            # Finally, can you just call it
            subsection()
        # Verify extra_args and groups
        tc = items[2]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'TriggerShutNoShutOspf.PE1')
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['var1'], 'value')
        uid_expected = ['test1', 'test2']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))
            # Finally, can you just call it
            subsection()
        uid_expected = ['without_param', 'with_param']
        for subsection, uid in zip(items[3], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

    def test_triggers_with_sections(self):
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        # Add triggers information to the script
        self.script.triggers = self.triggers_with_sections
        items = list(self.discoverer)
        for expected, item in zip(
            [CommonSetup, TriggerShutNoShutOspf, CommonCleanup], items):
            self.assertTrue(isinstance(item, expected))
        out_test1_pre_processors, out_test1_post_processors, out_test1_exceptions = _load_processors(
            items[1].parameters['sections']['test1'], items[1])
        test1_pre_processors = items[1].parameters['sections']['test1'][
            'processors'].get('pre', [])
        test1_post_processors = items[1].parameters['sections']['test1'][
            'processors'].get('post', [])
        expect_test1_pre_processors = {'parama': 'locala'}
        expect_test1_post_processors = {'paramb': ['uut']}
        self.assertIn('a_processor', test1_pre_processors)
        self.assertNotIn('a_processor', test1_post_processors)
        self.assertEqual(out_test1_pre_processors[0].keywords,
                         expect_test1_pre_processors)
        self.assertIn('b_processor', test1_post_processors)
        self.assertNotIn('b_processor', test1_pre_processors)
        self.assertEqual(out_test1_post_processors[0].keywords,
                         expect_test1_post_processors)
        with self.assertRaises(IndexError):
            _ = out_test1_exceptions[0]
        with self.assertRaises(KeyError):
            _, _, _ = _load_processors(
                items[1].parameters['sections']['test2'], items[1])

    def test_triggers_both_uids_and_groups(self):
        self.script.trigger_uids = And('TriggerShutNoShutBgp')
        self.script.trigger_groups = Or('bgp', 'ospf')
        # Add triggers information to the script
        self.script.triggers = self.triggers8
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)
        for expected, item in zip(
            [CommonSetup, TriggerShutNoShutBgp, CommonCleanup], items):
            self.assertTrue(isinstance(item, expected))

    # Test the situation where a user explicitly specifies a trigger-uid that
    # doesn't exist in the trigger datafile. Raise an error to let the user know
    # something went wrong but ensure that CommonCleanup is still executed
    # Note: this does NOT apply when using logic operators like And() or Or()
    def test_triggers_non_existant_uid(self):
        self.script.trigger_uids = ["TriggerDoesntExist"]
        # Add triggers information to the script
        self.script.triggers = self.triggers8
        self.script.subsection_data = self.subsections1
        items = []
        with self.assertRaises(ValueError) as e:
            items = items.extend(self.discoverer)

        for expected, item in zip(
            [CommonSetup, CommonCleanup], items):
            self.assertTrue(isinstance(item, expected))

    def test_triggers_only_uids(self):
        self.script.trigger_uids = And('TriggerShutNoShutBgp')
        self.script.trigger_groups = None
        # Add triggers information to the script
        self.script.triggers = self.triggers8
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)
        for expected, item in zip(
            [CommonSetup, TriggerShutNoShutBgp, CommonCleanup], items):
            self.assertTrue(isinstance(item, expected))

    def test_triggers_only_groups(self):
        self.script.trigger_uids = None
        self.script.trigger_groups = And('ospf')
        # Add triggers information to the script
        self.script.triggers = self.triggers8
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        for expected, item in zip(
            [CommonSetup, TriggerShutNoShutOspf, CommonCleanup], items):
            self.assertTrue(isinstance(item, expected))

    def test_triggers_both_uids_list_and_groups(self):
        self.script.trigger_uids = ['TriggerShutNoShutBgp']
        self.script.trigger_groups = Or('ospf', 'bgp')
        # Add triggers information to the script
        self.script.triggers = self.triggers8
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)
        for expected, item in zip(
            [CommonSetup, TriggerShutNoShutBgp, CommonCleanup], items):
            self.assertTrue(isinstance(item, expected))

    def test_triggers_no_uids_and_groups(self):
        self.script.trigger_uids = None
        self.script.trigger_groups = None
        # Add triggers information to the script
        self.script.triggers = self.triggers8
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        for expected, item in zip(
            [CommonSetup, items[1], CommonCleanup], items):
            try:
                self.assertTrue(isinstance(item, expected))
            except TypeError:
                pass

    def test_triggers_parameters_data_variables(self):
        self.script.trigger_uids = Or('')
        self.script.trigger_groups = None
        # Add triggers information to the script
        self.script.triggers = self.triggers1
        self.script.triggers['data'] = {'some_key': 'some_value'}
        self.script.triggers['parameters'] = {'some_key': 'some_value'}
        self.script.triggers['variables'] = {'some_key': 'some_value'}
        items = list(self.discoverer)
        for expected, item in zip([CommonSetup, TriggerShutNoShutBgp,
                                   TriggerShutNoShutOspf, CommonCleanup],
                                  items):
            self.assertTrue(isinstance(item, expected))
        for item in items:
            self.assertNotIn(item.__uid__, ['data', 'parameters', 'variables'])

    def test_triggers_order(self):
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        # Add triggers information to the script
        self.script.triggers = self.triggers2
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)
        for expected, item in zip([CommonSetup, TriggerShutNoShutOspf,
                                   TriggerShutNoShutBgp, CommonCleanup],
                                  items):
            self.assertTrue(isinstance(item, expected))
        uid_expected = ['no_paramed_subsection', 'paramed_subsection']
        for subsection, uid in zip(items[0], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))
        # Verify extra_args and groups
        tc = items[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'TriggerShutNoShutOspf.PE1')
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['var1'], 'value')
        uid_expected = ['test1']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))
            # Finally, can you just call it
            subsection()
        # Verify extra_args and groups
        tc = items[2]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'TriggerShutNoShutBgp.PE1')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['banana'], 'yellow')
        uid_expected = ['test1', 'test2']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))
            # Finally, can you just call it
            subsection()
        uid_expected = ['without_param', 'with_param']
        for subsection, uid in zip(items[3], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

    def test_triggers_no_order(self):
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        # Add triggers information to the script
        self.script.triggers = self.no_order
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)
        for expected, item in zip([CommonSetup, TriggerShutNoShutBgp,
                                   TriggerShutNoShutOspf, CommonCleanup],
                                  items):
            self.assertTrue(isinstance(item, expected))
        uid_expected = ['no_paramed_subsection', 'paramed_subsection']
        for subsection, uid in zip(items[0], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))
        # Verify extra_args and groups
        tc = items[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'TriggerShutNoShutBgp.PE1')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['banana'], 'yellow')
        uid_expected = ['test1']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))
            # Finally, can you just call it
            subsection()
        # Verify extra_args and groups
        tc = items[2]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'TriggerShutNoShutOspf.PE1')
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['var1'], 'value')
        uid_expected = ['test1', 'test2']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))
            # Finally, can you just call it
            subsection()
        uid_expected = ['without_param', 'with_param']
        for subsection, uid in zip(items[3], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

    def test_invalid_triggers(self):
        # Add triggers information to the script
        self.script.triggers = self.bad_triggers
        with self.assertRaises(ValueError):
            loaded = self.discoverer._load_item('Bad',
                                                self.bad_triggers,
                                                verification=False,
                                                counter=0)
        with self.assertRaises(Exception):
            self.script.subsection_data = self.subsections1
            items = list(self.discoverer)

    def test_invalid_verification_class(self):
        # Add triggers information to the script
        self.script.verifications = self.wrong_veri
        with self.assertRaises(TypeError):
            loaded = self.discoverer._load_item('Wrong',
                                                self.wrong_veri,
                                                verification=True,
                                                counter=0)
        with self.assertRaises(Exception):
            self.script.subsection_data = self.subsections1
            items = list(self.discoverer)

    def test_invalid_trigger_class(self):
        # Add triggers information to the script
        self.script.triggers = self.wrong_trigger
        with self.assertRaises(TypeError):
            loaded = self.discoverer._load_item('Wrong',
                                                self.wrong_trigger,
                                                verification=False,
                                                counter=0)
        with self.assertRaises(Exception):
            self.script.subsection_data = self.subsections1
            items = list(self.discoverer)

    def test_no_loc_triggers(self):
        # Add triggers information to the script
        self.script.triggers = self.trig_no_loc
        with self.assertRaises(ValueError):
            loaded = self.discoverer._load_item('TriggerShutNoShutBgp',
                                                self.trig_no_loc,
                                                verification=False,
                                                counter=0)
        with self.assertRaises(Exception):
            self.script.subsection_data = self.subsections1
            items = list(self.discoverer)

    def test_zzzzzno_device(self):
        # Add triggers information to the script
        self.script.triggers = self.no_device
        loaded = self.discoverer._load_item('TriggerShutNoShutBgp',
                                            self.no_device,
                                            verification=False,
                                            counter=0)

        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        self.assertEqual(len(items), 3)

    def test_wrong_source_triggers(self):
        # Add triggers information to the script
        self.script.triggers = self.wrong_local
        with self.assertRaises(ValueError):
            loaded = self.discoverer._load_item('TriggerShutNoShutBgp',
                                                self.wrong_local,
                                                verification=False,
                                                counter=0)
        with self.assertRaises(Exception):
            self.script.subsection_data = self.subsections1
            items = list(self.discoverer)

    def test_wrong_source_triggers2(self):
        # Add triggers information to the script
        self.script.triggers = self.wrong_local2
        with self.assertRaises(ModuleNotFoundError):
            loaded = self.discoverer._load_item('TriggerShutNoShutBgp',
                                                self.wrong_local2,
                                                verification=False,
                                                counter=0)
        with self.assertRaises(Exception):
            self.script.subsection_data = self.subsections1
            items = list(self.discoverer)

    def test_wrong_device(self):
        # Add triggers information to the script
        self.script.triggers = copy.deepcopy(self.trigger_local1)
        self.script.triggers['TriggerShutNoShutBgp']['devices'].append('PE3')

        loaded = self.discoverer._load_item('TriggerShutNoShutBgp',
                                            self.script.triggers,
                                            verification=False,
                                            counter=0)

        assert any(isinstance(x, TriggerDeviceNotFound) for x in loaded)

    def test_repeat_order(self):
        # Add triggers information to the script
        self.script.verifications = copy.deepcopy(self.veri1)
        self.script.verifications['order'].append('a_callable')
        loaded = self.discoverer._load_item('a_callable',
                                            self.script.verifications,
                                            verification=True,
                                            counter=0)

        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        self.assertEqual(items[1].verifiers[0].uid, 'a_callable.PE1.1')
        self.assertEqual(items[1].verifiers[1].uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(items[1].verifiers[2].uid, 'a_callable.PE1.2')

    def test_order_wrong_name(self):
        # Add triggers information to the script
        self.script.verifications = copy.deepcopy(self.veri1)
        self.script.verifications['order'].append('no_exists')
        self.script.verification_uids = ['no_exists']
        loaded = self.discoverer._load_item('a_callable',
                                            self.script.verifications,
                                            verification=True,
                                            counter=0)

        with self.assertRaises(ValueError):
            self.script.subsection_data = self.subsections1
            items = list(self.discoverer)

    def test_verifications(self):
        # Add triggers information to the script
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.verifications = self.veri1
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        for expected, item in zip([CommonSetup, items[1],
                                   CommonCleanup], items):

            try:
                self.assertTrue(isinstance(item, expected))
            except TypeError:
                # Ignore those for now,  callables verifications
                pass

        self.assertEqual(items[1].uid, 'Verifications.post')
        self.assertEqual(items[1].verifiers[0].uid, 'a_callable.PE1.1')
        self.assertEqual(items[1].verifiers[1].uid, 'a_callable_always_same.PE1.1')

        uid_expected = ['no_paramed_subsection', 'paramed_subsection']
        for subsection, uid in zip(items[0], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

        # Verify extra_args and groups

        tc = items[1].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable.PE1.1')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[1].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        uid_expected = ['without_param', 'with_param']
        for subsection, uid in zip(items[2], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

    def test_verifications_order(self):
        # Add triggers information to the script
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.verifications = self.veri2
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)
        
        for expected, item in zip([CommonSetup, items[1],
                                   CommonCleanup], items):

            try:
                self.assertTrue(isinstance(item, expected))
            except TypeError:
                # Ignore those for now,  callables verifications
                pass

        self.assertEqual(items[1].uid, 'Verifications.post')
        self.assertEqual(items[1].verifiers[0].uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(items[1].verifiers[1].uid, 'a_callable.PE1.1')

        uid_expected = ['no_paramed_subsection', 'paramed_subsection']
        for subsection, uid in zip(items[0], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

        # Verify extra_args and groups

        tc = items[1].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable.PE1.1')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[1].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        uid_expected = ['without_param', 'with_param']
        for subsection, uid in zip(items[2], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

    def test_verifications_no_order(self):
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        # Add triggers information to the script
        self.script.verifications = self.veri_no_order
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        for expected, item in zip([CommonSetup, items[1],
                                   CommonCleanup], items):

            try:
                self.assertTrue(isinstance(item, expected))
            except TypeError:
                # Ignore those for now,  callables verifications
                pass

        self.assertEqual(items[1].uid, 'Verifications.post')
        self.assertEqual(items[1].verifiers[0].uid, 'a_callable.PE1.1')
        self.assertEqual(items[1].verifiers[1].uid, 'a_callable_always_same.PE1.1')

        uid_expected = ['no_paramed_subsection', 'paramed_subsection']
        for subsection, uid in zip(items[0], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

        # Verify extra_args and groups

        tc = items[1].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable.PE1.1')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[1].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        uid_expected = ['without_param', 'with_param']
        for subsection, uid in zip(items[2], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

    def test_invalid_verifications(self):
        # Add triggers information to the script
        self.script.verifications = self.bad_veri
        with self.assertRaises(AttributeError):
            items = self.discoverer.load()

    def test_no_loc_verifications(self):
        # Add triggers information to the script
        self.script.verifications = self.veri_no_loc
        with self.assertRaises(ValueError):
            loaded = self.discoverer._load_item('VerifyUp',
                                                self.veri_no_loc,
                                                verification=True,
                                                counter=0)

        with self.assertRaises(Exception):
            self.script.subsection_data = self.subsections1
            items = list(self.discoverer)

    # And now Mix triggers and verifications
    def test_triggers_verifications(self):
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        # Add triggers information to the script
        self.script.triggers = self.triggers1
        self.script.verifications = self.veri1
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        for expected, item in zip([CommonSetup, items[1],
                                   TriggerShutNoShutBgp, items[3],
                                   TriggerShutNoShutOspf, items[5],
                                   CommonCleanup], items):

            try:
                self.assertTrue(isinstance(item, expected))
            except TypeError:
                # Ignore those for now,  callables verifications
                pass

        self.assertEqual(items[1].verifiers[0].uid, 'a_callable.PE1.1')
        self.assertEqual(items[1].verifiers[1].uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(items[3].verifiers[0].uid, 'a_callable.PE1.2')
        self.assertEqual(items[3].verifiers[1].uid, 'a_callable_always_same.PE1.2')
        self.assertEqual(items[5].verifiers[0].uid, 'a_callable.PE1.3')
        self.assertEqual(items[5].verifiers[1].uid, 'a_callable_always_same.PE1.3')

        uid_expected = ['no_paramed_subsection', 'paramed_subsection']
        for subsection, uid in zip(items[0], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

        # Verify extra_args and groups

        tc = items[1].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable.PE1.1')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[1].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[2]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'TriggerShutNoShutBgp.PE1')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['banana'], 'yellow')

        uid_expected = ['test1', 'test2']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))
            # Finally, can you just call it
            subsection()

        tc = items[3].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable.PE1.2')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[3].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.2')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[4]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'TriggerShutNoShutOspf.PE1')
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['var1'], 'value')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['test1']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))
            # Finally, can you just call it
            subsection()

        tc = items[5].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable.PE1.3')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[5].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.3')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        # Verify extra_args and groups

        uid_expected = ['without_param', 'with_param']
        for subsection, uid in zip(items[6], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

    # And now Mix triggers and Ops Verifications
    def test_triggers_verifications_ops(self):
        # Add triggers information to the script
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = self.triggers1
        self.script.verifications = self.veri_ops
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        for expected, item in zip([CommonSetup, items[1],
                                   TriggerShutNoShutBgp, items[3],
                                   TriggerShutNoShutOspf, items[5],
                                   CommonCleanup], items):

            try:
                self.assertTrue(isinstance(item, expected))
            except TypeError:
                # Ignore those for now,  callables verifications
                pass

        self.assertEqual(items[1].verifiers[0].uid, 'VerifyOpsName.PE1.1')
        self.assertEqual(items[1].verifiers[1].uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(items[3].verifiers[0].uid, 'VerifyOpsName.PE1.2')
        self.assertEqual(items[3].verifiers[1].uid, 'a_callable_always_same.PE1.2')
        self.assertEqual(items[5].verifiers[0].uid, 'VerifyOpsName.PE1.3')
        self.assertEqual(items[5].verifiers[1].uid, 'a_callable_always_same.PE1.3')

        uid_expected = ['no_paramed_subsection', 'paramed_subsection']
        for subsection, uid in zip(items[0], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

        # Verify extra_args and groups

        tc = items[1].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'VerifyOpsName.PE1.1')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['some_args'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[1].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[2]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'TriggerShutNoShutBgp.PE1')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['banana'], 'yellow')

        uid_expected = ['test1', 'test2']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))
            # Finally, can you just call it
            subsection()

        tc = items[3].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'VerifyOpsName.PE1.2')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['some_args'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[3].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.2')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[4]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'TriggerShutNoShutOspf.PE1')
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['var1'], 'value')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['test1']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))
            # Finally, can you just call it
            subsection()

        tc = items[5].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'VerifyOpsName.PE1.3')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['some_args'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[5].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.3')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        # Verify extra_args and groups

        uid_expected = ['without_param', 'with_param']
        for subsection, uid in zip(items[6], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

    def test_triggers_verifications_no_order(self):
        # Add triggers information to the script
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = self.no_order
        self.script.verifications = self.veri_no_order
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        for expected, item in zip([CommonSetup, items[1],
                                   TriggerShutNoShutBgp, items[3],
                                   TriggerShutNoShutOspf, items[5],
                                   CommonCleanup], items):

            try:
                self.assertTrue(isinstance(item, expected))
            except TypeError:
                # Ignore those for now,  callables verifications
                pass

        self.assertEqual(items[1].verifiers[0].uid, 'a_callable.PE1.1')
        self.assertEqual(items[1].verifiers[1].uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(items[3].verifiers[0].uid, 'a_callable.PE1.2')
        self.assertEqual(items[3].verifiers[1].uid, 'a_callable_always_same.PE1.2')
        self.assertEqual(items[5].verifiers[0].uid, 'a_callable.PE1.3')
        self.assertEqual(items[5].verifiers[1].uid, 'a_callable_always_same.PE1.3')

        uid_expected = ['no_paramed_subsection', 'paramed_subsection']
        for subsection, uid in zip(items[0], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

        # Verify extra_args and groups

        tc = items[1].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable.PE1.1')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[1].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[2]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'TriggerShutNoShutBgp.PE1')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['banana'], 'yellow')

        uid_expected = ['test1', 'test2']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))
            # Finally, can you just call it
            subsection()

        tc = items[3].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable.PE1.2')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[3].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.2')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[4]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'TriggerShutNoShutOspf.PE1')
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['var1'], 'value')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['test1']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))
            # Finally, can you just call it
            subsection()

        tc = items[5].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable.PE1.3')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[5].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.3')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        # Verify extra_args and groups

        uid_expected = ['without_param', 'with_param']
        for subsection, uid in zip(items[6], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

    def test_invalid_triggers_verifications(self):
        # Add triggers information to the script
        self.script.verifications = self.bad_veri
        self.script.triggers = self.bad_triggers
        with self.assertRaises(AttributeError):
            items = self.discoverer.load()

    def test_no_loc_triggers_verifications(self):
        # Add triggers information to the script
        self.script.verifications = self.veri_no_loc
        self.script.triggers = self.trig_no_loc
        with self.assertRaises(KeyError):
            loaded = self.discoverer._load_item('a_callable',
                                                self.veri_no_loc,
                                                verification=True,
                                                counter=0)

        with self.assertRaises(Exception):
            self.script.subsection_data = self.subsections1
            items = list(self.discoverer)

    def test_wrong_source_triggers_verifications(self):
        # Add triggers information to the script
        self.script.triggers = self.wrong_local
        with self.assertRaises(ValueError):
            loaded = self.discoverer._load_item('TriggerShutNoShutBgp',
                                                self.wrong_local,
                                                verification=False,
                                                counter=0)
        with self.assertRaises(Exception):
            self.script.subsection_data = self.subsections1
            items = list(self.discoverer)

    def test_wrong_source_triggers_verifications2(self):
        # Add triggers information to the script
        self.script.triggers = self.wrong_local2
        with self.assertRaises(ModuleNotFoundError):
            loaded = self.discoverer._load_item('TriggerShutNoShutBgp',
                                                self.wrong_local2,
                                                verification=False,
                                                counter=0)
        with self.assertRaises(Exception):
            self.script.subsection_data = self.subsections1
            items = list(self.discoverer)

    # And now Mix triggers and verifications
    def test_triggers_verifications_local(self):

        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = self.trigger_local1
        self.script.verifications = self.veri1
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        for expected, item in zip([CommonSetup, items[1],
                                   TriggerShutNoShutBgp, items[3],
                                   TriggerShutNoShutOspf, items[5],
                                   CommonCleanup], items):

            try:
                self.assertTrue(isinstance(item, expected))
            except TypeError:
                # Ignore those for now,  callables verifications
                pass

        self.assertEqual(items[1].verifiers[0].uid, 'a_callable.PE1.1')
        self.assertEqual(items[1].verifiers[1].uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(items[3].verifiers[0].uid, 'a_callable.PE1.2')
        self.assertEqual(items[3].verifiers[1].uid, 'a_callable_always_same.PE1.2')
        self.assertEqual(items[5].verifiers[0].uid, 'a_callable.PE1.3')
        self.assertEqual(items[5].verifiers[1].uid, 'a_callable_always_same.PE1.3')

        uid_expected = ['no_paramed_subsection', 'paramed_subsection']
        for subsection, uid in zip(items[0], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

        # Verify extra_args and groups

        tc = items[1].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable.PE1.1')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[1].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[2]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'TriggerShutNoShutBgp.PE1')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['banana'], 'yellow')

        uid_expected = ['pre_a_callable.PE1',
                        'pre_a_callable_always_same.PE1',
                        'test1', 'post_a_callable.PE1',
                        'post_a_callable_always_same.PE1']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))
            # Finally, can you just call it
            if uid in ['post_a_callable.PE1']:
                with self.assertRaises(ResultSignal):
                    subsection()
            else:
                subsection()

        tc = items[3].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable.PE1.2')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[3].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.2')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[4]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'TriggerShutNoShutOspf.PE1')
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['var1'], 'value')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['pre_a_callable.PE1',
                        'pre_a_callable_always_same.PE1',
                        'test1', 'test2', 'post_a_callable.PE1',
                        'post_a_callable_always_same.PE1']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))
            # Finally, can you just call it
            if uid in ['post_a_callable.PE1']:
                with self.assertRaises(ResultSignal):
                    subsection()
            else:
                subsection()

        tc = items[5].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable.PE1.3')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[5].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.3')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        # Verify extra_args and groups

        uid_expected = ['without_param', 'with_param']
        for subsection, uid in zip(items[6], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

    # And now Mix triggers and verifications
    def test_empty_local_ver(self):

        self.script.triggers = copy.deepcopy(self.trigger_local1)
        self.script.verifications = self.veri1
        del self.script.triggers['TriggerShutNoShutBgp']['verifications']
        self.script.triggers['TriggerShutNoShutBgp']['verifications'] = None
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        for expected, item in zip([CommonSetup, items[1],
                                   TriggerShutNoShutBgp, items[3],
                                   TriggerShutNoShutOspf, items[5],
                                   CommonCleanup], items):

            try:
                self.assertTrue(isinstance(item, expected))
            except TypeError:
                # Ignore those for now,  callables verifications
                pass

        self.assertEqual(items[1].verifiers[0].uid, 'a_callable.PE1.1')
        self.assertEqual(items[1].verifiers[1].uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(items[3].verifiers[0].uid, 'a_callable.PE1.2')
        self.assertEqual(items[3].verifiers[1].uid, 'a_callable_always_same.PE1.2')
        self.assertEqual(items[5].verifiers[0].uid, 'a_callable.PE1.3')
        self.assertEqual(items[5].verifiers[1].uid, 'a_callable_always_same.PE1.3')

    # And now Mix triggers and verifications
    def test_no_verification_for_local_verf(self):

        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = copy.deepcopy(self.trigger_local1)
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        self.assertEqual(len(items), 4)
        self.assertEqual(items[1].uid, 'TriggerShutNoShutBgp.PE1')
        self.assertEqual(items[2].uid, 'TriggerShutNoShutOspf.PE1')

        with self.assertRaises(KeyError):
            items[2]()

    # And now Mix triggers and verifications
    def test_local_verf_no_device(self):

        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = copy.deepcopy(self.trigger_local1)
        self.script.triggers['TriggerShutNoShutBgp']['verifications']['a_callable_always_same'] = 'None'
        self.script.verifications = self.veri1
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        self.assertEqual(len(items), 7)
        self.assertEqual(len(list(items[2])), 3)

    # And now Mix triggers and verifications
    def test_local_verf_no_device_count_device(self):

        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = copy.deepcopy(self.trigger_local1)
        self.script.triggers['TriggerShutNoShutBgp']['verifications']['a_callable_always_same'] = 'None'
        self.script.triggers['TriggerShutNoShutBgp']['count'] = 3
        self.script.verifications = self.veri1
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        self.assertEqual(len(items), 11)
        self.assertEqual(len(list(items[2])), 3)
        self.assertEqual(len(list(items[4])), 3)
        self.assertEqual(len(list(items[6])), 3)

    # And now Mix triggers and verifications
    def test_local_verf_ops(self):

        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = copy.deepcopy(self.trigger_local1)
        self.script.triggers['TriggerShutNoShutBgp']['verifications'] \
            ['VerifyOpsName'] = {'devices_attributes': {'PE1': {'test': 5}}}
        self.script.triggers['TriggerShutNoShutBgp']['verifications']['VerifyOpsName']['devices'] = ['PE1']
        del self.script.triggers['TriggerShutNoShutBgp'] \
            ['verifications']['a_callable']

        self.script.verifications = self.veri_ops
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        self.assertEqual(len(items), 7)
        self.assertEqual(len(list(items[2])), 5)
        self.assertEqual(list(items[2])[0].parameters['test'], 5)

    # And now Mix triggers and verifications
    def test_local_verf_ops_count_local(self):

        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = copy.deepcopy(self.trigger_local1)
        self.script.triggers['TriggerShutNoShutBgp']['verifications'] \
            ['VerifyOpsName'] = {'devices_attributes': {'PE1': {}}}
        self.script.triggers['TriggerShutNoShutBgp']['verifications'] \
            ['VerifyOpsName']['devices_attributes']['PE1'] = \
            {'test': 5, 'count': 3}
        self.script.triggers['TriggerShutNoShutBgp']['verifications'] \
            ['VerifyOpsName']['devices'] = ['PE1']
        del self.script.triggers['TriggerShutNoShutBgp'] \
            ['verifications']['a_callable']

        self.script.verifications = copy.deepcopy(self.veri_ops)
        self.script.verifications['VerifyOpsName']['devices_attributes'] = \
            {'PE1': {}}

        self.script.verifications['VerifyOpsName']['devices_attributes']['PE1'] \
            = {'test': 3, 'test2': 9}

        self.script.verifications['VerifyOpsName']['test'] = 2
        self.script.verifications['VerifyOpsName']['test2'] = 2
        self.script.verifications['VerifyOpsName']['test3'] = 2

        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        self.assertEqual(len(items), 7)
        sec_items = list(items[2])
        self.assertEqual(len(sec_items), 7)
        self.assertEqual(sec_items[0].uid, 'pre_VerifyOpsName.PE1')
        self.assertEqual(sec_items[1].uid, 'pre_a_callable_always_same.PE1')
        self.assertEqual(sec_items[2].uid, 'test1')
        self.assertEqual(sec_items[3].uid, 'post_VerifyOpsName.PE1.1')
        self.assertEqual(sec_items[4].uid, 'post_VerifyOpsName.PE1.2')
        self.assertEqual(sec_items[5].uid, 'post_VerifyOpsName.PE1.3')
        self.assertEqual(sec_items[6].uid, 'post_a_callable_always_same.PE1')
        self.assertEqual(sec_items[0].parameters['test'], 5)
        self.assertEqual(sec_items[3].parameters['test'], 5)
        self.assertEqual(sec_items[4].parameters['test'], 5)
        self.assertEqual(sec_items[5].parameters['test'], 5)
        self.assertEqual(sec_items[0].parameters['test2'], 9)
        self.assertEqual(sec_items[3].parameters['test2'], 9)
        self.assertEqual(sec_items[4].parameters['test2'], 9)
        self.assertEqual(sec_items[5].parameters['test2'], 9)
        self.assertEqual(sec_items[0].parameters['test3'], 2)
        self.assertEqual(sec_items[3].parameters['test3'], 2)
        self.assertEqual(sec_items[4].parameters['test3'], 2)
        self.assertEqual(sec_items[5].parameters['test3'], 2)

    # And now Mix triggers and verifications
    def test_local_verf_ops_wrong(self):

        self.script.triggers = copy.deepcopy(self.trigger_local1)
        del self.script.triggers['TriggerShutNoShutBgp'] \
            ['verifications']
        self.script.triggers['TriggerShutNoShutBgp']['verifications'] = {}
        self.script.triggers['TriggerShutNoShutBgp']['verifications'] \
            ['Wrong'] = {'devices': {'PE1': {'test': 5}}}

        self.script.verification_uids = And('Wrong')
        self.script.verifications = self.wrong_veri
        with self.assertRaises(TypeError):
            loaded = self.discoverer._load_item('Wrong',
                                                self.wrong_veri,
                                                verification=True,
                                                counter=0)
        with self.assertRaises(Exception):
            self.script.subsection_data = self.subsections1
            items = list(self.discoverer)

    # And now Mix triggers and verifications
    def test_local_verf_count_device(self):

        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = copy.deepcopy(self.trigger_local1)
        self.script.triggers['TriggerShutNoShutBgp']['count'] = 3
        self.script.verifications = self.veri1
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        self.assertEqual(len(items), 11)
        self.assertEqual(len(list(items[2])), 5)
        self.assertEqual(len(list(items[4])), 5)
        self.assertEqual(len(list(items[6])), 5)

    # And now Mix triggers and verifications
    def test_empty_local_ver(self):

        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = copy.deepcopy(self.trigger_local1)
        self.script.verifications = self.veri1
        self.script.subsection_data = self.subsections1
        del self.script.triggers['TriggerShutNoShutBgp']['verifications']
        self.script.triggers['TriggerShutNoShutBgp']['verifications'] = None
        items = list(self.discoverer)

        for expected, item in zip([CommonSetup, items[1],
                                   TriggerShutNoShutBgp, items[3],
                                   TriggerShutNoShutOspf, items[5],
                                   CommonCleanup], items):

            try:
                self.assertTrue(isinstance(item, expected))
            except TypeError:
                # Ignore those for now,  callables verifications
                pass

        self.assertEqual(items[1].verifiers[0].uid, 'a_callable.PE1.1')
        self.assertEqual(items[1].verifiers[1].uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(items[3].verifiers[0].uid, 'a_callable.PE1.2')
        self.assertEqual(items[3].verifiers[1].uid, 'a_callable_always_same.PE1.2')
        self.assertEqual(items[5].verifiers[0].uid, 'a_callable.PE1.3')
        self.assertEqual(items[5].verifiers[1].uid, 'a_callable_always_same.PE1.3')

    def test_triggers_verifications_wrong_local(self):
        # Add triggers information to the script
        self.script.triggers = self.trigger_local2
        self.script.verifications = self.veri1
        self.script.verification_uids = ['Bad']
        with self.assertRaises(KeyError):
            loaded = self.discoverer._load_item('Bad',
                                                self.trigger_local2,
                                                verification=False,
                                                counter=0)
        with self.assertRaises(Exception):
            self.script.subsection_data = self.subsections1
            items = list(self.discoverer)
        # assert any(isinstance(x, TriggerDeviceNotFound) for x in items)

    def test_triggers_count(self):
        # Repeat the same trigger twice, but dont count the other trigger

        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = copy.deepcopy(self.trigger_local1)
        self.script.verifications = self.veri1
        self.script.triggers['TriggerShutNoShutBgp']['count'] = 3
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        for expected, item in zip([CommonSetup, items[1],
                                   TriggerShutNoShutBgp, items[3],
                                   TriggerShutNoShutBgp, items[5],
                                   TriggerShutNoShutBgp, items[7],
                                   TriggerShutNoShutOspf, items[9],
                                   CommonCleanup], items):

            try:
                self.assertTrue(isinstance(item, expected))
            except TypeError:
                # Ignore those for now,  callables verifications
                pass

        self.assertEqual(items[1].verifiers[0].uid, 'a_callable.PE1.1')
        self.assertEqual(items[1].verifiers[1].uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(items[3].verifiers[0].uid, 'a_callable.PE1.2')
        self.assertEqual(items[3].verifiers[1].uid, 'a_callable_always_same.PE1.2')
        self.assertEqual(items[5].verifiers[0].uid, 'a_callable.PE1.3')
        self.assertEqual(items[5].verifiers[1].uid, 'a_callable_always_same.PE1.3')
        self.assertEqual(items[7].verifiers[0].uid, 'a_callable.PE1.4')
        self.assertEqual(items[7].verifiers[1].uid, 'a_callable_always_same.PE1.4')
        self.assertEqual(items[9].verifiers[0].uid, 'a_callable.PE1.5')
        self.assertEqual(items[9].verifiers[1].uid, 'a_callable_always_same.PE1.5')

        uid_expected = ['no_paramed_subsection', 'paramed_subsection']
        for subsection, uid in zip(items[0], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

        # Verify extra_args and groups

        tc = items[1].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable.PE1.1')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[1].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[2]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'TriggerShutNoShutBgp.PE1.1')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['banana'], 'yellow')

        uid_expected = ['pre_a_callable.PE1',
                        'pre_a_callable_always_same.PE1',
                        'test1', 'post_a_callable.PE1',
                        'post_a_callable_always_same.PE1']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))
            # Finally, can you just call it
            if uid in ['post_a_callable.PE1']:
                with self.assertRaises(ResultSignal):
                    subsection()
            else:
                subsection()

        tc = items[3].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable.PE1.2')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[3].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.2')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[4]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'TriggerShutNoShutBgp.PE1.2')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['banana'], 'yellow')

        uid_expected = ['pre_a_callable.PE1',
                        'pre_a_callable_always_same.PE1',
                        'test1', 'post_a_callable.PE1',
                        'post_a_callable_always_same.PE1']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))
            # Finally, can you just call it
            if uid in ['post_a_callable.PE1']:
                with self.assertRaises(ResultSignal):
                    subsection()
            else:
                subsection()

        tc = items[5].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable.PE1.3')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[5].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.3')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[6]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'TriggerShutNoShutBgp.PE1.3')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['banana'], 'yellow')

        uid_expected = ['pre_a_callable.PE1',
                        'pre_a_callable_always_same.PE1',
                        'test1', 'post_a_callable.PE1',
                        'post_a_callable_always_same.PE1']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))
            # Finally, can you just call it
            if uid in ['post_a_callable.PE1']:
                with self.assertRaises(ResultSignal):
                    subsection()
            else:
                subsection()

        tc = items[7].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable.PE1.4')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[7].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.4')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[8]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'TriggerShutNoShutOspf.PE1')
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['var1'], 'value')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['pre_a_callable.PE1',
                        'pre_a_callable_always_same.PE1',
                        'test1', 'test2', 'post_a_callable.PE1',
                        'post_a_callable_always_same.PE1']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))
            # Finally, can you just call it
            if uid in ['post_a_callable.PE1']:
                with self.assertRaises(ResultSignal):
                    subsection()
            else:
                subsection()

        tc = items[9].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable.PE1.5')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[9].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.5')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        # Verify extra_args and groups

        uid_expected = ['without_param', 'with_param']
        for subsection, uid in zip(items[10], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

    def test_triggers_count2(self):
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = copy.deepcopy(self.trigger_local1)
        self.script.verifications = self.veri1
        self.script.triggers['TriggerShutNoShutBgp']['count'] = 3
        self.script.triggers['TriggerShutNoShutOspf']['count'] = 2
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        for expected, item in zip([CommonSetup, items[1],
                                   TriggerShutNoShutBgp, items[3],
                                   TriggerShutNoShutBgp, items[5],
                                   TriggerShutNoShutBgp, items[7],
                                   TriggerShutNoShutOspf, items[9],
                                   TriggerShutNoShutOspf, items[11],
                                   CommonCleanup], items):

            try:
                self.assertTrue(isinstance(item, expected))
            except TypeError:
                # Ignore those for now,  callables verifications
                pass

        self.assertEqual(items[1].verifiers[0].uid, 'a_callable.PE1.1')
        self.assertEqual(items[1].verifiers[1].uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(items[3].verifiers[0].uid, 'a_callable.PE1.2')
        self.assertEqual(items[3].verifiers[1].uid, 'a_callable_always_same.PE1.2')
        self.assertEqual(items[5].verifiers[0].uid, 'a_callable.PE1.3')
        self.assertEqual(items[5].verifiers[1].uid, 'a_callable_always_same.PE1.3')
        self.assertEqual(items[7].verifiers[0].uid, 'a_callable.PE1.4')
        self.assertEqual(items[7].verifiers[1].uid, 'a_callable_always_same.PE1.4')
        self.assertEqual(items[9].verifiers[0].uid, 'a_callable.PE1.5')
        self.assertEqual(items[9].verifiers[1].uid, 'a_callable_always_same.PE1.5')
        self.assertEqual(items[11].verifiers[0].uid, 'a_callable.PE1.6')
        self.assertEqual(items[11].verifiers[1].uid, 'a_callable_always_same.PE1.6')

    def test_triggers_count3(self):
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = copy.deepcopy(self.trigger_local1)
        self.script.verifications = copy.deepcopy(self.veri1)
        self.script.triggers['TriggerShutNoShutBgp']['count'] = 3
        self.script.triggers['TriggerShutNoShutOspf']['count'] = 2
        self.script.verifications['a_callable']['count'] = 2
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        for expected, item in zip([CommonSetup, items[1], 
                                   TriggerShutNoShutBgp, items[3],
                                   TriggerShutNoShutBgp, items[5],
                                   TriggerShutNoShutBgp, items[7],
                                   TriggerShutNoShutOspf, items[9],
                                   TriggerShutNoShutOspf, items[11],
                                   CommonCleanup], items):
            try:
                self.assertTrue(isinstance(item, expected))
            except TypeError:
                # Ignore those for now,  callables verifications
                pass

        self.assertEqual(items[1].uid, 'Verifications.TriggerShutNoShutBgp.PE1.1')
        self.assertEqual(items[2].uid, 'TriggerShutNoShutBgp.PE1.1')
        self.assertEqual(items[3].uid, 'Verifications.TriggerShutNoShutBgp.PE1.2')
        self.assertEqual(items[4].uid, 'TriggerShutNoShutBgp.PE1.2')
        self.assertEqual(items[5].uid, 'Verifications.TriggerShutNoShutBgp.PE1.3')
        self.assertEqual(items[6].uid, 'TriggerShutNoShutBgp.PE1.3')
        self.assertEqual(items[7].uid, 'Verifications.TriggerShutNoShutOspf.PE1.1')
        self.assertEqual(items[8].uid, 'TriggerShutNoShutOspf.PE1.1')
        self.assertEqual(items[9].uid, 'Verifications.TriggerShutNoShutOspf.PE1.2')
        self.assertEqual(items[10].uid, 'TriggerShutNoShutOspf.PE1.2')
        self.assertEqual(items[11].uid, 'Verifications.post')

    def test_triggers_two_devices(self):
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = copy.deepcopy(self.trigger_local1)
        self.script.verifications = copy.deepcopy(self.veri1)
        self.script.triggers['TriggerShutNoShutBgp']['devices'].append('PE2')
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        for expected, item in zip([CommonSetup, items[1], 
                                   TriggerShutNoShutBgp, items[3],
                                   TriggerShutNoShutBgp, items[5],
                                   TriggerShutNoShutOspf, items[7],
                                   CommonCleanup], items):
            try:
                self.assertTrue(isinstance(item, expected))
            except TypeError:
                # Ignore those for now,  callables verifications
                pass

        self.assertEqual(items[1].uid, 'Verifications.TriggerShutNoShutBgp.PE1')
        self.assertEqual(items[2].uid, 'TriggerShutNoShutBgp.PE1')
        self.assertEqual(items[3].uid, 'Verifications.TriggerShutNoShutBgp.PE2')
        self.assertEqual(items[4].uid, 'TriggerShutNoShutBgp.PE2')
        self.assertEqual(items[5].uid, 'Verifications.TriggerShutNoShutOspf.PE1')
        self.assertEqual(items[6].uid, 'TriggerShutNoShutOspf.PE1')
        self.assertEqual(items[7].uid, 'Verifications.post')

    def test_triggers_two_devices_counts(self):
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = copy.deepcopy(self.trigger_local1)
        self.script.verifications = copy.deepcopy(self.veri1)
        self.script.triggers['TriggerShutNoShutBgp']['devices_attributes'] = {'PE1': {}, 'PE2': {}}
        self.script.triggers['TriggerShutNoShutBgp'] \
            ['devices_attributes']['PE1'] = {'count': 2}
        self.script.triggers['TriggerShutNoShutBgp'] \
            ['devices_attributes']['PE2'] = {'count': 3}
        self.script.triggers['TriggerShutNoShutBgp']['devices'].append('PE2')
        self.script.verifications['a_callable']['devices_attributes'] = {'PE1': {}}
        self.script.verifications['a_callable']['devices_attributes']['PE1'] = {'count': 3}
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        self.assertEqual(len(items), 15)
        self.assertEqual(items[1].uid, 'Verifications.TriggerShutNoShutBgp.PE1.1')
        self.assertEqual(items[2].uid, 'TriggerShutNoShutBgp.PE1.1')
        self.assertEqual(items[3].uid, 'Verifications.TriggerShutNoShutBgp.PE1.2')
        self.assertEqual(items[4].uid, 'TriggerShutNoShutBgp.PE1.2')
        self.assertEqual(items[5].uid, 'Verifications.TriggerShutNoShutBgp.PE2.1')
        self.assertEqual(items[6].uid, 'TriggerShutNoShutBgp.PE2.1')
        self.assertEqual(items[7].uid, 'Verifications.TriggerShutNoShutBgp.PE2.2')
        self.assertEqual(items[8].uid, 'TriggerShutNoShutBgp.PE2.2')
        self.assertEqual(items[9].uid, 'Verifications.TriggerShutNoShutBgp.PE2.3')
        self.assertEqual(items[10].uid, 'TriggerShutNoShutBgp.PE2.3')
        self.assertEqual(items[11].uid, 'Verifications.TriggerShutNoShutOspf.PE1')
        self.assertEqual(items[12].uid, 'TriggerShutNoShutOspf.PE1')
        self.assertEqual(items[13].uid, 'Verifications.post')

    def test_uids_triggers_verf(self):
        # Add triggers information to the script
        self.script.triggers = self.triggers1
        self.script.verifications = self.veri1
        self.script.verification_uids = And('same')
        self.script.trigger_uids = And('Bgp')
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)
        self.assertEqual(len(items), 5)

        self.assertEqual(items[1].verifiers[0].uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(items[2].uid, 'TriggerShutNoShutBgp.PE1')
        self.assertEqual(items[3].verifiers[0].uid, 'a_callable_always_same.PE1.2')

    def test_uids_triggers_verf_count(self):
        # Add triggers information to the script
        self.script.triggers = copy.deepcopy(self.triggers1)
        self.script.verifications = copy.deepcopy(self.veri1)
        self.script.triggers['TriggerShutNoShutBgp']['count'] = 3
        self.script.verifications['a_callable']['count'] = 2
        self.script.verifications['a_callable_always_same']['count'] = 3
        self.script.verification_uids = And('same')
        self.script.trigger_uids = And('Bgp')
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)
        self.assertEqual(len(items), 9)

        self.assertEqual(items[1].verifiers[0].uid, 'a_callable_always_same.PE1.1.1')
        self.assertEqual(items[1].verifiers[1].uid, 'a_callable_always_same.PE1.1.2')
        self.assertEqual(items[1].verifiers[2].uid, 'a_callable_always_same.PE1.1.3')
        self.assertEqual(items[2].uid, 'TriggerShutNoShutBgp.PE1.1')
        self.assertEqual(items[3].verifiers[0].uid, 'a_callable_always_same.PE1.2.1')
        self.assertEqual(items[3].verifiers[1].uid, 'a_callable_always_same.PE1.2.2')
        self.assertEqual(items[3].verifiers[2].uid, 'a_callable_always_same.PE1.2.3')
        self.assertEqual(items[4].uid, 'TriggerShutNoShutBgp.PE1.2')
        self.assertEqual(items[5].verifiers[0].uid, 'a_callable_always_same.PE1.3.1')
        self.assertEqual(items[5].verifiers[1].uid, 'a_callable_always_same.PE1.3.2')
        self.assertEqual(items[5].verifiers[2].uid, 'a_callable_always_same.PE1.3.3')
        self.assertEqual(items[6].uid, 'TriggerShutNoShutBgp.PE1.3')
        self.assertEqual(items[7].verifiers[0].uid, 'a_callable_always_same.PE1.4.1')
        self.assertEqual(items[7].verifiers[1].uid, 'a_callable_always_same.PE1.4.2')
        self.assertEqual(items[7].verifiers[2].uid, 'a_callable_always_same.PE1.4.3')

    def test_uids_triggers_verf_count2(self):
        # Add triggers information to the script
        self.script.triggers = copy.deepcopy(self.triggers1)
        self.script.verifications = copy.deepcopy(self.veri1)
        self.script.triggers['TriggerShutNoShutBgp']['count'] = 3
        self.script.verifications['a_callable']['count'] = 2
        self.script.verifications['a_callable_always_same']['count'] = 3
        self.script.verification_uids = Not('PE1')
        self.script.trigger_uids = Not('PE1')
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)
        self.assertEqual(len(items), 11)

        self.assertEqual(items[0].uid, 'common_setup')
        self.assertEqual(items[1].verifiers[0].uid, 'a_callable.PE1.1.1')

    def test_uids_triggers_verf_two_devices(self):
        self.script.triggers = copy.deepcopy(self.trigger_local1)
        self.script.verifications = copy.deepcopy(self.veri1)
        self.script.triggers['TriggerShutNoShutBgp']['devices'].append('PE2')
        self.script.verifications['a_callable']['devices'].append('PE2')
        self.script.verification_uids = Not('PE1')
        self.script.trigger_uids = Not('PE1')
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        self.assertEqual(items[1].verifiers[0].uid, 'a_callable.PE1.1')
        self.assertEqual(items[1].verifiers[1].uid, 'a_callable.PE2.1')
        self.assertEqual(items[1].verifiers[2].uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(items[2].uid, 'TriggerShutNoShutBgp.PE1')

    def test_uids_triggers_verf_two_devices_wrong_uid(self):
        self.script.triggers = copy.deepcopy(self.trigger_local1)
        self.script.verifications = copy.deepcopy(self.veri1)
        self.script.triggers['TriggerShutNoShutBgp']['devices'].append('PE2')
        self.script.verifications['a_callable']['devices'].append('PE2')
        self.script.verification_uids = Not('PE3')
        self.script.trigger_uids = Not('PE3')
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        self.assertEqual(items[1].verifiers[0].uid, 'a_callable.PE1.1')
        self.assertEqual(items[1].verifiers[1].uid, 'a_callable.PE2.1')
        self.assertEqual(items[1].verifiers[2].uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(items[2].uid, 'TriggerShutNoShutBgp.PE1')
        self.assertEqual(items[3].verifiers[0].uid, 'a_callable.PE1.2')
        self.assertEqual(items[3].verifiers[1].uid, 'a_callable.PE2.2')
        self.assertEqual(items[3].verifiers[2].uid, 'a_callable_always_same.PE1.2')
        self.assertEqual(items[4].uid, 'TriggerShutNoShutBgp.PE2')
        self.assertEqual(items[5].verifiers[0].uid, 'a_callable.PE1.3')
        self.assertEqual(items[5].verifiers[1].uid, 'a_callable.PE2.3')
        self.assertEqual(items[5].verifiers[2].uid, 'a_callable_always_same.PE1.3')
        self.assertEqual(items[6].uid, 'TriggerShutNoShutOspf.PE1')
        self.assertEqual(items[7].verifiers[0].uid, 'a_callable.PE1.4')
        self.assertEqual(items[7].verifiers[1].uid, 'a_callable.PE2.4')
        self.assertEqual(items[7].verifiers[2].uid, 'a_callable_always_same.PE1.4')

    def test_groups_triggers_verf(self):
        # Add triggers information to the script
        self.script.triggers = copy.deepcopy(self.triggers1)
        self.script.verifications = copy.deepcopy(self.veri1)
        self.script.verification_uids = None
        self.script.verification_groups = And('L2')
        self.script.trigger_uids = None
        self.script.trigger_groups = And('L2')
        self.script.triggers['TriggerShutNoShutBgp']['groups'] = 'L3'
        self.script.verifications['a_callable']['groups'] = 'L3'
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        self.assertEqual(items[1].verifiers[0].uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(items[2].uid, 'TriggerShutNoShutOspf.PE1')
        self.assertEqual(items[3].verifiers[0].uid, 'a_callable_always_same.PE1.2')

    def test_groups_triggers_verf2(self):
        # Add triggers information to the script
        self.script.triggers = copy.deepcopy(self.triggers1)
        self.script.verifications = copy.deepcopy(self.veri1)
        self.script.verification_uids = None
        self.script.verification_groups = And('L2')
        self.script.trigger_uids = None
        self.script.trigger_groups = And('L2')
        self.script.triggers['TriggerShutNoShutBgp']['groups'] = 'L3'
        self.script.verifications['a_callable']['groups'] = 'L3'
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)
        self.assertEqual(len(items), 5)

        self.assertEqual(items[1].verifiers[0].uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(items[2].uid, 'TriggerShutNoShutOspf.PE1')
        self.assertEqual(items[3].verifiers[0].uid, 'a_callable_always_same.PE1.2')

    def test_execution_results_fail_verification(self):
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        veri1 = {'fail':
                     {'source': {'class': 'genie.tests.harness.' \
                                          'script.verifications.a_failing_callable'},
                      'name': 'trigger', 'var1': 'yellow',
                      'groups': ['L2'],
                      'devices': ['PE1'],
                      },
                 }

        self.script.verifications = veri1
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        self.assertEqual(items[1].verifiers[0].result, results.Passed)
        items[1].verifiers[0]()
        self.assertEqual(items[1].verifiers[0].result, results.Failed)

    def test_execution_results_error_verification(self):
        veri1 = {'fail':
                     {'source': {'class': 'genie.tests.harness.' \
                                          'script.verifications.a_error_callable'},
                      'name': 'trigger', 'var1': 'yellow',
                      'groups': ['L2'],
                      'devices': ['PE1'],
                      },
                 }

        self.script.verifications = veri1
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)
        self.assertEqual(items[2].result, results.Passed)
        items[2]()
        self.assertEqual(items[2].result, results.Errored)

    def test_execution_results_missing_verification(self):
        veri1 = {'fail':
                     {'source': {'class': 'genie.tests.harness.' \
                                          'script.verifications.a_missing_arg_callable'},
                      'name': 'trigger', 'var1': 'yellow',
                      'groups': ['L2'],
                      'devices': ['PE1'],
                      },
                 }

        self.script.verifications = veri1
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)
        self.assertEqual(items[2].result, results.Passed)
        items[2]()
        self.assertEqual(items[2].result, results.Errored)

    def test_execution_results_diff_verification(self):
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        veri1 = {'fail':
                     {'source': {'class': 'genie.tests.harness.' \
                                          'script.verifications.a_callable'},
                      'name': 'trigger', 'var1': 'yellow',
                      'groups': ['L2'],
                      'devices': ['PE1'],
                      },
                 }

        self.script.verifications = veri1
        self.script.triggers = self.triggers1
        self.script.subsection_data = self.subsections1
        
        items = list(self.discoverer)

        self.assertEqual(items[1].verifiers[0].result, results.Passed)
        items[1].verifiers[0]()
        self.assertEqual(items[1].verifiers[0].result, results.Passed)
        msg = "-value: {x}".format(x=items[1].verifiers[0].x)

        self.assertEqual(items[5].verifiers[0].result, results.Passed)
        with self.assertLogs('', level='INFO') as cm:
            items[5].verifiers[0]()
            output = '\n'.join(cm.output)
            msg2 = "+value: {x}".format(x=items[5].verifiers[0].x)
            self.assertTrue(msg in output)
            self.assertTrue(msg2 in output)
        self.assertEqual(items[5].verifiers[0].result, results.Failed)

    def test_execution_results_diff_verification_local(self):

        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.verifications = self.veri1
        self.script.triggers = self.trigger_local1
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        self.assertEqual(items[1].verifiers[0].result, results.Passed)
        items[1].verifiers[0]()
        self.assertEqual(items[1].verifiers[0].result, results.Passed)
        msg_item1 = '-value: {x}'.format(x=items[1].verifiers[0].x)

        # Local here
        elem = list(items[2])

        elem[0].result = results.Passed
        elem[0]()
        elem[0].result = results.Passed
        elem[1].result = results.Passed
        elem[1]()
        elem[1].result = results.Passed

        elem[3].result = results.Passed
        with self.assertRaises(ResultSignal):
            elem[3]()
        elem[3].result = results.Failed

        elem[4].result = results.Passed
        elem[4]()
        elem[4].result = results.Passed

    # And now Mix triggers, verifications and setup/cleanup
    def test_triggers_verifications_local_setup_cleanup(self):

        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = self.triggers3
        self.script.verifications = self.veri1
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        self.assertEqual(items[2].uid, 'TriggerIsisBasic.PE1')
        elem = list(items[2])
        self.assertEqual(elem, list())

        item_idx = [4, 6, 8, 10, 12, 14, 16]

        tcs = ['TriggerBgpNoSetupCleanup.PE1', 'TriggerHsrpWtSetup.PE1',
               'TriggerVlanWtCleanup.PE1', 'TriggerOspfWtSetupCleanup.PE1',
               'TriggerWtJustSetupCleanup.PE1', 'TriggerMixedOrder.PE1',
               'TriggerNoDecorator.PE1', ]

        uids = [
            ['pre_a_callable.PE1', 'pre_a_callable_always_same.PE1',
             'test1', 'test2',
             'post_a_callable.PE1', 'post_a_callable_always_same.PE1'],

            ['test_setup',
             'pre_a_callable.PE1', 'pre_a_callable_always_same.PE1',
             'test1',
             'post_a_callable.PE1', 'post_a_callable_always_same.PE1'],

            ['pre_a_callable.PE1', 'pre_a_callable_always_same.PE1',
             'test1',
             'post_a_callable.PE1', 'post_a_callable_always_same.PE1',
             'test_cleanup'],

            ['test_setup',
             'pre_a_callable.PE1', 'pre_a_callable_always_same.PE1',
             'test1',
             'post_a_callable.PE1', 'post_a_callable_always_same.PE1',
             'test_cleanup'],

            ['test_setup',
             'pre_a_callable.PE1', 'pre_a_callable_always_same.PE1',
             'post_a_callable.PE1', 'post_a_callable_always_same.PE1',
             'test_cleanup'],

            ['test_setup',
             'pre_a_callable.PE1', 'pre_a_callable_always_same.PE1',
             'test1',
             'test2',
             'post_a_callable.PE1', 'post_a_callable_always_same.PE1',
             'test_cleanup'],

            ['test_setup',
             'pre_a_callable.PE1', 'pre_a_callable_always_same.PE1',
             'test2',
             'post_a_callable.PE1', 'post_a_callable_always_same.PE1',
             'test_cleanup'], ]

        for expected_tc, expected_sec, idx in zip(tcs, uids, item_idx):
            self.assertEqual(items[idx].uid, expected_tc)
            elem = list(items[idx])
            for expected, testsection in zip(expected_sec, elem):
                self.assertEqual(testsection.uid, expected)

    # And now common setup/cleanup
    def test_common_setup_cleanup(self):
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)
        self.assertEqual(items[0].uid, 'common_setup')
        self.assertEqual(items[1].uid, 'common_cleanup')
        setup = list(items[0])
        self.assertEqual(setup[0].uid, 'no_paramed_subsection')
        self.assertEqual(setup[1].uid, 'paramed_subsection')
        cleanup = list(items[1])
        self.assertEqual(cleanup[0].uid, 'without_param')
        with self.assertRaises(ValueError):
            cleanup[1]()

    def test_tc_name(self):

        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        triggers = {'TriggerShutNoShutBgp':
                        {'source': {'class': 'genie.tests.harness.script.triggers.TriggerShutNoShutBgp'},
                         'name': 'trigger', 'banana': 'yellow',
                         'groups': ['L2'],
                         'devices': {'PE4': 'None'},
                         }
                    }

        dev3 = Device(testbed=self.testbed, name='PE4', os='iosxr')
        dev3.custom = {'abstraction': {'order': ['os'], 'context': 'yang'}}

        dev3.aliases = ['uut', 'random']
        self.script.triggers = triggers
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        # self.assertEqual(items[1].uid, 'Verifications.TriggerShutNoShutBgp.uut')
        self.assertEqual(items[1].uid, 'TriggerShutNoShutBgp.uut')

    def test_verification_parameters(self):
        # Mix of callable verification and verification instances
        veri1 = {'callable_verification':
                     {'source': {'class': 'genie.tests.harness.' \
                                          'script.verifications.a_missing_arg_callable'},
                      'name': 'trigger', 'var1': 'yellow',
                      'groups': ['L2'],
                      'devices': ['PE1'],
                      'parameters': {'missing': 'None'}
                      },
                 'VerifyOpsParameters':
                     {'source': {'class': 'genie.tests.harness.script.verifications.VerifyOpsWithParameters'},
                      'some_args': 'trigger', 'var1': 'yellow',
                      'groups': ['L2'],
                      'devices': ['PE1'],
                      'parameters': {'missing': 'None'}
                      },
                 }
        self.script.verifications = veri1
        self.script.subsection_data = self.subsections1
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        items = list(self.discoverer)

        self.assertEqual(items[1].result, results.Passed)
        items[1]()
        self.assertEqual(items[1].result, results.Passed)

        self.script.triggers = self.triggers4
        self.script.verifications = veri1
        items = list(self.discoverer)
        
        for idx in range(1, 4):
            self.assertEqual(items[idx].result, results.Passed)
            items[idx]()
            self.assertEqual(items[idx].result, results.Passed)

    def test_trigger_processors(self):
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = self.triggers5
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        from pyats.aetest import processors
        from genie.tests.harness.script.triggers import prepostprocessor, \
            processorwithparam, \
            exceptionprocessor
        pre_processors = processors.get(items[1], 'pre')
        post_processors = processors.get(items[1], 'post')
        exception_processors = processors.get(items[1], 'exception')

        self.assertEqual(pre_processors, [prepostprocessor])
        self.assertEqual(post_processors[0].func,
                         processorwithparam)
        self.assertEqual(post_processors[0].keywords,
                         {'param1': 'abc'})
        self.assertEqual(exception_processors, [exceptionprocessor])

    def test_trigger_processors_different_args(self):
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = self.triggers7
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        from pyats.aetest import processors
        from genie.tests.harness.script.triggers import prepostprocessor, \
            processorwithparam, \
            exceptionprocessor
        pre_processors = processors.get(items[1], 'pre')
        post_processors = processors.get(items[1], 'post')
        exception_processors = processors.get(items[1], 'exception')

        self.assertEqual(pre_processors, [prepostprocessor])
        self.assertEqual(post_processors[0].func,
                         processorwithparam)
        if post_processors[0].keywords == {'param1': 'abc'}:
            first = {'param1': 'abc'}
            second = {'param1': '123'}
        else:
            first = {'param1': '123'}
            second = {'param1': 'abc'}

        self.assertEqual(post_processors[0].keywords,
                         first)
        self.assertEqual(post_processors[1].func,
                         processorwithparam)
        self.assertEqual(post_processors[1].keywords,
                         second)
        self.assertEqual(exception_processors, [exceptionprocessor])

    def test_verification_processors(self):
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.verifications = self.veri5
        self.script.subsection_data = self.subsections1
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        items = list(self.discoverer)

        from pyats.aetest import processors
        from genie.tests.harness.script.triggers import prepostprocessor, \
            processorwithparam, \
            exceptionprocessor

        pre_processors = processors.get(items[1].verifiers[0], 'pre')
        post_processors = processors.get(items[1].verifiers[0], 'post')
        exception_processors = processors.get(items[1].verifiers[0], 'exception')

        self.assertEqual(pre_processors, [prepostprocessor])
        self.assertEqual(post_processors[0].func,
                         processorwithparam)
        self.assertEqual(post_processors[0].keywords,
                         {'param1': 'abc'})
        self.assertEqual(exception_processors, [exceptionprocessor])
        self.assertEqual(exception_processors, [exceptionprocessor])

    def test_ordered_processors(self):
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = self.triggers6
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)
        from pyats.aetest import processors
        from genie.tests.harness.script.triggers import prepostprocessor, \
            processorwithparam, \
            exceptionprocessor
        pre_processors = processors.get(items[1], 'pre')
        pre_processors[-1] = pre_processors[-1]
        # Expect first two processors in order like defined,
        # with other processors following
        self.assertEqual(pre_processors[:-1], [exceptionprocessor, prepostprocessor])
        self.assertEqual(pre_processors[-1].func, processorwithparam)

    def test_subsection_processors(self):
        from pyats.aetest import processors
        from genie.tests.harness.script.triggers import prepostprocessor, \
            processorwithparam, \
            exceptionprocessor
        self.script.subsection_data = self.subsections2
        items = list(self.discoverer)
        # Check what is inside each items
        # In expected order
        subsection = list(items[0])
        pre_processors = processors.get(subsection[1], 'pre')
        pre_processors[-1] = pre_processors[-1]
        # Expect first two processors in order like defined,
        # with other processors following
        self.assertEqual(pre_processors[:-1], [exceptionprocessor, prepostprocessor])
        self.assertEqual(pre_processors[-1].func, processorwithparam)
        self.script.subsection_data = self.subsections2
        subsection = list(items[1])
        pre_processors = processors.get(subsection[1], 'pre')
        pre_processors[-1] = pre_processors[-1]
        # Expect first two processors in order like defined,
        # with other processors following
        self.assertEqual(pre_processors[:-1], [exceptionprocessor, prepostprocessor])
        self.assertEqual(pre_processors[-1].func, processorwithparam)

    def test_common_setup_cleanup_1(self):
        self.script.url = 'test'
        self.script.subsection_data = self.subsections3
        items = list(self.discoverer)
        self.assertEqual(items[0].uid, 'common_setup')
        self.assertEqual(items[1].uid, 'common_cleanup')
        setup = list(items[0])
        self.assertEqual(setup[0].uid, 'check_config')
        setup[0]()
        cleanup = list(items[1])
        self.assertEqual(cleanup[0].uid, 'check_post_config')
        with self.assertRaises(AEtestSkippedSignal):
            cleanup[0]()

    def test_common_setup_cleanup_4(self):
        self.script.url = 'test'
        self.script.subsection_data = self.subsections4
        items = list(self.discoverer)
        for item in items:
            with self.assertRaises(ModuleNotFoundError):
                item()

    def test_triggers_order_list1(self):
        # test triggers order when input trigger_uids is list
        self.script.verification_uids = []
        self.script.trigger_uids = ['TriggerShutNoShutOspf', 'TriggerShutNoShutBgp']
        self.script.triggers = self.triggers2
        self.script.subsection_data = self.subsections1
        self.discoverer_list = GenieScriptDiscover(self.script)

        self.assertTrue(isinstance(self.discoverer_list.target.trigger_uids, list))

        items = list(self.discoverer_list.discover())

        for expected, item in zip([CommonSetup, items[1],
                                   TriggerShutNoShutOspf, items[3],
                                   TriggerShutNoShutBgp, items[5],
                                   CommonCleanup],
                                  items):
            try:
                self.assertTrue(isinstance(item, expected))
            except TypeError:
                pass

        uid_expected = ['no_paramed_subsection', 'paramed_subsection']
        for subsection, uid in zip(items[0], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

            # Verify extra_args and groups
            tc = items[2]
            self.assertEqual(tc.groups, ['L2'])
            self.assertEqual(tc.uid, 'TriggerShutNoShutOspf.PE1')
            self.assertEqual(tc.parameters['name'], 'test')
            self.assertEqual(tc.parameters['var1'], 'value')

            uid_expected = ['test1']
            for subsection, uid in zip(tc, uid_expected):
                self.assertEqual(subsection.uid, uid)
                self.assertTrue(isinstance(subsection, TestSection))
                # Finally, can you just call it
                subsection()

            # Verify extra_args and groups
            tc = items[4]
            self.assertEqual(tc.groups, ['L2'])
            self.assertEqual(tc.uid, 'TriggerShutNoShutBgp.PE1')
            self.assertEqual(tc.parameters['name'], 'trigger')
            self.assertEqual(tc.parameters['banana'], 'yellow')

            uid_expected = ['test1', 'test2']
            for subsection, uid in zip(tc, uid_expected):
                self.assertEqual(subsection.uid, uid)
                self.assertTrue(isinstance(subsection, TestSection))
                # Finally, can you just call it
                subsection()

            uid_expected = ['without_param', 'with_param']
            for subsection, uid in zip(items[6], uid_expected):
                self.assertEqual(subsection.uid, uid)
                self.assertTrue(isinstance(subsection, Subsection))

    def test_triggers_order_list2(self):
        # test triggers order when input trigger_uids is list
        self.script.verification_uids = []
        self.script.trigger_uids = ['TriggerShutNoShutBgp', 'TriggerShutNoShutOspf']
        self.script.triggers = self.triggers2
        self.script.subsection_data = self.subsections1
        self.discoverer_list = GenieScriptDiscover(self.script)
        self.assertTrue(isinstance(self.discoverer_list.target.trigger_uids, list))
        items = list(self.discoverer_list.discover())
        for expected, item in zip([CommonSetup, TriggerShutNoShutBgp,
                                   TriggerShutNoShutOspf, CommonCleanup],
                                  items):
            self.assertTrue(isinstance(item, expected))
        uid_expected = ['no_paramed_subsection', 'paramed_subsection']
        for subsection, uid in zip(items[0], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))
            # Verify extra_args and groups
            tc = items[2]
            self.assertEqual(tc.groups, ['L2'])
            self.assertEqual(tc.uid, 'TriggerShutNoShutOspf.PE1')
            self.assertEqual(tc.parameters['name'], 'test')
            self.assertEqual(tc.parameters['var1'], 'value')
            uid_expected = ['test1']
            for subsection, uid in zip(tc, uid_expected):
                self.assertEqual(subsection.uid, uid)
                self.assertTrue(isinstance(subsection, TestSection))
                # Finally, can you just call it
                subsection()
            # Verify extra_args and groups
            tc = items[1]
            self.assertEqual(tc.groups, ['L2'])
            self.assertEqual(tc.uid, 'TriggerShutNoShutBgp.PE1')
            self.assertEqual(tc.parameters['name'], 'trigger')
            self.assertEqual(tc.parameters['banana'], 'yellow')
            uid_expected = ['test1', 'test2']
            for subsection, uid in zip(tc, uid_expected):
                self.assertEqual(subsection.uid, uid)
                self.assertTrue(isinstance(subsection, TestSection))
                # Finally, can you just call it
                subsection()
            uid_expected = ['without_param', 'with_param']
            for subsection, uid in zip(items[3], uid_expected):
                self.assertEqual(subsection.uid, uid)
                self.assertTrue(isinstance(subsection, Subsection))

    def test_triggers_order_list1(self):
        # test triggers order when input trigger_uids is list
        self.script.verification_uids = []
        self.script.trigger_uids = ['TriggerShutNoShutOspf', 'TriggerShutNoShutBgp']
        self.script.triggers = self.triggers2
        self.script.subsection_data = self.subsections1
        self.discoverer_list = GenieScriptDiscover(self.script)
        self.assertTrue(isinstance(self.discoverer_list.target.trigger_uids, list))
        items = list(self.discoverer_list.discover())
        for expected, item in zip([CommonSetup, TriggerShutNoShutOspf,
                                   TriggerShutNoShutBgp, CommonCleanup],
                                  items):
            self.assertTrue(isinstance(item, expected))
        uid_expected = ['no_paramed_subsection', 'paramed_subsection']
        for subsection, uid in zip(items[0], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))
            # Verify extra_args and groups
            tc = items[1]
            self.assertEqual(tc.groups, ['L2'])
            self.assertEqual(tc.uid, 'TriggerShutNoShutOspf.PE1')
            self.assertEqual(tc.parameters['name'], 'test')
            self.assertEqual(tc.parameters['var1'], 'value')
            uid_expected = ['test1']
            for subsection, uid in zip(tc, uid_expected):
                self.assertEqual(subsection.uid, uid)
                self.assertTrue(isinstance(subsection, TestSection))
                # Finally, can you just call it
                subsection()
            # Verify extra_args and groups
            tc = items[2]
            self.assertEqual(tc.groups, ['L2'])
            self.assertEqual(tc.uid, 'TriggerShutNoShutBgp.PE1')
            self.assertEqual(tc.parameters['name'], 'trigger')
            self.assertEqual(tc.parameters['banana'], 'yellow')
            uid_expected = ['test1', 'test2']
            for subsection, uid in zip(tc, uid_expected):
                self.assertEqual(subsection.uid, uid)
                self.assertTrue(isinstance(subsection, TestSection))
                # Finally, can you just call it
                subsection()
            uid_expected = ['without_param', 'with_param']
            for subsection, uid in zip(items[3], uid_expected):
                self.assertEqual(subsection.uid, uid)
                self.assertTrue(isinstance(subsection, Subsection))

    def test_verifications_order_list2(self):
        # test verifications order when input verification_uids is list
        # Add triggers information to the script
        self.script.verification_uids = ['a_callable', 'a_callable_always_same']
        self.script.trigger_uids = []
        self.script.verifications = self.veri2
        self.script.subsection_data = self.subsections1
        self.discoverer_list = GenieScriptDiscover(self.script)

        self.assertTrue(isinstance(self.discoverer_list.target.verification_uids, list))

        items = list(self.discoverer_list.discover())

        for expected, item in zip([CommonSetup, items[1],
                                   CommonCleanup], items):

            try:
                self.assertTrue(isinstance(item, expected))
            except TypeError:
                # Ignore those for now,  callables verifications
                pass

        self.assertEqual(items[1].uid, 'Verifications.post')
        self.assertEqual(items[1].verifiers[0].uid, 'a_callable.PE1.1')
        self.assertEqual(items[1].verifiers[1].uid, 'a_callable_always_same.PE1.1')

        uid_expected = ['no_paramed_subsection', 'paramed_subsection']
        for subsection, uid in zip(items[0], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

        # Verify extra_args and groups

        tc = items[1].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable.PE1.1')
        self.assertEqual(tc.parameters['var1'], 'yellow')
        self.assertEqual(tc.parameters['name'], 'trigger')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[1].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'a_callable_always_same.PE1.1')
        self.assertEqual(tc.parameters['var1'], 5)
        self.assertEqual(tc.parameters['name'], 'test')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        uid_expected = ['without_param', 'with_param']
        for subsection, uid in zip(items[2], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

    def test_load_procesors_both_local_and_global_processor(self):
        '''local and global processors where parameters are overwrite and order is changed'''
        tc = self.triggers_with_processor['TriggerBgpNoSetupCleanup']
        dv = copy.deepcopy(self.global_processor)
        dv.update(self.triggers_with_processor)
        out_pre_processors, out_post_processors, out_exceptions = \
            _load_processors(tc, data_values=dv)
        expect_pre_processors = {'parama': 'locala'}
        expect_post_processors = [{'paramc': 1},
                                  {'paramb': ['uut']},
                                  {'paramd': 2}]
        self.assertEqual(out_pre_processors[0].keywords, expect_pre_processors)
        self.assertEqual(out_post_processors[0].keywords, expect_post_processors[0])
        self.assertEqual(out_post_processors[1].keywords, expect_post_processors[1])
        self.assertEqual(out_post_processors[2].keywords, expect_post_processors[2])

    def test_load_procesors_only_local_processor(self):
        tc = self.triggers_with_processor['TriggerBgpNoSetupCleanup']
        dv = self.triggers_with_processor
        out_pre_processors, out_post_processors, out_exceptions = \
            _load_processors(tc, data_values=dv)
        expect_pre_processors = {'parama': 'locala'}
        expect_post_processors = [{'paramc': 1},
                                  {'paramb': ['uut']}]
        self.assertEqual(out_pre_processors[0].keywords, expect_pre_processors)
        self.assertEqual(out_post_processors[0].keywords, expect_post_processors[0])
        self.assertEqual(out_post_processors[1].keywords, expect_post_processors[1])

    def test_load_procesors_only_global_processor(self):
        tc = self.triggers_without_processor['TriggerBgpNoSetupCleanup']
        dv = copy.deepcopy(self.global_processor)
        dv.update(self.triggers_without_processor)
        out_pre_processors, out_post_processors, out_exceptions = \
            _load_processors(tc, data_values=dv)
        expect_pre_processors = {'parama': 'globala'}
        expect_post_processors = [{'paramb': ['uut', 'P1']},
                                  {'paramd': 2},
                                  {'paramc': 'globalc'}]
        self.assertEqual(out_pre_processors[0].keywords, expect_pre_processors)
        self.assertEqual(out_post_processors[0].keywords, expect_post_processors[0])
        self.assertEqual(out_post_processors[1].keywords, expect_post_processors[1])
        self.assertEqual(out_post_processors[2].keywords, expect_post_processors[2])

    def test_load_procesors_no_processor(self):
        tc = self.triggers_without_processor['TriggerBgpNoSetupCleanup']
        dv = self.triggers_without_processor
        out_pre_processors, out_post_processors, out_exceptions = \
            _load_processors(tc, data_values=dv)
        self.assertEqual(out_pre_processors, [])
        self.assertEqual(out_post_processors, [])

    def test_multiple_triggers(self):
        tc1 = self.triggers_for_global_local_processor['TriggerBgpNoSetupCleanup']
        tc2 = self.triggers_for_global_local_processor['TriggerOspfWtSetupCleanup']
        dv = self.triggers_for_global_local_processor
        out_pre_processors1, out_post_processors1, out_exceptions1 = \
            _load_processors(tc1, data_values=dv)
        expect_post_processors1 = [{'paramc': 1},
                                   {'paramb': ['uut']},
                                   {'paramd': 2}]
        self.assertEqual(out_post_processors1[0].keywords, expect_post_processors1[0])
        self.assertEqual(out_post_processors1[1].keywords, expect_post_processors1[1])
        self.assertEqual(out_post_processors1[2].keywords, expect_post_processors1[2])

        out_pre_processors2, out_post_processors2, out_exceptions2 = \
            _load_processors(tc2, data_values=dv)
        expect_post_processors2 = [{'paramb2': ['P1'], 'paramb': ['uut', 'P1']},
                                   {'paramc': 2},
                                   {'paramd': 2}]
        self.assertEqual(out_post_processors2[0].keywords, expect_post_processors2[0])
        self.assertEqual(out_post_processors2[1].keywords, expect_post_processors2[1])
        self.assertEqual(out_post_processors2[2].keywords, expect_post_processors2[2])

    def test_trigger_with_aetest_loop(self):
        # Get instance of TriggerAetestLoop
        trigger = TriggerAetestLoop()
        uids = [trig.uid for trig in trigger.__loop__]
        expected_uids = ['Test1', 'Test2', 'Test3']
        assert uids == expected_uids, 'uids do not equal expected_uids'

    def test_trigger_with_aetest_loop_different_params(self):
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.subsection_data = self.subsections1
        self.script.triggers = self.trigger_aetest_loop_params    
        
        items = list(self.discoverer)

        for section in items:
            if isinstance(section, CommonSetup) \
                or isinstance(section, CommonCleanup) \
                or isinstance(section, Verifications):
                continue
            iteration = section.parameters['iteration']           
            assert f'iteration_{iteration}' in section.parameters, 'parameter missing'
            assert f'iteration_{iteration-1}' not in section.parameters, f'unexpected parameters present'

    def test_triggers_with_section_parameters(self):
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        # Add triggers information to the script
        self.script.triggers = self.triggers_with_section_parameters
        items = list(self.discoverer)
        items[1]()
        self.assertEqual('This should override', items[1].test_val)
        self.assertEqual('This should be overridden', items[1].test2_val)
        self.assertEqual('This should be overridden', items[1].test3_val)
        self.assertEqual('This should also be overridden', items[1].test3_val2)

    def test_extended_trigger_external_package(self):
        sys.path.append(os.path.dirname(__file__))
        # Add triggers information to the script
        self.script.triggers = self.triggers_external_override

        # Test an existing trigger in an external package is overridden and
        # returned (using pyats.configuration)
        cfg[PYATS_EXT_TRIGGER_CFG_PATH] = "genie.tests.harness.dummy_trigger"
        os.environ['PYATS_LIBS_EXTERNAL_TRIGGER'] = ""

        loaded = self.discoverer._load_item('TriggerSleep',
                                            self.script.triggers,
                                            verification=False,
                                            counter=0)
        self.assertEqual("genie.tests.harness.dummy_trigger.sleep.sleep",
                         loaded[0].__module__)
        self.assertEqual("TriggerSleep", loaded[0].__class__.__name__)


        # Test a new trigger in an external package is found and
        # returned (using env variable)
        cfg[PYATS_EXT_TRIGGER_CFG_PATH] = ""
        os.environ['PYATS_LIBS_EXTERNAL_TRIGGER'] = "genie.tests.harness.dummy_trigger"

        loaded = self.discoverer._load_item('DummyTrigger',
                                            self.script.triggers,
                                            verification=False,
                                            counter=0)
        self.assertEqual(
            "genie.tests.harness.dummy_trigger.dummy_trigger.dummy_trigger",
            loaded[0].__module__)
        self.assertEqual("DummyTrigger", loaded[0].__class__.__name__)


    def test_extended_trigger_entrypoint(self):
        # Add triggers information to the script
        self.script.triggers = self.triggers_external_override

        try:
            import genie.libs.cisco.sdk.triggers
            _dist = pkg_resources.get_distribution("genie.libs.cisco")
            entry_point = load_entry_point(dist=_dist, group=TRIGGER_ENTRY_POINT, name='cisco')
        except ImportError:
            raise unittest.SkipTest(
                "Failed to import genie.libs.cisco.sdk.triggers. "
                "Skipping test as it requires the triggers entry point")

        # Test that the genielibs.cisco entry point is correctly declared
        self.assertEqual(entry_point.__name__, "genie.libs.cisco.sdk.triggers")

        # Now modify the entry point to reference the dummy trigger package
        for entry in iter_entry_points(group=TRIGGER_ENTRY_POINT):
            if entry.name == "cisco":
                entry.module_name = "genie.tests.harness.dummy_trigger"

        # Remove other pointers to the package
        cfg[PYATS_EXT_TRIGGER_CFG_PATH] = ""
        os.environ['PYATS_EXT_TRIGGER_ENV_NAME'] = ""

        loaded = self.discoverer._load_item('TriggerSleep',
                                            self.script.triggers,
                                            verification=False,
                                            counter=0)
        self.assertEqual("genie.tests.harness.dummy_trigger.sleep.sleep",
                         loaded[0].__module__)
        self.assertEqual("TriggerSleep", loaded[0].__class__.__name__)

    def test_parallel_verifications(self):
        # Add triggers information to the script
        self.script.verification_uids = Or('')
        self.script.trigger_uids = Or('')
        self.script.triggers = self.trigger_sleep
        self.script.verifications = self.parallel_verf
        self.script.subsection_data = self.subsections1
        items = list(self.discoverer)

        for expected, item in zip([CommonSetup, 
                                   items[1], # pre verfs
                                   self.trigger_sleep,
                                   items[3], # post verfs
                                CommonCleanup], items):

            try:
                self.assertTrue(isinstance(item, expected))
            except TypeError:
                # Ignore those for now,  callables verifications
                pass

        self.assertEqual(items[1].verifiers[0].uid, 'Verify_1.PE1.1')
        self.assertEqual(items[1].verifiers[1].uid, 'Verify_1.PE2.1')

        uid_expected = ['no_paramed_subsection', 'paramed_subsection']
        for subsection, uid in zip(items[0], uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, Subsection))

        # Pre verfs
        tc = items[1].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'Verify_1.PE1.1')
        self.assertEqual(tc.parameters['uut'], self.dev1)
        self.assertEqual(tc.parameters['parallel_verifications'], True)

        tc = items[1].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'Verify_1.PE2.1')

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[1].verifiers[2]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'Verify_2.PE1.1')
        self.assertEqual(tc.parameters['uut'], self.dev1)
        self.assertEqual(tc.parameters['parallel_verifications'], True)

        tc = items[1].verifiers[3]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'Verify_2.PE2.1')

        # Post verfs
        tc = items[3].verifiers[0]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'Verify_1.PE1.2')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        tc = items[3].verifiers[1]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'Verify_1.PE2.2')

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

        tc = items[3].verifiers[2]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'Verify_2.PE1.2')
        self.assertEqual(tc.parameters['uut'], self.dev1)

        tc = items[3].verifiers[3]
        self.assertEqual(tc.groups, ['L2'])
        self.assertEqual(tc.uid, 'Verify_2.PE2.2')

        uid_expected = ['verify']
        for subsection, uid in zip(tc, uid_expected):
            self.assertEqual(subsection.uid, uid)
            self.assertTrue(isinstance(subsection, TestSection))

    def test_triggers_order_dict(self):
        self.script.triggers = self.triggers_order_dict
        items = list(self.discoverer)
        self.assertEqual(items[1].uid, 'TriggerShutNoShutBgp.PE2')
        self.assertEqual(items[2].uid, 'TriggerShutNoShutOspf.PE2')

    def test_triggers_order_dict_multiple(self):
        self.script.triggers = self.triggers_order_dict_multiple
        items = list(self.discoverer)

        self.assertEqual(items[1].uid, 'TriggerShutNoShutBgp.PE2.1')
        self.assertEqual(items[2].uid, 'TriggerShutNoShutBgp.PE1.2')


if __name__ == '__main__':
    unittest.main()
