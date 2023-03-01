from pyats import aetest
from genie.harness.discovery import GenieScriptDiscover

aetest.runtime.discoverer.script = GenieScriptDiscover

if __name__ == '__main__':
    aetest.main()
