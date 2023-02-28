'''
This file only exists for backwards compatibility purposes if the user is
in Python versions older than 3.7

Leaving it for Python 3.7 has zero side effects.
'''

import sys
from pyats import async_

from pyats.utils.import_utils import LegacyImporter

LegacyImporter.register(**{'pyats.async': 'pyats.async_'})
LegacyImporter.install()

sys.modules['pyats.async'] = async_
