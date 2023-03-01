import os
import sys
import time
import shutil
import pathlib
import tempfile
import unittest
import multiprocessing as mp

# enforce fork (py38 defaults to spawn in mac)
multiprocessing = mp.get_context('fork')

from pyats.easypy.job import Job
from pyats.easypy.common_funcs import reset_global_easypy, init_runtime
from pyats.easypy.tests.common_mocks import patch_report, unpatch_report

from pyats.easypy.runinfo import RunInfo
from pyats.easypy.main import EasypyRuntime
from pyats.easypy.reporter import Reporter
from genie.harness.main import gTask


class TestGenieTask(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global TaskManager

        from pyats.easypy.tasks import TaskManager

        # cleanup easypy global
        reset_global_easypy()

    @classmethod
    def tearDownClass(cls):
        # cleanup easypy global
        reset_global_easypy()

    def setUp(self):
        f, self.jobfile = tempfile.mkstemp()
        os.close(f)
        self.archive_dir = tempfile.mkdtemp(prefix='archive_dir')
        self.runinfo_dir = tempfile.mkdtemp(prefix='runinfo_dir')
        f, self.testscript = tempfile.mkstemp()
        os.close(f)
        with open(self.testscript, 'w') as f:
            f.write('print("in testscript")')

        self.runtime = runtime = EasypyRuntime()
        init_runtime(self.runtime, self.jobfile)

        runtime.synchro = multiprocessing.Manager()

        runtime.plugins._plugins = list()
        patch_report()

        runtime.configuration.load()

        TIME_FORMAT = '%Y%b%d_%H:%M:%S'

        job_uid =  '{name}.{time}'.format(
                                        name = pathlib.Path(self.jobfile).stem,
                                          time = time.strftime(TIME_FORMAT,
                                                           time.localtime()))
        self.job = Job(runtime = runtime, job_uid = job_uid,
                       jobfile = self.jobfile)
        runtime.job = self.job

        runtime.reporter = Reporter(runtime = self.runtime,
                               **self.runtime.configuration.components.reporter)

        runtime.runinfo = RunInfo(runtime = self.runtime,
                                  archive_dir = self.archive_dir,
                                  runinfo_dir = self.runinfo_dir)

    def tearDown(self):
        unpatch_report()

        os.remove(self.jobfile)
        os.remove(self.testscript)
        shutil.rmtree(self.archive_dir)
        shutil.rmtree(self.runinfo_dir)

    def test_task_api(self):
        task = gTask(runtime=self.runtime)
        assert task.testscript == os.path.join(
            os.path.dirname(sys.modules['genie.harness'].__file__), 'genie_testscript.py')
        assert task.harness.__name__ == 'genie.harness'


if __name__ == '__main__': # pragma: no cover
    unittest.main()
