import sys

from .implementation import RuntimeInfo
sys.modules[__name__] = runtime = RuntimeInfo()

# hardwire all module hidden attributes to runtime instance
runtime.__file__    = __file__
runtime.__loader__  = __loader__
runtime.__package__ = __package__
runtime.__name__    = __name__
runtime.__spec__    = __spec__
runtime.__doc__     = __doc__
