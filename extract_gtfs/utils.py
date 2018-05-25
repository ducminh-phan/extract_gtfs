from functools import wraps
from time import time


def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        res = func(*args, **kwargs)

        elapsed_time = time() - start_time
        print("Time elapsed:", round(elapsed_time, 3), 'seconds')
        print('-' * 50)

        return res

    return wrapper
