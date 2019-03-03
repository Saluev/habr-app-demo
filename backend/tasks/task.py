import functools
from typing import Callable

from backend.wiring import Wiring


def task(func: Callable):
    varnames = func.__code__.co_varnames

    @functools.wraps(func)
    def result(*args, **kwargs):
        wiring: Wiring = kwargs.pop("wiring")
        wired_objects_by_name = wiring.__dict__
        for arg_name in varnames:
            if arg_name in wired_objects_by_name:
                kwargs[arg_name] = wired_objects_by_name[arg_name]
        return func(*args, **kwargs)

    return result
