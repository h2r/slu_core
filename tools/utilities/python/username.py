import pwd
import os
def username():
    return pwd.getpwuid(os.getuid())[0]

