import signal
import time
import sys
import threading
count = 0

def receive_alarm(signum, stack):

    print('Alarm Handler :', time.ctime())

    raise Exception('raised from alarm handler')

# Call receive_alarm in 2 seconds
signal.signal(signal.SIGALRM, receive_alarm)

def action():
    signal.alarm(2)
    # print('Thread Callback Start:', time.ctime())
    # time.sleep(4)
    # print('Thread Callback Ends', time.ctime())
t = threading.Thread(target=action)
print('thread staring ...')
t.start()
sys.stdin.read()
t.join()
