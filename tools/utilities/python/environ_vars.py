import os


SLU_HOME = "";
for param in os.environ.keys():
    if(param == "SLU_HOME"):
        SLU_HOME = os.environ[param]

SLU_HOME=SLU_HOME

def fix_path(fname):
    if not os.path.exists(fname):
        dirs = fname.split("/")
        print dirs
        for i in range(len(dirs)):
            new_fname = os.path.join(*([SLU_HOME] + dirs[i:]))
            if os.path.exists(new_fname):
                return new_fname
    return fname
