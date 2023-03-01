#!/usr/bin/env python
""" Unit tests for the traceabledict module within metaparser package. """

import unittest

from genie.metaparser.util.traceabledict import TraceableDict

class TestTraceableDict(unittest.TestCase):
    def setUp(self):

        TraceableDict.tracer = {}

        dic = {'cmp': {'module': {'1': {'bios_compile_time': '2008 19:39:40',
                              'bios_version': '02.01.05',
                              'image_compile_time': '9/25/2011 2:00:00',
                              'image_version': '6.0(1) [build 6.0(0.66)]',
                              'status': 'ok'},
                        '2': {'bios_compile_time': '2008 19:39:40',
                              'bios_version': '02.01.05',
                              'image_compile_time': '9/25/2011 2:00:00',
                              'image_version': '6.0(1) [build 6.0(0.66)]',
                              'status': 'ok'}}},
             'hardware': {'bootflash': '2048256',
                          'chassis': 'Supervisor Module-1X',
                          'cpu': 'Intel(R) Xeon(R)',
                          'device_name': 'PE1',
                          'memory': '8260604',
                          'model': 'Nexus7000 C7009',
                          'processor_board_id': 'JAF1608ADKR',
                          'slot0': '2093273',
                          'slots': '9'},
             'kernel_uptime': {'days': '144',
                               'hours': '22',
                               'minutes': '58',
                               'seconds': '43'},
             'reason': 'Unknown',
             'software': {'bios': 'version 3.22.0',
                          'bios_compile_time': '02/20/10',
                          'kickstart': 'version 6.2(6)',
                          'kickstart_compile_time': '12/5/2013 14:00:00 [2013 '
                                                    '01:54:43]',
                          'kickstart_image_file': 'bootflash:///n7000-2.2.bin',
                          'system': 'version 6.2(6)',
                          'system_compile_time': '12/5/2013 14:00:00 [2013 '
                                                 '03:41:10]',
                          'system_image_file': 'bootflash:///n7000-s1.bin'},
             'system_version': '6.2(6)'}
    
        TraceableDict.tracer[self.__class__.__name__] = set()
    
        self.d = TraceableDict.convert(dic, self.__class__.__name__)

    def test_traceabledict(self):
        self.assertEqual(TraceableDict.tracer, {'TestTraceableDict': set()})
        
        # common way to access
        self.d['hardware']['chassis']
        self.assertEqual(TraceableDict.tracer,
                         {'TestTraceableDict': {('hardware', 'chassis')}})
        
        # indirectly way to access
        temp = self.d['software']
        temp['kickstart']
        self.assertEqual(TraceableDict.tracer,
                         {'TestTraceableDict': {('hardware', 'chassis'), 
                                                ('software', 'kickstart')}})
        
        # test creating a new object and tracer accumulation  
        dict2 = {'hardware': {'bootflash': '2048256',
                              'chassis': 'Supervisor Module-1X',
                              'cpu': 'Intel(R) Xeon(R)',
                              'device_name': 'PE1',
                              'memory': '8260604',
                              'model': 'Nexus7000 C7009',
                              'processor_board_id': 'JAF1608ADKR',
                              'slot0': '2093273',
                              'slots': '9'},}
        self.d2 = TraceableDict.convert(dict2, self.__class__.__name__)
        self.d2['hardware']['cpu']
        self.assertEqual(TraceableDict.tracer,
                         {'TestTraceableDict': {('hardware', 'chassis'),
                                                ('hardware', 'cpu'),
                                                ('software', 'kickstart')}})
        
        # test copy() - should be no change
        self.d3 = self.d.copy()
        self.assertEqual(TraceableDict.tracer,
                         {'TestTraceableDict': {('hardware', 'chassis'),
                                                ('hardware', 'cpu'),
                                                ('software', 'kickstart')}})
        
        # test tracer accumulation after copy()
        self.d3['hardware']['memory']
        self.assertEqual(TraceableDict.tracer,
                            {'TestTraceableDict': {('hardware', 'chassis'),
                                                   ('hardware', 'cpu'),
                                                   ('hardware', 'memory'),
                                                   ('software', 'kickstart')}})
        # test keys()
        self.d3.keys()
        self.assertEqual(TraceableDict.tracer,
                        {'TestTraceableDict': {('cmp',),
                                               ('hardware',),
                                               ('hardware', 'chassis'),
                                               ('hardware', 'cpu'),
                                               ('hardware', 'memory'),
                                               ('kernel_uptime',),
                                               ('reason',),
                                               ('software',),
                                               ('software', 'kickstart'),
                                               ('system_version',)}})
        
        # test values()
        self.d3['kernel_uptime'].values()
        self.assertEqual(TraceableDict.tracer,
                         {'TestTraceableDict': {('cmp',),
                                                ('hardware',),
                                                ('hardware', 'chassis'),
                                                ('hardware', 'cpu'),
                                                ('hardware', 'memory'),
                                                ('kernel_uptime',),
                                                ('kernel_uptime', 'days'),
                                                ('kernel_uptime', 'hours'),
                                                ('kernel_uptime', 'minutes'),
                                                ('kernel_uptime', 'seconds'),
                                                ('reason',),
                                                ('software',),
                                                ('software', 'kickstart'),
                                                ('system_version',)}})
        # test items()
        self.d3['cmp'].items()
        self.assertEqual(TraceableDict.tracer,
                         {'TestTraceableDict': {('cmp',),
                                                ('cmp', 'module'),
                                                ('hardware',),
                                                ('hardware', 'chassis'),
                                                ('hardware', 'cpu'),
                                                ('hardware', 'memory'),
                                                ('kernel_uptime',),
                                                ('kernel_uptime', 'days'),
                                                ('kernel_uptime', 'hours'),
                                                ('kernel_uptime', 'minutes'),
                                                ('kernel_uptime', 'seconds'),
                                                ('reason',),
                                                ('software',),
                                                ('software', 'kickstart'),
                                                ('system_version',)}})
        # test pop()
        self.d3['cmp']['module']['1'].pop('status')
        self.assertEqual(TraceableDict.tracer,
                     {'TestTraceableDict': {('cmp',),
                                            ('cmp', 'module'),
                                            ('cmp', 'module', '1', 'status'),
                                            ('hardware',),
                                            ('hardware', 'chassis'),
                                            ('hardware', 'cpu'),
                                            ('hardware', 'memory'),
                                            ('kernel_uptime',),
                                            ('kernel_uptime', 'days'),
                                            ('kernel_uptime', 'hours'),
                                            ('kernel_uptime', 'minutes'),
                                            ('kernel_uptime', 'seconds'),
                                            ('reason',),
                                            ('software',),
                                            ('software', 'kickstart'),
                                            ('system_version',)}})
        
        # test get()
        self.d3['cmp']['module']['2'].get('image_version')
        self.assertEqual(TraceableDict.tracer,
             {'TestTraceableDict': {('cmp',),
                                    ('cmp', 'module'),
                                    ('cmp', 'module', '2', 'image_version'),
                                    ('cmp', 'module', '1', 'status'),
                                    ('hardware',),
                                    ('hardware', 'chassis'),
                                    ('hardware', 'cpu'),
                                    ('hardware', 'memory'),
                                    ('kernel_uptime',),
                                    ('kernel_uptime', 'days'),
                                    ('kernel_uptime', 'hours'),
                                    ('kernel_uptime', 'minutes'),
                                    ('kernel_uptime', 'seconds'),
                                    ('reason',),
                                    ('software',),
                                    ('software', 'kickstart'),
                                    ('system_version',)}})
