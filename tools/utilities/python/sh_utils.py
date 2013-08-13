from subprocess import Popen
import subprocess

class FailedCommandError(Exception):
    def __init__(self, *args, **margs):
        Exception.__init__(self, *args, **margs)


def sh(cmd):
    process = Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT)
    log = ""
    log += "Running " + cmd + "\n"
    stdout, stderr = process.communicate()
    log += "\n\n************************* Standard output\n"
    log += str(stdout)

    log += "\n\n************************* Standard error\n"
    log += str(stderr)
    if process.returncode != 0:
        error = FailedCommandError("command failed!" + `cmd`)
        error.stdout = stdout
        error.stderr = stderr
        error.log = log
        raise error
    return log, stdout
