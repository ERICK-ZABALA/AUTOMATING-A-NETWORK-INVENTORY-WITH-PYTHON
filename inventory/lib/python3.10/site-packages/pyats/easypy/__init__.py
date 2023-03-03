# metadata
__version__ = '23.2'
__author__ = 'Cisco Systems Inc.'
__contact__ = ['pyats-support@cisco.com', 'pyats-support-ext@cisco.com']
__copyright__ = 'Copyright (c) 2018-2019, Cisco Systems Inc.'

from .main import _default_runtime as runtime, main
from operator import attrgetter as _attrgetter

globals().update((name.split('.')[-1], _attrgetter(name)(runtime))
                 for name in runtime.__all__)

__all__ = ['main', 'runtime']
__all__.extend(name.split('.')[-1] for name in runtime.__all__)
