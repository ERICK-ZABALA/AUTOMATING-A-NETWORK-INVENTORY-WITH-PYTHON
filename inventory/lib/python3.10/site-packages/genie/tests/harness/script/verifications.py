import random
from genie.ops.base import Base

class VerifyOps(Base):
    '''Template for quick ops'''

    def __init__(self, some_args, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.some_args = some_args

    def learn(self):
        '''Learn Ospf object'''
        pass


def a_callable_always_same(self, var1, name, *args, **kwargs):
    return {'value':var1}


def a_callable_always_same2(self, var1, name, *args, **kwargs):
    return {'value':var1}


def a_callable(self, var1, *args, **kwargs):
    self.x = random.random()
    return {'value':self.x}


def a_failing_callable(self, var1, *args, **kwargs):
    assert False, 'False callable'


def a_error_callable(self, *args, **kwargs):
    qwe


def a_missing_arg_callable(self, var1, missing, *args, **kwargs):
    pass


class Wrong(object):
    pass


class VerifyOpsWithParameters(Base):
    '''Template for quick ops'''

    def __init__(self, some_args, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.some_args = some_args

    def learn(self, missing):
        '''Learn Ospf object'''
        pass