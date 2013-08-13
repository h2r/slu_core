import cPickle as pickle
import os

def save(fname, obj):
    try:
        with open(fname, "wb") as f:
            pickle.dump(obj, f, protocol=2)
    except:
        print "exception on", fname
        print "saving", repr(obj)
        raise

def load(fname):
    try:
        with open(fname, "r") as f:
            return pickle.load(f)
    except:
        print "exception on", fname
        raise


def numbered_fname(basename_pattern):
    """
    Returns a file name with a unique number in the %d position of the
    basename pattern.  basename_pattern should be something like
    "./filename_%03d.pck"
    """
    i = 0
    while True:
        fname = basename_pattern % i
        if not os.path.exists(fname):
            return fname
        i += 1
        if i > 10000:
            raise ValueError("Too many iterations! " + basename_pattern)
        
        
