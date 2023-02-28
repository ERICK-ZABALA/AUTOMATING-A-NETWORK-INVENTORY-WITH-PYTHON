import random
import threading as th
# import multiprocessing as th
# from threading import Thread as Worker
from multiprocessing import Process as Worker
import time
import logging
probe = 10
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

def callback(sleep_time):
    logging.info('sleep time is %s' % sleep_time)
    time.sleep(sleep_time)
    logging.info('and here I complete ... %s' % probe)

def crazy_callback(sleep_time):
    logging.info('sleep time is %s' % sleep_time)
    global probe
    deep_probe = 1000
    probe = 100
    tn = Worker(name='thread_of_crazy_thread', target=callback, args=(sleep_time*2,))
    tn.start()
    time.sleep(sleep_time)


    logging.info('and here I complete ... %s' % probe)

w1 = Worker(name='test_thread1', target=callback, args=(1,))
w2 = Worker(name='test_thread2', target=callback, args=(1,))
w3 = Worker(name='test_thread3', target=callback, args=(1,))
w4 = Worker(name='crazy_thread', target=crazy_callback, args=(1,))

w1.start()
w2.start()
w3.start()
w4.start()
w1.join()
w2.join()
w3.join()
w4.join()
w4.terminate()
# for i in range(10):
#     time.sleep(1)
#     logging.error(w4.is_alive())

logging.info('was I really async? %s' % (probe,))