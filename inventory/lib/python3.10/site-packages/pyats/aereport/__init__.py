'''
    Module:
        AEReport

    Authors:
        Ahmad Barghout (abarghou), CSG Test - Ottawa
        Jean-Benoit Aubin (jeaubin), CSG Test - Ottawa

    Description:
        This module provide a mechanism to record logical test events, data,
        and results for storing and serialization into XML.

        In Python ATS infrastructure, XML-RPC server infrastructure is used to
        allow multiple users, runs in parallel or testcase in parallel.

    Notes:
'''

# metadata
__version__ = '23.2'
__author__ = 'Cisco Systems Inc.'
__contact__ = ['pyats-support@cisco.com', 'pyats-support-ext@cisco.com']
__copyright__ = 'Copyright (c) 2017-2019, Cisco Systems Inc.'


class LoggingMode (object):
    """
    Provide the available modes for logging.
    """
    SingleFile, FilePerTestcase = list(range(0,2))
