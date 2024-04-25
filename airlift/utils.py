import time
import logging
logger = logging.getLogger(__name__)

func_times = {}
def timer_wrapper(func):
    
    def timer(*args, **kwargs): 
        t0 = time.time()
        result = func(*args, **kwargs)
        t1 = time.time()
        elapsed = t1 - t0
        func_times[func.__name__] = round(elapsed,3)
        return result

    return timer

def get_all_timings():
    return func_times