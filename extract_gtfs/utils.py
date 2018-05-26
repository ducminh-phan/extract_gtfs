import os
import pickle
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


class LogAttribute:
    @classmethod
    def save_attributes(cls, directory):
        # Create the folder to save the temporary files
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Pickle all attribute from __slots__
        for key in cls.__slots__:
            value = getattr(cls, key)

            with open('{}/{}.pickle'.format(directory, key), 'wb') as f:
                pickle.dump(value, f)

    @classmethod
    def load_attributes(cls, directory):
        try:
            for key in cls.__slots__:
                with open('{}/{}.pickle'.format(directory, key), 'rb') as f:
                    print("\nLoading precomputed {}.{}".format(cls.__name__, key))
                    value = pickle.load(f)

                setattr(cls, key, value)

            return True
        except FileNotFoundError:
            return False


def save_load(func):
    @wraps(func)
    def wrapper(cls, *args, **kwargs):
        from .data import Data
        directory = 'tmp/{}'.format(Data.in_folder)

        file_exists = cls.load_attributes(directory)

        if not file_exists:
            res = func(cls, *args, **kwargs)
            cls.save_attributes(directory)

            return res

    return wrapper
