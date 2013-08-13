import numpy
from functools import partial
import collections

class MemoizeInstance(object):
    """cache the return value of a method
    
    This class is meant to be used as a decorator of methods. The return value
    from a given method invocation will be cached on the instance whose method
    was invoked. All arguments passed to a method decorated with memoize must
    be hashable.
    
    If a memoized method is invoked directly on its class the result will not
    be cached. Instead the method will be invoked like a static method:
    class Obj(object):
        @memoize
        def add_to(self, arg):
            return self + arg
    Obj.add_to(1) # not enough arguments
    Obj.add_to(1, 2) # returns 3, result is not cached
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.func
        return partial(self, obj)
    def __call__(self, *args, **kw):
        obj = args[0]
        try:
            cached_obj, cache = self.cache[id(obj)]
            if not cached_obj is obj:
                raise KeyError
        except KeyError:
            cache = {}
            self.cache[id(obj)] = (obj, cache)

        key = (self.func, args[1:], frozenset(kw.items()))
        try:
            res = cache[key]
        except KeyError:
            res = cache[key] = self.func(*args, **kw)
        return res



class memoized(object):
    """
       source: http://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
       Decorator that caches a function's return value each time it is called.
       If called later with the same arguments, the cached value is returned, and
       not re-evaluated.
       """ 
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args, **margs):
        try:
            return self.cache[args]
        except KeyError:
            self.cache[args] = value = self.func(*args, **margs)
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args, **margs)
    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__




def hashable(x):
    if isinstance(x, list) or isinstance(x, tuple) or isinstance(x, numpy.ndarray):
        return tuple([hashable(o) for o in x])
    elif isinstance(x, dict):
        return tuple([hashable(o) for o in x.iteritems()])
    elif isinstance(x, set):
        return frozenset(x)
    else:
        return x
   

