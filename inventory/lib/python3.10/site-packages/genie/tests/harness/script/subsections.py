from pyats import aetest

import sys,os
sys.path.append(os.path.dirname(__file__))


@aetest.subsection
def without_param(self, testbed, testscript):
    pass

@aetest.subsection
def with_param(self, testbed, testscript, param1, param2):
    pass

@aetest.subsection
def cleanup_without_param(self, testbed, testscript):
    pass

@aetest.subsection
def cleanup_with_param(self, testbed, testscript, param1, param2):
    pass
