# To run the job:
# pyats run job $VIRTUAL_ENV/examples/basic/job/basic_example_job.py
# Description: This example shows the the functionality of configuration datafiles

import os
from genie.harness.main import gRun

def main():
    test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    subsection_datafile = os.path.join(test_path, 'script/subsection.yaml',)

    gRun(
        subsection_datafile=subsection_datafile,
        )
