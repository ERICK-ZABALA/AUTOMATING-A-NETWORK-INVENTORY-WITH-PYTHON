#!/bin/env python
###################################################################
# basic_example.py : A very simple test script example which include:
#     common_setup
#     Tescases
#     common_cleanup
# The purpose of this sample test script is to show the "hello world"
# of aetest.
###################################################################

# To get a logger for the script
import logging
import sys, os

# Needed for aetest script
from pyats import aetest
sys.path.append(os.path.dirname(__file__))
# Genie Imports
from genie.harness.standalone import run_genie_sdk, GenieStandalone
from genie.conf import Genie

# Verifications classes and template class which is used for verifications
# using parser or Genie Ops.

# Get your logger for your script
log = logging.getLogger(__name__)

###################################################################
###                  COMMON SETUP SECTION                       ###
###################################################################

# This is how to create a CommonSetup
# You can have one of no CommonSetup
# CommonSetup can be named whatever you want

class common_setup(aetest.CommonSetup):
    """ Common Setup section """

    @aetest.subsection
    def connect(self, testbed):
        # pass
        genie_testbed = Genie.init(testbed)
        self.parent.parameters['testbed'] = genie_testbed
        uut = genie_testbed.devices['uut']
        r2 = genie_testbed.devices['P1']
        uut.connect(via='cli')
        r2.connect(via='cli')

    # If you want to get the name of current section,
    # add section to the argument of the function.


###################################################################
###                     TESTCASES SECTION                       ###
###################################################################


# You can also call Triggers and Verifications within a pyATS section
class tc_pyats_genie(aetest.Testcase):
    # First test section
    @ aetest.test
    def simple_test_1(self, steps):
        """ Sample test section. Only print """
        log.info("First test section ")

        # Run genie triggers and verifications
        run_genie_sdk(self, steps,
                      ['TriggerSleep', 'TriggerShutNoShutLoopbackInterface',
                       'TriggerSleep',], parameters={
                'TriggerSleep': {'devices': ['uut', 'P1'], 'sleep_time': 2},
                'TriggerShutNoShutLoopbackInterface': {
                    'devices': ['uut', 'P1'],
                    'static': {'interface': 'Loopback0'},
                    'count': 2,
                    'timeout': {
                        'max_time': 20,
                        'interval': 10
                    }
                }
                        })

class tc_pyats_genie_verification(aetest.Testcase):
    """ This is user Testcases section """

    # This is how to create a setup section
    @aetest.setup
    def simple_test_2(self, steps, section):
        """ Testcase Setup section """
        log.info("Second test section ")
        run_genie_sdk(self, steps,
                      ['Verify_IpInterface'], parameters={
                'Verify_IpInterface': {'devices': ['uut', 'P1'], 'count': 2}})


#####################################################################
####                 Genie Harness information                    ###
#####################################################################

# Run verification
# Enter the name of the verification name which
# matches the one in the datafile.
#
# class Verify_bgp(GenieStandalone):
#     verifications = ['Verify_BgpVrfAllAll']
#
# class TriggerSleep(GenieStandalone):
#     triggers = ['TriggerSleep']
#
class TriggerSleep(GenieStandalone):
    '''Custom arguments can be provided to overwrite the datafile information'''
    triggers = ['TriggerSleep','TriggerShutNoShutLoopbackInterface']
    custom_arguments = {'TriggerSleep': {'devices': ['uut', 'P1'], 'sleep_time': 2, 'count':2},
                        'TriggerShutNoShutLoopbackInterface': {
                            'devices': ['uut', 'P1'],
                            'static': {'interface': 'Loopback0'},
                            'count': 2,
                            'timeout': {
                                'max_time':20,
                                'interval':10
                            }
                            }
                        }

class Trigger_verification(GenieStandalone):
    verifications = ['Verify_IpInterface']

    custom_arguments = {'Verify_IpInterface': {'devices': ['uut', 'P1'], 'count': 2}}



#####################################################################
####                       COMMON CLEANUP SECTION                 ###
#####################################################################

# This is how to create a CommonCleanup
# You can have 0 , or 1 CommonCleanup.
# CommonCleanup can be named whatever you want :)
class common_cleanup(aetest.CommonCleanup):
    """ Common Cleanup for Sample Test """

    # CommonCleanup follow exactly the same rule as CommonSetup regarding
    # subsection
    # You can have 1 to as many subsections as wanted
    # here is an example of 1 subsection

    @aetest.subsection
    def clean_everything(self):
        """ Common Cleanup Subsection """
        log.info("Aetest Common Cleanup ")

if __name__ == '__main__': # pragma: no cover
    aetest.main()
