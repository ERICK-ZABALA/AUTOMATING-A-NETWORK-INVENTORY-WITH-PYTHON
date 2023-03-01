import collections

from pyats.datastructures import AttrDict

from pyats.utils.yaml import Loader
from pyats.utils.dicts import recursive_cast

from .schema import config_schema

# declare module as infra
__genietelemetry_infra__ = True

class ConfigLoader(Loader):
    def __init__(self):
        super().__init__(schema = config_schema,
                         enable_extensions = True,
                         postprocessor = self.postprocessor)

    def postprocessor(self, content):
        # remove extends key
        content.pop('extends', None)

        # convert everything to AttrDict
        # (cuz i like it ...)
        return recursive_cast(content, AttrDict)
