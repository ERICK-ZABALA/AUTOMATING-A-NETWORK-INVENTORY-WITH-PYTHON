import sys

from pyats.utils.import_utils import LegacyImporter

LegacyImporter.register(ats = 'pyats')
LegacyImporter.install()

sys.modules['_ats'] = sys.modules['ats']
sys.modules['ats'] = __import__('pyats')
