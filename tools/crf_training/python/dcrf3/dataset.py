from scipy import zeros, isinf
from bisect import bisect
from scipy import nan, isnan, nanmin, nanmax, linspace
from scipy.sparse import lil_matrix
from spatial_features_cxx import flu_binarize_feature_uniform
import numpy as na
from collections import defaultdict

def compute_obs_counts(observations):
    label_to_count = defaultdict(lambda : 0)
    fname_to_count = defaultdict(lambda : 0)
    fname_to_label_to_count = defaultdict(lambda: defaultdict(lambda: 0))
    for o in observations:
        label_to_count[o.label] += 1
        for fname in o.features_obs.keys():
            fname_to_count[fname] += 1
            fname_to_label_to_count[fname][o.label] += 1

    fname_to_label_to_count = \
        dict((fname, dict(value)) 
             for fname, value in fname_to_label_to_count.iteritems())
    return dict(fname_to_count), dict(label_to_count), fname_to_label_to_count


def to_mallet_dataset(obs):
    """
    Convert to mallet in svmlight format, which also supports continuous features
    """
    mystr = ""
    for d in obs.observations:
        mystr += str(d.label) + " "
        for fname, fvalue in d.features_obs.iteritems():
            if isnan(fvalue) or isinf(fvalue):
                fvalue = 0.0
            mystr+= str(fname) + ":%.10f " % fvalue
            mystr += "\n"
        mystr+="\n"
    return mystr


def binarize_feature_uniform_cmp(name, value, min_val, max_val, num_units):
    # print "binarize"
    #print "name = ", repr(name)
    #print "value = ", repr(value)
    #print "min_val = ", repr(min_val)
    #print "max_val = ", repr(max_val)
    #print "num_units = ", repr(num_units)
    #p = binarize_feature_uniform_p(name, value, min_val, max_val, num_units)
    c = binarize_feature_uniform_c(name, value, min_val,
                                   max_val, num_units)
    #assert p == c
    return c

def binarize_feature_uniform_c(name, value, min_val, max_val, num_units):
    #print name, value, min_val, max_val, num_units
    r = flu_binarize_feature_uniform(str(name), float(value), float(min_val),
                                     float(max_val), num_units)
    return r

def binarize_feature_uniform_p(name, value, min_val, max_val, num_units):
    """
    Now reimplemented in c, so don't use this.  Keeping around in case
    of problems.  But I tested that the c and python versions were identical
    for many values.   -- stefie10
    """
    if(isnan(value) or isnan(min_val) or isnan(max_val)):
        return name+"_nan"

    if(isinf(min_val)):
        discrete = linspace(-100-0.1, max_val+0.1, num_units)
        #print discrete
    elif(isinf(max_val)):
        discrete = linspace(min_val-0.1, 100+0.1, num_units)
        #print discrete
    else:
        discrete = linspace(min_val-0.1, max_val+0.1, num_units)
    #print "discrete = ", 
    #print repr(discrete)
    #print len(discrete)
    i = bisect(discrete, value)
    #print "i", i
    if(i <= len(discrete)-1 and i > 0):
        ret_name = name+"_{0:0.2f}".format(discrete[i-1])+"_{0:0.2f}".format(discrete[i])
    elif(i == 0):
        ret_name = name+"_lt_{0:0.2f}".format(discrete[0])
    elif(i == len(discrete)):
        ret_name = name+"_gt_{0:0.2f}".format(discrete[-1])
    
    return ret_name

binarize_feature_uniform = binarize_feature_uniform_c

def intern_dict(strings_to_values):
    return dict((intern(key), value) for key, value in strings_to_values.iteritems())

class ContinuousObservation(object):
    def __init__(self, example_id, label, true_label,
                 features_obs,
                 sdcs=None, ggg=None, factor=None, node=None,
                 annotation=None):
        self.id = example_id
        
        self.label = label
        self.true_label = true_label
        self.features_obs = intern_dict(features_obs)
        for key, value in features_obs.iteritems():
            if value == True:
                features_obs[key] = 1.0
            elif value == False:
                features_obs[key] = 0.0
            elif value > 10:
                features_obs[key] = 10
            elif value < -10:
                features_obs[key] = -10
        self.sdcs = sdcs
        self.ggg = ggg
        self.factor = factor
        self.node = node

        self.features_obs_rl = dict((key, value) for key, value in self.features_obs.iteritems()
                                    if (not na.isinf(value) and 
                                        not na.isnan(value)  and 
                                        not "avs" in key and 
                                        "Ratio" not in key and not "null" in key))
        self.annotation = annotation
    def get_feature_summary(self):
        fname_to_observed_values = {}
        
        for i, (fname, fvalue) in enumerate(self.features_obs.iteritems()):
            fname_to_observed_values.setdefault(fname, set())
            fname_to_observed_values[fname].add(fvalue)

        
        return fname_to_observed_values


      
    def to_discrete_observation(self, f_min_max, dfactor=10):

        obs = []
        for feature_name, fvalue in self.features_obs.iteritems():
            if not isnan(fvalue):
                f_min, f_max = f_min_max.get(feature_name, (-10, 10))
                f_name_discrete = binarize_feature_uniform(feature_name, 
                                                           fvalue, f_min, f_max, dfactor)
                obs.append(f_name_discrete)

        try:
            return DiscreteObservation(self.label, self.true_label, dict((x, 1.0) for x in obs),
                                       self.sdcs, self.ggg, self.factor, self.node,
                                       self.annotation)
        except:
            print [str(s) for s in self.sdcs]
            raise

    

class ContinuousDataset(object):
    def __init__(self, observations, feature_extractor_cls=None):
        self.observations = observations  
        if any(o == None for o in self.observations):
            raise ValueError("None observation. " + `self.observations`)
        self.feature_extractor_cls = feature_extractor_cls

        # fname is feature name, not file name.
        self.fname_to_count, self.label_to_count, self.fname_to_label_to_count = compute_obs_counts(self.observations)
        self.labels = sorted(self.label_to_count.keys())
        self.fname_to_idx = dict(zip(self.fname_to_count.keys(), 
                                     range(len(self.fname_to_count.keys()))))
        
        self.label_to_idx =  dict(zip(self.labels, range(len(self.labels))))
        
        self.fnames = sorted(self.fname_to_count.keys())
        
        

    def convert_observation(self, c_obs):
        """
        No-op to support the same API as discrete dataset.
        """
        return c_obs

    def to_sparse_numpy_obs(self):
        D_obs = lil_matrix((len(self.observations), len(self.fname_to_idx.keys())))
        labels_obs = []
        
        for i, o in enumerate(self.observations):
            for t in range(len(o.features_obs_names)):
                labels_obs.append(o.labels[t])
                for j, key in enumerate(o.features_obs_names[t]):
                    D_obs[i, self.fname_to_idx[key]] = o.features_obs_vals[t][j]
                    
        return self.fname_to_idx, D_obs, labels_obs
            
    def to_discrete_dataset(self, dfactor=36, dataset=None):
        #get maximum and minimum values
        print "getting feature summary"
        f_summary = self.get_feature_summary()
        
        print "min/max val"
        f_min_max = {}
        for name in f_summary.keys():
            #if(nan in f_summary[name]):
            #    print "f_summary[name]", fsummary[name]
            #try:
            #    f_summary[name].remove(nan)
            #except:
            #    print "not removed"
            #print f_summary, name
            #print list(f_summary[name])
            min_val = nanmin(list(f_summary[name]))
            max_val = nanmax(list(f_summary[name]))

            #if(isnan(min_val) or isnan(max_val)):
            #    print "name:", name, min_val, max_val
            #else:
            #    print "name:", name, min_val, max_val
            #    print "nan in summary:", nan in f_summary[name]
            #    print "set:", f_summary[name]
            #    print "dataset.py: error neither should be nan"
            #    exit(0)
            f_min_max[name] = [min_val, max_val]
            #print name, [min_val, max_val]
            #raw_input()

        # print "computed keys"
        # for key in f_min_max.keys():
        #     if "3d" in key and "w_pick" in key:
        #         print key, f_min_max[key]

        #convert other datset if applicable
        if(dataset==None):
            observations = self.observations
        else:
            observations = dataset
        
        obs_discrete = []
        print "converting observations"
        for o in observations:
            dobs = o.to_discrete_observation(f_min_max, dfactor=dfactor)
            dobs.annotation = o.annotation
            obs_discrete.append(dobs)

        print "constructing dataset"          

        return DiscreteDataset(obs_discrete, dfactor, f_min_max=f_min_max,
                               feature_extractor_cls=self.feature_extractor_cls)

    
    def get_feature_summary(self):
        ret_val = {}
        for o in self.observations:
            o_sum = o.get_feature_summary()
            
            for name in o_sum.keys():
                if(ret_val.has_key(name)):
                    ret_val[name].update(o_sum[name])
                else:
                    ret_val[name] = set(o_sum[name])
        return ret_val
    
    def to_mallet_dataset(self):
        return to_mallet_dataset(self)


class DiscreteObservation(object):
    def __init__(self, label, true_label, features_obs,
                 sdcs=None, ggg=None, factor=None, node=None, annotation=None):

        self.label = label
        self.true_label = true_label
        self.features_obs = intern_dict(features_obs)
        self.features_obs_names = features_obs.keys()
        self.features_obs_values = features_obs.values()
        self.sdcs = sdcs
        self.ggg = ggg
        self.factor = factor
        self.node = node
        self.annotation = annotation

    def to_array_obs(self, name_to_num):
        #if(len(self.features_obs_arr) > 0):
        #    return self.features_obs_arr 

        ret_arr = []
        
        for elt in self.features_obs:
            f_arr = zeros(len(name_to_num))
            for f in elt:
                if(name_to_num.has_key(f)):
                    f_arr[name_to_num[f]] = 1.0
            
            ret_arr.append(f_arr)

        #self.features_obs_arr = ret_arr
        return ret_arr
    

    def to_array_output(self, name_to_num, num_features):
        ret_arr = []
        
        for elt in self.labels:
            #if(name_to_num.has_key(elt)):
            ret_arr.append(name_to_num[elt])
            
        return ret_arr


class DiscreteDataset(object):
    def __init__(self, observations, dFactor, f_min_max=None, 
                 feature_extractor_cls=None):
        self.observations = observations
        self.feature_extractor_cls = feature_extractor_cls

        print "counts"
        self.fname_to_count, self.label_to_count, self.fname_to_label_to_count = compute_obs_counts(self.observations)
        self.fnames = sorted(self.fname_to_count.keys())
        self.labels = sorted(self.label_to_count.keys())

        print "idx"
        self.fname_to_idx = dict(zip(self.fnames, range(len(self.fnames))))
        self.label_to_idx =  dict(zip(self.labels, range(len(self.labels))))

        self.num_labels = len(self.label_to_count)
        self.num_obs = len(self.fname_to_idx)
        
        self.f_min_max = f_min_max
        self.discretization_factor = dFactor
        
    def to_mallet_dataset_tokens(self):
        """
        Original mallet export that only works with binary features.
        """
        mystr=""
        for d in self.observations:
            for ft in d.features_obs:
                for f in ft:
                    mystr+= str(f) + " "
                mystr += str(d.labels[0])+"\n"
            mystr+="\n"

        return mystr

    def to_mallet_dataset(self):
        return to_mallet_dataset(self)
    
    def to_sparse_numpy_obs(self):
        name2num_obs = self.name_to_num_obs()
        
        D_obs = lil_matrix((len(self.observations), len(name2num_obs.keys())))
        labels_obs = []
        
        for i, o in enumerate(self.observations):
            for t in range(len(o.features_obs)):
                labels_obs.append(o.labels[t])
                for j, f_name in enumerate(o.features_obs[t]):
                    D_obs[i, name2num_obs[f_name]] = 1.0
                    
        return name2num_obs, D_obs, labels_obs


        
    def convert_observation(self, c_obs):
        """
        Converts a continuous observation to discrete.
        """
        if self.f_min_max != None:
            obs = c_obs.to_discrete_observation(self.f_min_max, 
                                                self.discretization_factor)
            return obs
        return None

        





    def name_to_num_output(self):
        if(self.name2num_output != None):
            return self.name2num_output
        
        self.name2num_output =  dict(zip(self.get_output_alphabet(), 
                                         range(self.num_output)))
        
        return self.name2num_output


    def compute_feature_counts(self):
        obs_dict = self.name_to_num_obs()
        
        cnt_obs = {}

        
        
        for i in range(self.num_output):
            cnt_obs[self.o_alphabet[i]] = zeros(self.get_num_features_obs())*1.0
        
        for o in self.observations:
            for i, ts in enumerate(o.features_obs):
                for f in ts:
                    #print "stuff", o.labels[i], obs_dict[f]
                    cnt_obs[o.labels[i]][obs_dict[f]] += 1

        
        return cnt_obs


    


    def get_features(self, d, has_fc=False):
        ntonum_oput = self.name_to_num_output()

        if(has_fc == False):
            f_obs = d.to_array_obs(self.name_to_num_obs(), self.num_obs)
        else:
            f_obs = d.features_obs
        
        num_obs = self.num_output*self.num_obs
        
        #initialize the return matrices
        f_obs_ret = []
        for i in range(len(f_obs)):
            f_obs_ret.append(zeros(num_obs))
        
        

        for i in range(len(f_obs_ret)):
            start = ntonum_oput[d.labels[i]]*self.num_obs
            f_obs_ret[i][start:start+self.num_obs] = f_obs[i]

        return f_obs_ret

    def get_features_I(self, d, has_fc=False, use_nan=False):
        ntonum_oput = self.name_to_num_output()

        f_obs_I = []
        ntonum_obs = self.name_to_num_obs()
        #set the features
        for i in range(len(d.features_obs)):
            #get an index here
            start = ntonum_oput[d.labels[i]]*self.num_obs
            
            curr_feat_I = []
            for f_name in d.features_obs[i]:
                #print f_name
                if(ntonum_obs.has_key(f_name)):
                    curr_feat_I.append(ntonum_obs[f_name]+start)
                elif(use_nan):
                    curr_feat_I.append(nan)
                #else:
                    #print f_name, "does not exist"
                    #raw_input()
            f_obs_I.append(curr_feat_I)
            
        return f_obs_I
        
    

    def observations_count(self):
        num_obs = 0
        for o in self.observations:
            for i, ts in enumerate(o.features_obs):
                num_obs +=1

        return num_obs




