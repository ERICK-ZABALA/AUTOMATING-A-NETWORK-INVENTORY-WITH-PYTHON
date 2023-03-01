import sys
import logging
import functools
import importlib.util

from .decorator import mixedmethod

log = logging.getLogger(__name__)


class Base(object):
    '''Base class for all genie objects

    Base class for all objects of the genie infrastructure.
    '''

    def __init__(self, **kwargs):
        '''Initialize the object.

        All keyword arguments (kwargs) will be set as attributes of the object.
        '''
        for key, value in kwargs.items():
            setattr(self, key, value)
        # The below super call (in some cases) calls ats/topology/testbed
        # object where we need to pass tb name that's why we pass the kwargs
        # which includes the tb name passed.
        try:
            super().__init__(**kwargs)
        except TypeError:
            super().__init__()

    def __repr__(self):
        '''Implement repr(self).

        If available, the 'name' attribute of the object will be included.
        '''
        try:
            name = self.name
        except:
            return '<%s object at 0x%x>' % (
                self.__class__.__name__,
                id(self))
        else:
            return '<%s object %r at 0x%x>' % (
                self.__class__.__name__,
                name,
                id(self))

# vim: ft=python et sw=4
