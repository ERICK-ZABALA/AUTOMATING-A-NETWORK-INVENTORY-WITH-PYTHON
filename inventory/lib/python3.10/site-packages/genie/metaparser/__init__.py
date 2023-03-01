__copyright__ = 'Cisco Systems, Inc. Cisco Confidential'

import re
from ._metaparser import *

_IMPORTMAP = {
    re.compile(r'^metaparser(?=$|\.)'): 'genie.metaparser'
}

