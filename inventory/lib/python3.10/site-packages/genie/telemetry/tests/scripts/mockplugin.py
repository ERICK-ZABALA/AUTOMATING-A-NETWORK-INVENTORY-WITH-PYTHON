
from unittest.mock import Mock
from genie.telemetry import BasePlugin
from genie.telemetry.status import PARTIAL

class Plugin(BasePlugin):

    parser = None
    def parse_args(self, *args, **kwargs):
        return

    def execution(self, device):
        return PARTIAL('mocked plugin result')