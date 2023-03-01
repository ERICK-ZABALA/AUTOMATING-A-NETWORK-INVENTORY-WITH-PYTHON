# ATS
from pyats import aetest

from . import _commons_internal

# subsections for common_setup
@aetest.subsection
def connect(self, testbed, steps):
    '''Connect all the devices defined in mapping file'''
    return _commons_internal.connect(self, testbed, steps)

@aetest.subsection
def disconnect(self, testbed, steps):
    '''Connect all the devices defined in mapping file'''
    return _commons_internal.disconnect(self, testbed, steps)

@aetest.subsection
def configure(self, testbed, steps):
    '''Configure the devices'''
    return _commons_internal.configure(self, testbed, steps)

@aetest.subsection
def check_config(self, testbed, testscript, steps, devices=None, include_os=None,
                 exclude_os=None, include_devices=None, exclude_devices=None):
    '''Take snapshot of configuration for each devices'''
    return _commons_internal.check_config(self, testbed, testscript, steps,
                                          devices, include_os, exclude_os,
                                          include_devices, exclude_devices)

@aetest.subsection
def initialize_traffic(self, testbed, steps):
    '''Connect to TGN device, load configuration, start protocols and traffic'''
    conn_class_name = None
    for dev in testbed.find_devices(type='tgn'):
        for con in dev.connections:
            try:
                conn_class_name = dev.connections[con]['class'].__name__
            except:
                continue
    if conn_class_name == 'GenieTgn':
        return _commons_internal.initialize_traffic_tcl(self, testbed, steps)
    return _commons_internal.initialize_traffic(self, testbed, steps)

@aetest.subsection
def profile_traffic(self, testbed, steps):
    '''Connect to TGN device, create traffic profile, compare to golden profile'''
    return _commons_internal.profile_traffic(self, testbed, steps)

# subsections for common_cleanup
@aetest.subsection
def check_post_config(self, testbed, testscript, steps, configs=None):
    '''Verify the configuration for the devices has not changed'''
    return _commons_internal.check_post_config(self, testbed, testscript,
                                               steps, configs)

# subsections for common_cleanup
@aetest.subsection
def stop_traffic(self, testbed, steps):
    '''Connect to TGN device, stop protocols and traffic'''
    conn_class_name = None
    for dev in testbed.find_devices(type='tgn'):
        for con in dev.connections:
            try:
                conn_class_name = dev.connections[con]['class'].__name__
            except:
                continue
    if conn_class_name == 'GenieTgn':
        return _commons_internal.stop_traffic_tcl(self, testbed, steps)
    return _commons_internal.stop_traffic(self, testbed, steps)


class ProfileSystem(object):

    @aetest.subsection
    def ProfileSystem(self, feature, container, testscript, testbed, steps):
        return _commons_internal.ProfileSystem.ProfileSystem(self, feature,
                                                            container,
                                                            testscript, testbed,
                                                            steps)

# subsections for common_cleanup
@aetest.subsection
def delete_plugin(self, testbed, testscript, steps):
    '''Delete all the plugins associated with the device during the run'''
    return _commons_internal.delete_plugin(self, testbed, testscript,
                                               steps)