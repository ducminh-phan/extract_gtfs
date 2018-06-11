from functools import wraps
from time import time


def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        res = func(*args, **kwargs)

        elapsed_time = time() - start_time
        print('\nTime elapsed:', round(elapsed_time, 3), 'seconds')
        print('-' * 50)

        return res

    return wrapper


def query_yes_no(question, default="yes"):
    """
    Ask a yes/no question using input() and return the answer.
    :param question: a string that is presented to the user
    :param default: the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user)
    :return: True for "yes" or False for "no"
    """
    valid = {"yes": True, "y": True,
             "no": False, "n": False}

    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        choice = input(question + prompt).lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")
