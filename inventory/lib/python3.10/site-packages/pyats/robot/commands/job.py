import os
import pathlib
import logging

from pyats.easypy.job import Job

logger = logging.getLogger(__name__)

JOBFILE_TEMPLATE = '''
from pyats.robot.runner import run_robot

def main(runtime):
    run_robot('{robotscript}', runtime = runtime)
'''

class SimpleRobotJob(Job):

    @classmethod
    def configure_parser(cls, parser, legacy_cli = True):
        grp = parser.add_argument_group('Robot Script Info')

        if legacy_cli:
            job_uid_opt = ['-job_uid']
        else:
            job_uid_opt = ['--job-uid']

        # jobfile args
        # ------------
        grp.add_argument('robotscript',
                         nargs = '?',
                         metavar = 'FILE',
                         action = "store",
                         help = 'target RobotFramework script to be run')

        grp.add_argument(*job_uid_opt,
                         type = str,
                         metavar = '',
                         dest = 'job_uid',
                         help = 'Unique ID identifiying this job run')

        return parser

    def __init__(self, runtime, **kwargs):

        # get the robot script to run (abspath)
        robotscript = os.path.abspath(runtime.args.robotscript)

        # do some error checking
        # ----------------------
        if not robotscript:
            runtime.parser.error('Did you forget to provide a RobotFramework '
                                 'script?')

        elif not os.path.isfile(robotscript):
            runtime.parser.error("The provided Robot script '%s' does not "
                                 "exist." % robotscript)

        elif not os.access(robotscript, os.R_OK):
            runtime.parser.error("Robot script '%s' cannot be read: "
                                 "invalid permissions" % robotscript)

        # set robotscript as the job file to run
        kwargs.setdefault('jobfile', robotscript)

        # call parent
        super().__init__(runtime, **kwargs)

    def run(self):

        # generate the job file
        jobfile = os.path.join(self.runtime.directory,
                               "%s_job.py" % pathlib.Path(self.file).stem)

        logger.info('Generating Robot job file: %s' % jobfile)

        # write to runtime directory
        with open(jobfile, 'w') as f:
            f.write(JOBFILE_TEMPLATE.format(robotscript = self.file))

        # update self.file to the actual job file
        self.file = jobfile

        return super().run()
