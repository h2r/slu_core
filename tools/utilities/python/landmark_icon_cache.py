import os.path
from memoized import memoized
from environ_vars import SLU_HOME
import matplotlib.image as mpimg
import numpy as na

@memoized
def getIcon(word):
    icon_fname = "%s/tools/utilities/resources/object_icons/%s.png" % (SLU_HOME, word)
    if os.path.exists(icon_fname):
        img = mpimg.imread(icon_fname)
        return na.flipud(na.asarray(img))
    else:
        return None
