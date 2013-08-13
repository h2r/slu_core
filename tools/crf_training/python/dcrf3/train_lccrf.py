from mallet.learners.crf_mallet import CRFMallet
from optparse import OptionParser
import pickle_util
import dcrf3.dataset as dataset

def train_lccrf(dataset_all, outfilename, sigma=0.99, train_iterations=500):

    outfilename = outfilename.replace(".", "_"+str(sigma)+".")
    
    
    print "--------------------------------------"
    print "starting n=", len(dataset_all.observations)
    print "sigma=", sigma
    print "--------------------------------------"
    
    
    lcrf = CRFMallet(dataset_all, sigma, train_iterations)
    lcrf.train()
    lcrf.dataset.observations = None
    
    print "saving to:", outfilename
    CRFMallet.save(lcrf, outfilename)
    return outfilename


def main():
    parser = OptionParser()

    parser.add_option("--training_filename",dest="training_fname", 
                      help="Training Filename", metavar="FILE")
    parser.add_option("--crf_filename", dest="crf_fname", 
                      help="CRF Filename", metavar="FILE")
    parser.add_option("-s", "--sigma", dest="sigma", type="float",help="Sigma")
    parser.add_option("--iterative-train-and-save-observations", dest="iterative_train_and_save_observations", default=None, help="trains the model with frist 1 observation, then 2, then 3 .. etc until all. Saves each model after each train")
    parser.add_option("--iterative-train-and-save-crf-iterations", dest="iterative_train_and_save_train_iterations", default=None )
        
    (options, args) = parser.parse_args()

    print "opening positive dataset"
    dataset_all = pickle_util.load(options.training_fname)
    print "dataset", dataset_all
    print len([e for e in dataset_all.observations 
               if e.sdcs[0].type == "EVENT"]), "events"


    if options.iterative_train_and_save_observations is not None:
        
        ## ok, let's build up the model names and the training dataset
        for i in range( 1, len( dataset_all.observations )):

            print "*!*!*!*!*!*!!* Taking ", i , " Observations"
            
            output_model_name = options.crf_fname.replace(".", "_numobs="+str(i)+".")
            current_dataset = dataset.DiscreteDataset( dataset_all.observations[0:i], dataset_all.discretization_factor, dataset_all.f_min_max, dataset_all.feature_extractor_cls )
            
            train_lccrf( current_dataset, output_model_name, options.sigma)

            


    elif options.iterative_train_and_save_train_iterations is not None:
        
        ## let's train with different iterations all the data
        for i in range( 1, 500, 1 ):
            output_model_name = options.crf_fname.replace(".", "_trainiters="+str(i)+".")
            dataset_all = pickle_util.load(options.training_fname)
            train_lccrf( dataset_all, output_model_name, options.sigma, i)
        
    else:
        train_lccrf(dataset_all, options.crf_fname, options.sigma)

    
if __name__=="__main__":

    main()
