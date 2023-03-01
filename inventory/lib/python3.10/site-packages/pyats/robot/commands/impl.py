import logging

from pyats.cli.base import Command, Subcommand
from pyats.cli.base import CustomHelpFormatter

# use the global runtime
from pyats.easypy import runtime

from . import job


logger = logging.getLogger(__name__)

class RunRobot(Command):
    '''
    Run RobotFramework Script in a generated job file
    '''

    name = 'robot'
    help = 'runs the provided RobotFramework script'

    usage = '''{prog} [file] [options]

Example
-------
  {prog} /path/to/my_robot_script.robot
  {prog} /path/to/my_robot_script.robot --testbed-file /path/to/testbed.yaml
'''

    description = '''
Runs a RobotFramework script with the provided arguments, generating & report
result.
'''

    def main(self, argv):
        # configure the parser
        runtime.parser = self.parser

        # configuration for running this guy
        modulename = job.__name__
        classname = job.SimpleRobotJob.__qualname__

        configuration = {
            'components': {
                'job': {
                    'class': '{module}.{class_}'.format(module = modulename,
                                                        class_ = classname),
                }
            }
        }

        # run and exit
        return runtime.main(argv = argv,
                            configuration = configuration)
