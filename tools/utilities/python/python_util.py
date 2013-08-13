import glob
import os

def recursive_glob(prefix, pattern):
    files1 = glob.glob(prefix+pattern);
    mydirs = os.listdir(prefix)

    for mydir in mydirs:
        if(os.path.isdir(prefix+mydir+"/")):
            files1.extend(recursive_glob(prefix+mydir+"/", pattern));

    return files1
