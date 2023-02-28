import warnings

from ..log import *

warnings.warn(message = '''
********************************************************************************
*                                   WARNING                                    *
********************************************************************************
     ats.atslog module is now renamed to ats.log:
         from ats.atslog import x   -->   from ats.log import x
         from ats import atslog     -->   from ats import log
         import ats.atslog          -->   import ats.log

     The following command can make this change recursively.
         grep -rl "atslog" * | xargs sed -i "s/atslog/log/g"

     This command is very powerful. USE WITH CAUTION.
********************************************************************************
''',
category = DeprecationWarning)
