# declare module as infra
__aetest_infra__ = True

from .decorator import discover_global_processors

# this is the api user will use
# eg:
#   @processors(pre = [func,])
#   def test(self): pass
from .decorator import ProcessorDecorator as processors


from .skips import skip, skipIf, skipUnless
