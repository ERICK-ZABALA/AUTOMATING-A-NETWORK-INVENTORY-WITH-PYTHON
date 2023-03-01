import os
import unittest
import subprocess


class TestValidateJinja2Config(unittest.TestCase):

    def test_validate_jinja2_config(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        p = subprocess.run(
            'pyats validate jinja2_config data/config_datafile.yaml --testbed data/testbed.yaml',
            shell=True,
            encoding='utf-8',
            stdout=subprocess.PIPE)

        expected = '''
Device R1 sequence 1:
interface Loopback0
no shutdown
ip address 1.1.1.1 255.255.255.255


'''
        self.assertEqual(expected, p.stdout)


    def test_validate_jinja2_config_error(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        p = subprocess.run(
            'pyats validate jinja2_config data/config_datafile_error.yaml --testbed data/testbed.yaml',
            shell=True,
            encoding='utf-8',
            stdout=subprocess.PIPE)

        self.assertIn("jinja2.exceptions.TemplateSyntaxError: Encountered unknown tag 'endif'.", p.stdout)


if __name__ == '__main__':
    unittest.main()
