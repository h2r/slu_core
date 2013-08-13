import errno
import signal
import os
def join(p):
    while True:
        try:
            p.join()
            return
        except OSError, ose:
            print "interrupt", ose
            if ose.errno != errno.EINTR:
                raise 
            
def send_signal_to_self(signum):
    os.kill(os.getpid(), signum);

def send_sigterm():
    send_signal_to_self(signal.SIGTERM)
