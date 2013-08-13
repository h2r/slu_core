package edu.mit.csail.spatial.learner;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.util.Iterator;

import cc.mallet.types.FeatureVectorSequence;
import cc.mallet.types.FeatureSequence;
import cc.mallet.types.Label;
import cc.mallet.types.Instance;
import cc.mallet.types.LabelSequence;
import cc.mallet.types.FeatureVector;
import cc.mallet.pipe.Pipe;


/** 
 * Given instances with a FeatureVectorSequence in the data field,
 * break up the sequence into the individual FeatureVectors, producing
 * one FeatureVector per Instance.
 */

public class FeatureVector2FeatureVectorSequence extends Pipe 
{

    final class FeatureVectorSequenceIterator implements Iterator<Instance> 
    {
        Iterator<Instance> mIterator;
        int count = 0;
        public FeatureVectorSequenceIterator (Iterator<Instance> iterator) {
            mIterator = iterator;
        }
        public Instance next () {
            Instance instance = mIterator.next();
            FeatureVector fv = (FeatureVector) instance.getData();
            FeatureVector[] fva = new FeatureVector[1];
            fva[0] = fv;
            FeatureVectorSequence fvs = new FeatureVectorSequence(fva);

            Label target = (Label) instance.getTarget();
            int[] target_indexes = new int[1];
            target_indexes[0] = target.getIndex();
            
            FeatureSequence fs = new FeatureSequence(target.getAlphabet(), target_indexes);
            
            return new Instance (fvs, fs, 
                                 instance.getName() + " as sequence", instance.getSource());
        }
        public boolean hasNext () {
            return mIterator.hasNext();
        }
        public void remove () { 
            throw new UnsupportedOperationException();
        }
    }
    
    public FeatureVector2FeatureVectorSequence() {}
    
    public Iterator<Instance> newIteratorFrom (Iterator<Instance> inputIterator) {
        return new FeatureVectorSequenceIterator (inputIterator);
    }
    
    // Serialization 
    private static final long serialVersionUID = 1;
    private static final int CURRENT_SERIAL_VERSION = 0;
    private void writeObject (ObjectOutputStream out) throws IOException {
        out.writeInt (CURRENT_SERIAL_VERSION);
    }
    private void readObject (ObjectInputStream in) throws IOException, ClassNotFoundException {
        int version = in.readInt ();
    }

}
