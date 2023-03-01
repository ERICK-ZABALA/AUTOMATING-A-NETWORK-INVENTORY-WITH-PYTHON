import unittest
from genie.harness.base import Trigger, TestcaseVerification,\
                               LocalVerification

class TestBase(unittest.TestCase):

    # So far,  that's all to test.
    # They got nothing else!
    def test_init(self):
        trigger = Trigger()
        tcV = TestcaseVerification()
        lVer = LocalVerification(lambda: x)

if __name__ == '__main__':
    unittest.main()
