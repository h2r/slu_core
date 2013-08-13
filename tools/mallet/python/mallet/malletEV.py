from environ_vars import SLU_HOME

def classpath():
    import os
    os.environ.setdefault("MALLET_HOME",
                          SLU_HOME+"/3rdParty/mallet/")
    mallet_home = os.environ["MALLET_HOME"]
    return ":".join(["%s/lib/mallet-deps.jar" % mallet_home,
                     "%s/class" % mallet_home])


