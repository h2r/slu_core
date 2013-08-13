from sh_utils import sh

def current_svn_revision():
    log, stdout =  sh("svn info")
    global_rev = stdout.split("\n")[4]
    revision, revno = global_rev.split()
    try:
        return int(revno)
    except:
        print revno
        print revno.__class__
        raise

def has_diffs(lastrev, currentrev):
    if lastrev == None:
        return True
    log, diff = sh("svn diff -r%d:%d --summarize" % (lastrev, currentrev))
    if len(diff) != 0:
        return True
    else:
        return False
