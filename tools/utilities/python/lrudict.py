import orderedDict
from collections import MutableMapping
class LruCache(MutableMapping):
    """
    LRU cache that automatically flushes old elements when size is
    greater than cache size.
    """
    def __init__(self, cache_size):
        self.cache_size = cache_size
        self.cache = orderedDict.OrderedDict()

        
        
    def __getitem__(self, key):
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def __setitem__(self, key, value):
        self.cache[key] = value
        self.cache.move_to_end(key)

        
    def __delitem__(self, key):
        del self.cache[key]

    
    def __len__(self):
        return len(self.cache)
    
    def __iter__(self):
        return iter(self.cache)

    def __contains__(self, x):
        return x in self.cache

    
