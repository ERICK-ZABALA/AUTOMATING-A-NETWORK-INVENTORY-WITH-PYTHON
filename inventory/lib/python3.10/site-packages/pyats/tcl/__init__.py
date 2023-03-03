'''
Module:
    tcl

Authors:
    Siming Yuan (siyuan), CSG Test - Ottawa

Description:
    This module provides a standard way for users to access Tcl code/libraries
    when using the python ATS infrastructure.

    This module requires environment variable AUTOTEST to be set to user's
    Tcl ATS tree for proper ATS Tcl functionalities to work.

    It acts as a wrapper to Python's Tkinter module, and in addition provides
    standard typecasting for easy conversion from Tcl string to python native
    objects.

    By default, this module provides one managed interpreter.

'''

# metadata
__version__ = '23.2'
__author__ = 'Cisco Systems'
__contact__ = 'pyats-support-ext@cisco.com'
__copyright__ = 'Copyright (c) 2017-2019, Cisco Systems Inc.'

# check whether tkinter is loadable first
try:
    from tkinter import TclError
except ImportError as e:
    # suppress the libtk8.4.so warning as it doesn't make sense to the user
    raise ImportError('Cannot use %s module when tkinter module cannot '
                      'be imported.' % __name__) from e

# only proceed with import from this module if tkinter loadable
from .interpreter import Interpreter, _global_interpreter
from .array import Array
from .keyedlist import KeyedList
from .tclstr import tclstr, tclobj
from .history import History, Entry
from .namespace import *

globals().update((name.split('.')[-1], getattr(_global_interpreter, name))
                 for name in _global_interpreter.__all__)
