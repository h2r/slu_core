def save_theta_dict(fname, theta):
    with open(fname, "w") as f:
        for key, value in theta.iteritems():
            f.write("%s %.100f\n" % (key, value))

def load_theta_dict(fname):
    tuples = []
    with open(fname, "r") as f:
        for line in f:
            key, value = line.strip().split(" ")
#            if "EVENT" in key:
#                continue
            tuples.append((key, float(value)))
    return dict(tuples)
