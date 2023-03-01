from pyats import aetest

import sys,os
sys.path.append(os.path.dirname(__file__))

# import everything from base - this shouldn't affect lookup
from testScriptBase import *

class common_setup(aetest.CommonSetup):
    pass

class testcase(aetest.Testcase):
    pass

class common_cleanup(aetest.CommonCleanup):
    pass

if __name__ == '__main__':
    aetest.main()
