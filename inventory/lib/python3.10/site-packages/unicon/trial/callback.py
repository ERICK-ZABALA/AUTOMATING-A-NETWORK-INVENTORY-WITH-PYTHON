import threading
import multiprocessing
from threading import Thread as Worker
# from multiprocessing import Process as Worker
from functools import wraps
import time
import sys
#
#
def callback(f):
    @wraps(f)
    def deco(*args, **kwargs):
        w = Worker(target=f, args=args, kwargs=kwargs)
        w.start()
        return w
    return deco
#
# def worker_delay():
#     w = Worker(target=mcb)
#     w.start()
#     return 'hello'
#
#
# @callback
# def mcb(delay=5):
#     stime = time.time()
#     while (time.time() - stime) < delay:
#         sys.stdout.write('sleeping for a sec [%s] ...' % delay)
#         sys.stdout.flush()
#         time.sleep(1)
#     time.sleep(delay)
#
# # w = Worker(target=mcb, args=(10,))
# # w.start()
#
#


def run_async(func):
    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Worker(target = func, args = args, kwargs = kwargs)
        func_hl.start()
        return func_hl
    return async_func

if __name__ == '__main__':
    from time import sleep

    @callback
    def print_somedata():
        t_name = threading.currentThread().getName()
        p_name = multiprocessing.current_process().name
        print('[%s|%s] starting print_somedata' % (p_name, t_name))
        sleep(1)
        print('[%s|%s] print_somedata: 1 sec passed' % (p_name, t_name))
        sleep(2)
        print('[%s|%s] print_somedata: 2 sec passed' % (p_name, t_name))
        sleep(1)
        print('[%s|%s] finished print_somedata' % (p_name, t_name))




    t_name = threading.currentThread().getName()
    p_name = multiprocessing.current_process().name

    print_somedata()
    print('*[%s|%s]* back in main' % (p_name, t_name))
    print_somedata()
    print('*[%s|%s]* back in main' % (p_name, t_name))
    print_somedata()
    print('*[%s|%s]* back in main' % (p_name, t_name))

    # def main(timeout=1):
    #     t_name = threading.currentThread().getName()
    #     p_name = multiprocessing.current_process().name
    #     t = print_somedata()
    #     t.join(timeout=timeout)
    #     if t.is_alive():
    #         raise Exception('timedout ....')
    #     else:
    #         print('*[%s|%s]* completed gracefully ...' % (p_name, t_name))
    #
    # try:
    #     main(5)
    # except Exception as err:
    #     print('seems something went wrong .....')