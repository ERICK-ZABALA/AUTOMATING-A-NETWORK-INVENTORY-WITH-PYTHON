from pyats import aetest
from pyats.aetest.loop import Iteration
from genie.harness.base import Trigger

def prepostprocessor(section):
    pass

def processorwithparam(section, param1):
    pass

def exceptionprocessor(section, exc_type, exc_value, exc_traceback):
    pass

class TriggerShutNoShutBgp(Trigger):
    @aetest.test
    def test1(self):
        pass

class TriggerShutNoShutOspf(Trigger):
    @aetest.test
    def test1(self):
        pass
    @aetest.test
    def test2(self):
        pass

class Bad(object):
    @aetest.test
    def test1(self):
        pass

class Wrong(object):
    pass

class TriggerBgpNoSetupCleanup(Trigger):
    @aetest.test
    def test1(self):
        pass
    @aetest.test
    def test2(self):
        pass

class TriggerOspfWtSetupCleanup(Trigger):
    @aetest.setup
    def test_setup(self):
        pass
    @aetest.test
    def test1(self):
        pass
    @aetest.cleanup
    def test_cleanup(self):
        pass

class TriggerHsrpWtSetup(Trigger):
    @aetest.setup
    def test_setup(self):
        pass
    @aetest.test
    def test1(self):
        pass

class TriggerVlanWtCleanup(Trigger):
    @aetest.test
    def test1(self):
        pass
    @aetest.cleanup
    def test_cleanup(self):
        pass

class TriggerIsisBasic(Trigger):
    pass

class TriggerWtJustSetupCleanup(Trigger):
    @aetest.setup
    def test_setup(self):
        pass
    @aetest.cleanup
    def test_cleanup(self):
        pass

class TriggerMixedOrder(Trigger):
    @aetest.test
    def test1(self):
        pass
    @aetest.test
    def test2(self):
        pass
    @aetest.cleanup
    def test_cleanup(self):
        pass
    @aetest.setup
    def test_setup(self):
        pass

class TriggerNoDecorator(Trigger):
    @aetest.setup
    def test_setup(self):
        pass
    # test without decorator
    def test1(self):
        pass
    @aetest.test
    def test2(self):
        pass
    @aetest.cleanup
    def test_cleanup(self):
        pass

@aetest.loop(uids=['Test1', 'Test2', 'Test3'])
class TriggerAetestLoop(Trigger):
    @aetest.test
    def test(self):
        pass

class TestCaseGenerator(object):
    def __init__(self, loopee):
        pass

    def __iter__(self):
        for i in range(1, 3):
            yield Iteration(uid=f'test_{i}',
                            parameters={'iteration': i,
                                        f'iteration_{i}': True})

@aetest.loop(generator=TestCaseGenerator)
class TriggerAetestLoopParams(Trigger):
    @aetest.test
    def test(self):
        pass

class TriggerSectionWithParameters(Trigger):
    @aetest.test
    def test(self, val):
        self.test_val = val

    @aetest.test
    def test2(self, val):
        self.test2_val = val

    @aetest.test
    def test3(self, val2, val='override this'):
        self.test3_val = val
        self.test3_val2 = val2
