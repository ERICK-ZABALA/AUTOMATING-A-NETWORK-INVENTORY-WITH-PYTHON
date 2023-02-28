import multiprocessing
import threading
from threading import Event
from threading import Thread as Worker
import time

class ObedientWorker(Worker):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.cancel = Event()
        super().__init__(*args, **kwargs)

    def run(self):
        """function to run"""
        t_name = threading.currentThread().getName()
        p_name = multiprocessing.current_process().name
        print('[%s|%s] waiting for cancel happen' % (p_name, t_name))
        new_t = Worker(target=rogue_resource)
        new_t.daemon=True
        #ret = self.cancel.wait(timeout=2)
        new_t.start()
        new_t.join(timeout=2)
        if new_t.is_alive():
            print('it is still running ....')
            return False
        else:
            return True
        # print('[%s|%s] cancelled ..' % (p_name, t_name))

def rogue_resource():
    t_name = threading.currentThread().getName()
    p_name = multiprocessing.current_process().name
    print('[%s|%s] I am rogue resource ...' % (p_name, t_name))
    time.sleep(20)

def f():
    t = ObedientWorker()
    ret = t.start()
    print(ret)
f()