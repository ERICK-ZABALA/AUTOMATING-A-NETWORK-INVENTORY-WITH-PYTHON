def run_robot(robotscript,
              taskid = None,
              runtime = None,
              max_runtime = None,
                **kwargs):
    if runtime is None:
        # default to the global runtime
        from pyats.easypy import runtime as default_runtime
        runtime = default_runtime

    # set test harness to robot runner
    kwargs.setdefault('test_harness', 'pyats.robot.runner')

    # create the task
    task = runtime.tasks.Task(robotscript,
                              taskid = taskid,
                              **kwargs)

    # start it, wait for it to finish
    task.start()
    task.wait(max_runtime)

    # return the result
    return task.result
