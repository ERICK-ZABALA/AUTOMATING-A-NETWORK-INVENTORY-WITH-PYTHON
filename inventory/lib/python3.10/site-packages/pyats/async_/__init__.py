'''
Module:
    async_

Authors:
    Siming Yuan (siyuan), CSG Test - Ottawa

'''

# metadata
__version__ = '23.2'
__author__ = 'Cisco Systems Inc.'
__contact__ = ['pyats-support@cisco.com', 'pyats-support-ext@cisco.com']
__copyright__ = 'Copyright (c) 2017-2019, Cisco Systems Inc.'


from .parallelcall import Pcall

pcall = Pcall.pcall
