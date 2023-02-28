"""
    this module reporduces the threading issue in unicon
"""

import threading
from multiprocessing.pool import ThreadPool
from unicon import Connection

commands = ("sh clock",
            "sh ip int br",
            "sh file system")

con = Connection(start=['telnet 10.64.70.11 2041'],
                 hostname="si-tvt-7200-28-41")

con.connect()


def thread_work(handle, command="sh clock"):
    print("\n+++ entering worker: %s +++" % threading.current_thread().name)
    handle.sendline(command)
    handle.spawn.expect([con.hostname], timeout=60)
    print("\n+++ exiting worker: %s +++" % threading.current_thread().name)


def pool_worker(command):
    """this is also an error"""
    global con
    handle = con
    print("\n+++ entering worker: %s +++" % threading.current_thread().name)
    # handle.sendline(command)
    # handle.spawn.expect([con.hostname], timeout=60)
    handle.execute(command)
    print("\n+++ exiting worker: %s +++" % threading.current_thread().name)
# w1 = Worker(target=thread_work, args=(con, "ping 1.1.1.1"))
# w2 = Worker(target=thread_work, args=(con, "sh ip int br"))

# w1.start()
# w2.start()
# w1.join()
# w2.join()

pool = ThreadPool(10)
pool.map(pool_worker, commands)
print("+++ all joins have completed +++")


class This():

    def __init__(self):
        pass
