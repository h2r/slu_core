import multiprocessing
from Queue import Empty
import process_utils
import atexit

import traceback


def noop(key, key_extra_len=0):
    pass

def network_writer(queue):
    import pylibmc as memcache
    cache = memcache.Client(["127.0.0.1:21201"])
    cache.check_key = noop
    
    while True:
        try:
            try:
                r = queue.get(block=True, timeout=0.1)
            except IOError:
                return
            if r == "terminate":
                return
            else:
                key, value = r
                cache.set(key, value)
        except Empty:
            pass


dicts = []            


def reopen():
    for d in dicts:
        d.reopen()
def terminator():
    """
    If we don't terminate the dictionary, the process hangs and never
    exits.  However this solution causes a memory leak.  It's a
    tradeoff.
    """
    for d in dicts:
        d.close()

atexit.register(terminator)


class Dict:
    
    def __init__(self):
        import pylibmc as memcache
        self.cache = memcache.Client(["127.0.0.1:21201"])
        self.pid = multiprocessing.current_process().pid
        self.write_queue = multiprocessing.Queue()
        self.write_process = multiprocessing.Process(target=network_writer, 
                                                     args=(self.write_queue,))

        self.write_process.daemon = True
        self.write_process.start()

        dicts.append(self)

    def reopen(self):
        import pylibmc as memcache
        pid = multiprocessing.current_process().pid
        if self.pid != pid:
            self.cache = memcache.Client(["127.0.0.1:21201"])
            self.pid = pid
        
    def __setitem__(self, key, value):
        self.write_queue.put((key, value))

    def get_multi(self, keys):
        return self.cache.get_multi(keys)

    def __getitem__(self, key):
        try:
            result = self.cache.get(key)
        except:
            print "except on key", key
            traceback.print_exc()
            raise KeyError()
        if result == None:
            raise KeyError()
        return result

    def close(self):
        #print "bsddb_process sending close", self.write_queue.qsize()
        self.write_queue.put("terminate")
        #print "bsddb_process joining"
        process_utils.join(self.write_process)
        #print "bsddb_process done"
        
