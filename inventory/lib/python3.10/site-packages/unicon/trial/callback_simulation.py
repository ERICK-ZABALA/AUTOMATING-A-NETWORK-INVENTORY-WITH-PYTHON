import time
import signal
import sys


def timeout_handler(signum, stack):
    print('Alarm Handler :', time.ctime())
    raise Exception('raised from alarm handler')
def foo(signum, stack):
    print('Foo Handler :', time.ctime())
import ipdb;ipdb.set_trace()
signal.signal(signal.SIGALRM, timeout_handler)




def wrap():
    def process_dialog(timeout=5):
        signal.alarm(timeout)
        while True:
            print('sleeping for a sec ....')
            time.sleep(1)
            sys.stdin.read()

    try:
        process_dialog()
    except Exception as err:
        print('now I will call timeout stuff ...')

try:
    wrap()
except Exception as err:
    print('caught but did nothing')

print('doing something more in the next step ...')
