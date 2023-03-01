import datetime
import unittest

from genie.metaparser import MetaParser
from genie.metaparser.util.schemaengine import Any

from genie.ops.base import Base
from genie.conf.base import Device
from genie.conf.base import Testbed


class FakeParserSchema(MetaParser):
    """Fake parser schema for test"""

    schema = {Any(): Any()}


class FakeParser_1(FakeParserSchema):
    """Fake parser for unit tests"""

    def cli(self):
        return {"l1_a": "a"}


class FakeParser_2(FakeParserSchema):
    """Fake parser for unit tests"""

    def cli(self):
        return {
            "l1_a": "a",
            "l1_b": "b"
        }


class FakeParser_3(FakeParserSchema):
    """Fake parser for unit tests"""

    def cli(self):
        return {
            "l1_a": {
                "l2_a": "aa",
                "l2_ab": "ab"
            },
            "l1_b": {
                "l2_bb": "ba",
                "l2_c": "bc"
            },
        }


class FakeParser_4(FakeParserSchema):
    """Fake parser for unit tests"""
    def cli(self):
        return {
            "l1_a": {
                "l2_a": "aa",
                "l2_ab": "ab"
            },
            "l1_b": {
                "l2_bb": "ba",
                "l2_c": "bc",
                "l2_d": {
                    "l3_d": "ff"
                }
            },
        }


class FakeParser_5(FakeParserSchema):
    """Fake parser for unit tests"""
    cli_command = 'fakeparser_5'

    def cli(self):
        return {"l1_a": "a"}


class test_base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.testbed = Testbed()
        cls.dev1 = Device(name="pe1", testbed=cls.testbed, os="nxos")

    class Feature(Base):
        cli_1 = {"l1_a": "a"}
        cli_2 = {"l1_a": "a", "l1_b": "b"}
        cli_3 = {
            "l1_a": {"l2_a": "aa", "l2_ab": "ab"},
            "l1_b": {"l2_bb": "ba", "l2_c": "bc"},
        }
        cli_4 = {
            "l1_a": {"l2_a": "aa", "l2_ab": "ab"},
            "l1_b": {"l2_bb": "ba", "l2_c": "bc", "l2_d": {"l3_d": "ff"}},
        }

        def learn(self):
            self.maker.outputs[FakeParser_1] = {"": self.cli_1}
            self.maker.outputs[FakeParser_2] = {"": self.cli_2}
            self.maker.outputs[FakeParser_3] = {"": self.cli_3}
            self.maker.outputs[FakeParser_4] = {"": self.cli_4}

            self.at = "level2"

            self.add_leaf(
                cmd=FakeParser_2, src="[l1_a]", dest="l1_a[level2][level3][l1_a]"
            )

            self.add_leaf(
                cmd=FakeParser_2, src="[l1_b]", dest="l1_a[level2][level3][l1_b]"
            )

            self.add_leaf(cmd=FakeParser_3, src="[l1_a]", dest="two[{self.at}][level3]")

            self.add_leaf(
                cmd=FakeParser_3,
                src="(?P<first>.*)[(?P<second>.*)]",
                dest="three[(?P<second>.*)][(?P<first>.*)][{self.at}]",
            )
            self.make()

    class FeatureWithRawData(Base):
        exclude = []

        def __init__(self, *args, **kwargs):
            kwargs.update({'raw_data': True})
            super().__init__(*args, **kwargs)

        def learn(self):
            self.add_leaf(
                cmd=FakeParser_5, src="[l1_a]", dest="info[l1_a]"
            )

            self.make()

    def test_equal(self):

        f = self.Feature(device=self.dev1)
        g = self.Feature(device=self.dev1)
        f.learn()
        g.learn()

        self.assertEqual(f, g)

        diff = f.diff(g)
        self.assertEqual(str(diff), "")

        diff = g.diff(f)
        self.assertEqual(str(diff), "")

    def test_not_equal_1(self):

        f = self.Feature(device=self.dev1)
        g = self.Feature(device=self.dev1)
        f.learn()
        g.learn()
        g.new = True

        self.assertNotEqual(f, g)

        diff = f.diff(g)
        self.assertEqual(str(diff), "-new: True")

        diff = g.diff(f)
        self.assertEqual(str(diff), "+new: True")

    def test_not_equal_2(self):

        f = self.Feature(device=self.dev1)
        g = self.Feature(device=self.dev1)
        f.learn()
        g.learn()
        g.new = True
        f.new = False

        self.assertNotEqual(f, g)

        diff = f.diff(g)
        self.assertEqual(str(diff), "-new: True\n+new: False")

        diff = g.diff(f)
        self.assertEqual(str(diff), "-new: False\n+new: True")

    def test_equal_remove_attributes_1(self):

        f = self.Feature(device=self.dev1)
        g = self.Feature(device=self.dev1)
        f.learn()
        g.learn()

        f.diff_ignore.append("two[(.*)][level3][(.*)]")

        self.assertNotEqual(f, g)

        diff = f.diff(g)
        self.maxDiff = None
        self.assertEqual(
            sorted(str(diff)),
            sorted(" two:\n  level2:\n   level3:\n-   l2_a: aa\n-   l2_ab: ab"),
        )

        diff = g.diff(f)
        self.assertEqual(
            sorted(str(diff)),
            sorted(" two:\n  level2:\n   level3:\n+   l2_a: aa\n+   l2_ab: ab"),
        )

    def test_equal_remove_attributes_2(self):

        f = self.Feature(device=self.dev1)
        g = self.Feature(device=self.dev1)
        f.learn()
        g.learn()

        f.diff_ignore.append("two[(.*)][level3][(.*)]")
        g.diff_ignore.append("two[(.*)][level3][(.*)]")

        self.assertEqual(f, g)

        diff = f.diff(g)
        self.assertEqual(str(diff), "")

        diff = g.diff(f)
        self.assertEqual(str(diff), "")

    def test_equal_remove_attributes_3(self):

        f = self.Feature(device=self.dev1)
        g = self.Feature(device=self.dev1)
        f.learn()
        g.learn()

        f.diff_ignore.append("(.*)")
        g.diff_ignore.append("(.*)")

        self.assertEqual(f, g)

        diff = f.diff(g)
        self.assertEqual(str(diff), "")

        diff = g.diff(f)
        self.assertEqual(str(diff), "")

    def test_equal_remove_attributes_4(self):
        f = self.Feature(device=self.dev1)
        g = self.Feature(device=self.dev1)
        f.learn()
        g.learn()

        f.diff_ignore.append("(.*)")

        self.assertNotEqual(f, g)

        diff = f.diff(g)
        self.assertEqual(
            sorted(str(diff)),
            sorted(
                "-at: level2\n-attributes: None\n-commands: None\n-connections: None\n-context_manager:\n-l1_a:\n- level2:\n-  level3:\n-   l1_a: a\n-   l1_b: b\n-raw_data: False\n-three:\n- l2_a:\n-  l1_a:\n-   level2: aa\n- l2_ab:\n-  l1_a:\n-   level2: ab\n- l2_bb:\n-  l1_b:\n-   level2: ba\n- l2_c:\n-  l1_b:\n-   level2: bc\n-two:\n- level2:\n-  level3:\n-   l2_a: aa\n-   l2_ab: ab"
            ),
        )

        diff = g.diff(f)
        self.assertEqual(
            sorted(str(diff)),
            sorted(
                "+at: level2\n+attributes: None\n+commands: None\n+connections: None\n+context_manager:\n+l1_a:\n+ level2:\n+  level3:\n+   l1_a: a\n+   l1_b: b\n+raw_data: False\n+three:\n+ l2_a:\n+  l1_a:\n+   level2: aa\n+ l2_ab:\n+  l1_a:\n+   level2: ab\n+ l2_bb:\n+  l1_b:\n+   level2: ba\n+ l2_c:\n+  l1_b:\n+   level2: bc\n+two:\n+ level2:\n+  level3:\n+   l2_a: aa\n+   l2_ab: ab"
            ),
        )

    def test_raw_data(self):
        f = self.FeatureWithRawData(device=self.dev1)
        f.learn()
        self.assertTrue(hasattr(f, 'raw_data'))
        self.assertTrue(f.raw_data)
        output = f.maker.outputs[FakeParser_5]['']
        self.assertTrue(hasattr(output, 'raw_output'))
        self.assertTrue(
            output.raw_output[0]['command'],
            'fakeparser_5')


class test_base_poll(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.testbed = Testbed()
        cls.dev1 = Device(name="pe1", testbed=cls.testbed, os="nxos")

    class Feature_1(Base):
        def learn(self):
            self.a = 5
            self.b = "test"

    class Feature_2(Base):
        def learn(self):
            explode

    class Feature_2(Base):
        def learn(self):
            explode
            self.a = 5

    class Feature_3(Base):
        i = 0

        def learn(self):
            if self.i == 1:
                self.a = 5
            else:
                self.i = +1
                explode

    class Feature_4(Base):
        i = 0

        def learn(self):
            if self.i == 1:
                pass
            else:
                self.i = +1
                explode

    def verify(self, feature):
        assert hasattr(feature, "a")

    def test_poll_1(self):
        f = self.Feature_1(device=self.dev1)
        before = datetime.datetime.now()
        f.learn_poll(sleep=0.5, attempt=2)
        after = datetime.datetime.now()
        delta = after - before
        self.assertLess(delta.total_seconds(), 1)
        self.assertTrue(hasattr(f, "a"))
        self.assertTrue(hasattr(f, "b"))

    def test_poll_2(self):
        f = self.Feature_2(device=self.dev1)
        before = datetime.datetime.now()
        with self.assertRaises(StopIteration):
            f.learn_poll(sleep=0.5, attempt=2)
        after = datetime.datetime.now()
        delta = after - before
        self.assertGreater(delta.total_seconds(), 1)
        self.assertFalse(hasattr(f, "a"))

    def test_poll_3(self):
        f = self.Feature_3(device=self.dev1)
        before = datetime.datetime.now()
        f.learn_poll(sleep=0.5, attempt=2)
        after = datetime.datetime.now()
        delta = after - before
        self.assertGreater(delta.total_seconds(), 0.5)

    def test_poll_4(self):
        f = self.Feature_3(device=self.dev1)
        before = datetime.datetime.now()
        f.learn_poll(verify=self.verify, sleep=0.5, attempt=2)
        after = datetime.datetime.now()
        delta = after - before
        self.assertGreater(delta.total_seconds(), 0.5)

    def test_poll_5(self):
        f = self.Feature_4(device=self.dev1)
        before = datetime.datetime.now()
        with self.assertRaises(StopIteration):
            f.learn_poll(verify=self.verify, sleep=0.5, attempt=2)
        after = datetime.datetime.now()
        delta = after - before
        self.assertGreater(delta.total_seconds(), 1)


if __name__ == "__main__":
    unittest.main()
