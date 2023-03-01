import os
import pathlib
import logging
import argparse

from pyats.easypy.job import Job

log = logging.getLogger(__name__)

JOBFILE_TEMPLATE = '''
from genie.harness.main import gRun

def main(runtime):
    gRun(runtime = runtime)
'''

class GenieJob(Job):

    @classmethod
    def configure_parser(cls, parser, legacy_cli = True):
        grp = parser.add_argument_group('Genie Script argument')

        if legacy_cli:
            job_uid_opt = ['-job_uid']
        else:
            job_uid_opt = ['--job-uid']

        grp.add_argument(*job_uid_opt,
                         type = str,
                         metavar = '',
                         dest = 'job_uid',
                         help=argparse.SUPPRESS)

        return parser

    def __init__(self, runtime, **kwargs):
        # set robotscript as the job file to run
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        job = os.path.join(curr_dir, 'job.py')
        kwargs.setdefault('jobfile', job)
        super().__init__(runtime, **kwargs)

    def run(self):

        # generate the job file
        jobfile = os.path.join(self.runtime.directory,
                               "{d}_job.py".format(
                                   d=pathlib.Path(self.file).stem))

        log.info('Generating Genie job file: {j}'.format(j=jobfile))

        # write to runtime directory
        with open(jobfile, 'w') as f:
            f.write(JOBFILE_TEMPLATE)

        # update self.file to the actual job file
        self.file = jobfile

        return super().run()
