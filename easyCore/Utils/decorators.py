__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import collections
import functools
from time import time
from easyCore import borg


class memoized:
    """
    Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    """

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)


def counted(func):
    """
    Counts how many times a function has been called and adds a `func.calls` to it's properties
    :param func: Function to be counted
    :return: Results from function call
    """

    def wrapped(*args, **kwargs):
        wrapped.calls += 1
        return func(*args, **kwargs)

    wrapped.calls = 0
    return wrapped


def time_it(func):
    """
    Times a function and reports the time either to the class' log or the base logger
    :param func: function to be timed
    :return: callable function with timer
    """
    name = func.__module__ + '.' + func.__name__
    time_logger = borg.log.getLogger('timer.' + name)

    @functools.wraps(func)
    def _time_it(*args, **kwargs):
        start = int(round(time() * 1000))
        try:
            return func(*args, **kwargs)
        finally:
            end_ = int(round(time() * 1000)) - start
            time_logger.debug(f"\033[1;34;49mExecution time: {end_ if end_ > 0 else 0} ms\033[0m")
    return _time_it
