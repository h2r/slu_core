from environ_vars import SLU_HOME
import traceback
import smtplib
import os
from email.mime.text import MIMEText

import datetime
from socket import gethostname
from svn_utils import current_svn_revision, has_diffs
from sh_utils import sh, FailedCommandError

lastrun_file = "%s/regression.lastrun" % SLU_HOME





class CommandLogger:
    def __init__(self):
        self.log = ""
        self.failed_count = 0
        self.run_count = 0
        self.raise_on_errors=False
    def sh(self, cmd):
        print 'running', cmd
        self.run_count += 1
        try:
            log, stdout = sh(cmd)
            self.append(log)
            return True
        except FailedCommandError as e:
            self.append(e.log)
            self.failed_count += 1
            if self.raise_on_errors:
                raise
            else:
                return False
    def append(self, txt):
        self.log += "\n" + txt  + "\n"
        



def save_last_run():
    f = open(lastrun_file, "w")
    f.write(`datetime.datetime.now()`)
    f.write("\n")
    f.write(`current_svn_revision()`)
    f.write("\n")
    f.close()
    
def get_last_run():
    if os.path.exists(lastrun_file):
        f = open(lastrun_file, "r")
        date = eval(f.readline())
        svnrevno = eval(f.readline())
        return date, svnrevno
    else:
        return None, None

def run(test_function):
    lockfile = "%s/regression.lock" % SLU_HOME
    if os.path.exists(lockfile):
        return
    else:
        open(lockfile, "w").close()
        failed_count = None
        run_count = None
        try:
            failed_count, run_count, msgBody, log = runtests(test_function)
        except:
            failed_count = 1
            run_count = 1
            msgBody = traceback.format_exc()
            log = None
        finally:
            os.remove(lockfile)
            if failed_count != None:
                send_email(failed_count, run_count, msgBody, log)


def runtests(test_function):

    last_run_datetime, last_svn_revno = get_last_run()

    log = ""
    os.chdir(SLU_HOME)
    #log += sh("svn up") # happens in cron
    svn_revno = current_svn_revision()
    diffs = has_diffs(last_svn_revno, svn_revno)

    if last_run_datetime != None:
        time_delta = datetime.datetime.now() - last_run_datetime
    else:
        time_delta = None
    time_delta_passes = last_run_datetime == None or  time_delta >= datetime.timedelta(minutes=10)
    print "revno", svn_revno, "(last run on", last_svn_revno, ")", "has_diffs:", diffs, "time delta:", time_delta, time_delta_passes
    if diffs and time_delta_passes:
        save_last_run()
        failed_count, run_count, msgBody = test_function()
        return failed_count, run_count, msgBody, log
    else:
        return None, None, None, log
        



def send_email(failed_count, run_count, msgBody, log):
    print "sending email"
    to = [
        "ar-language-dev@csail.mit.edu", 
        #"stefie10@csail.mit.edu", 
        ]

    if failed_count == 0:
        msgBody += "\n\nEverything passed!\n"
        subject_str = "Passed"
    else:
        now = datetime.datetime.now()
        log_fname = now.strftime(SLU_HOME + "/regression.%Y-%m-%d-%H-%M-%S.log")
        log_file = open(log_fname, 'w')
        if log != None:
            log_file.write(log)
        print log_fname, log_fname.__class__
        print msgBody, msgBody.__class__
        msgBody += "\n\nLog written to %s\n" % log_fname
        subject_str = "Failed"
        subject_str +=  " %d of %d" % (failed_count, run_count)

    msg = MIMEText(msgBody)
    svn_revno = current_svn_revision()
    msg['Subject'] = "SLU Regression Tests on %s for -r%d (%s)" % (gethostname(), svn_revno, subject_str)
    msg['From'] = "regression@" + gethostname() + ".csail.mit.edu"
    msg['To'] = ", ".join(to)



    server = smtplib.SMTP("outgoing.csail.mit.edu")
    server.sendmail(msg['From'], to, msg.as_string())
    server.quit()
    print msg.as_string()

