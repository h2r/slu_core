import datetime
from regression_runner import CommandLogger
import regression_runner
from environ_vars import SLU_HOME


def run_tests():
    start_time = datetime.datetime.now()
    log = CommandLogger()

    directory_names = ["forklift", "du_crf3", "esdcs", "stanford-parser",
                       "spatial_features", "nlu_navigation", "gis", 
                       #"kitchen",
                       "pr2",
                       "language_generation",
                       "reinforcement_learning", "sparse",
                       "utilities"]
    log.sh("rm /tmp/*.pck")
    log.sh("rake clean_python")
    log.sh("cd tools/du_crf3 && rake train_forklift")
    log.sh("cd tools/du_crf3 && rake train_esdcs")
    log.sh("cd tools/du_crf3 && rake train_sr")
    log.sh("cd tools/du_crf3 && rake train_d8_full")
    log.sh("cd tools/du_crf3 && rake train_pr2_bolt_2012")
    #log.sh("cd tools/kitchen && rake train")


    for directory_name in directory_names:

        cmd = "cd %s/tools/%s && rake tests" % (SLU_HOME, directory_name)
        log.sh(cmd)


    end_time = datetime.datetime.now()


    log.append("Ran %d tests in " % len(directory_names) + 
               str(end_time - start_time))
    return log.failed_count, log.run_count, log.log

def main():
    regression_runner.run(run_tests)

if __name__ == "__main__":
    main()
