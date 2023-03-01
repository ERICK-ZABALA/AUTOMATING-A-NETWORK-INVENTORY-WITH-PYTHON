#!/bin/env python
""" Unit tests for the data files schema within genie package"""

import unittest, yaml
from pyats import aetest
from pyats.utils.schemaengine import Schema, SchemaTypeError
from genie.harness.datafile.schema import mappingdatafile_schema,\
                    triggerdatafile_schema,\
                    verificationdatafile_schema,\
                    configdatafile_schema,\
                    ptsdatafile_schema, \
                    subsectiondatafile_schema

def pre_processor(section):
    pass
def post_processor(section):
    pass
def exception_processor(section, exc_type, exc_value, exc_traceback):
    pass

@aetest.subsection
def subsection(self, testbed, testscript, param1, param2):
    pass

@aetest.subsection
def subsection_without_params(self):
    pass

class TestSchemaEngine(unittest.TestCase):

    def test_mapping_data_file_schema(self):

        schema = Schema(mappingdatafile_schema)

        data = yaml.safe_load('''
                        parameters:
                            param1: a
                            param2: b
                        variables:
                            vars1: c
                            vars2: d
                        devices:
                            uut:
                               context: cli
                               pool_size: 5
                               label: uut
                               mapping:
                                 cli: vty
                                 yang: netconf
                        ''')
        schema.validate(data)

        data = yaml.safe_load('''
                        devices:
                            uut:
                               context: cli
                               pool_size: 5
                               label: uut
                               mapping:
                                 cli: vty
                                 yang: netconf
                        topology:
                            links:
                                link1:
                                    label: superlink
                            uut:
                                interfaces:
                                    int1:
                                        label: abc
                        ''')
        schema.validate(data)

        schema = Schema(mappingdatafile_schema)

        data = yaml.safe_load('''
                        devices:
                            uut:
                               context: cli
                               netconf_pool_size: 1
                               pool_size: 5
                               label: uut
                               mapping:
                                 cli: vty
                                 yang: netconf
                        ''')
        schema.validate(data)

        data = yaml.safe_load('''
                                devices:
                                    uut:
                                      mapping:
                                         context:
                                           cli:
                                            - via: cli
                                              alias: cli
                                            - via: ssh
                                              alias: ssh
                                  ''')
        schema.validate(data)

        data = yaml.safe_load('''
                                        devices:
                                            uut:
                                              mapping:
                                                 context:
                                                   cli:
                                                    - via: cli
                                                      alias: cli
                                                    - via: ssh
                                                      alias: ssh
                                                   yang:
                                                    - via: ssh
                                                      alias: banana
                                                    - via: netconf
                                                      alias: orange
                                          ''')
        schema.validate(data)

    def test_config_data_file_schema(self):

        schema = Schema(configdatafile_schema)

        data = yaml.safe_load('''
                        parameters:
                            param1: a
                            param2: b
                        variables:
                            vars1: c
                            vars2: d
                        devices:
                            uut:
                                1:
                                  config: /ws/karmoham-sjc/pyats/uut_config
                                  sleep: 3
                                  invalid: []
                                  vrf: management
                        ''')

        wrong_data = yaml.safe_load('''
                        devices:
                            uut:
                                1:
                                  config: /ws/karmoham-sjc/pyats/uut_config
                                  sleep: '3'
                                  invalid: []
                        ''')

        schema.validate(data)
        with self.assertRaises(SchemaTypeError):
            schema.validate(wrong_data)

    def test_trigger_data_file_schema(self):

        schema = Schema(triggerdatafile_schema)

        data = yaml.safe_load('''
                    parameters:
                        param1: a
                        param2: b
                    variables:
                        vars1: c
                        vars2: d
                    TriggerSleepBgp:
                        source:
                            pkg: genie_libs
                            class: sdk.triggers.sleep.bgp.sleep.TriggerSleepBgp
                        groups: ['L3']
                        devices: ['uut']
                        sleep_time: 10
                        message_time: 5
                        processors:
                          pre:
                            pre_sleep:
                                pkg: genie
                                method: harness.datafile.tests.test_schema.pre_processor
                          post:
                            post_sleep:
                                pkg: genie_libs
                                method: harness.datafile.tests.test_schema.post_processor
                          exception:
                            exception_sleep:
                                pkg: genie_libs
                                method: harness.datafile.tests.test_schema.exception_processor
                        verifications:
                            verif_1:
                                devices: ['uut']
                                parameters:
                                    param1: a
                                    param2: b
                    ''')

        schema.validate(data)

    def test_verification_data_file_schema(self):

        schema = Schema(verificationdatafile_schema)

        data = yaml.safe_load('''
                        parameters:
                            param1: a
                            param2: b
                        variables:
                            vars1: c
                            vars2: d
                        Verify_Ospf:
                            source:
                                pkg: genie_libs
                                class: ops.ospf.ospf.Ospf
                            exclude: [age, cksum, last_change, advrouter]
                            sleep_time: 5
                            message_time: 6
                            processors:
                              pre:
                                pre_sleep:
                                    pkg: genie
                                    method: harness.datafile.tests.test_schema.pre_processor
                              post:
                                post_sleep:
                                    pkg: genie_libs
                                    method: harness.datafile.tests.test_schema.post_processor
                              exception:
                                exception_sleep:
                                    pkg: genie_libs
                                    method: harness.datafile.tests.test_schema.exception_processor
                            parameters:
                                param1: a
                                param2: b
                        ''')

        schema.validate(data)

    def test_pts_data_file_schema(self):

        schema = Schema(ptsdatafile_schema)

        data = yaml.safe_load('''
                        parameters:
                            param1: a
                            param2: b
                        variables:
                            vars1: c
                            vars2: d
                        ospf:
                            # By default, uses uut, but more can be passed
                            source:
                                pkg: genie_libs
                                class: ops.ospf.ospf.Ospf
                            exclude:
                                - last_change
                                - age
                                - cksum
                                - seq
                                - uptime
                        ''')

        schema.validate(data)

    def test_subsection_data_file_schema(self):

        schema = Schema(subsectiondatafile_schema)

        data = yaml.safe_load('''
        parameters:
            param1: a
            param2: b
        variables:
            vars1: c
            vars2: d
        setup:
            sections:
              my_own_common_setup:
                method: genie.harness.datafile.tests.test_schema.subsection
                parameters:
                  param1 : a
                  param2 : b
            order: ['configure', 'my_own_common_setup']

        cleanup:
            sections:
              my_own_common_cleanup:
                method: genie.harness.datafile.tests.test_schema.subsection
                parameters:
                  param1 : a
                  param2 : b
            order: ['my_own_common_cleanup']
                        ''')

        schema.validate(data)

if __name__ == "__main__":
    unittest.main()
