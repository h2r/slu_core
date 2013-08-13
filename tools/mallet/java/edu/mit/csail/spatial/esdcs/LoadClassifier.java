package edu.mit.csail.spatial.esdcs;

import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.io.ObjectInputStream;
import cc.mallet.classify.Classifier;

public class LoadClassifier {
    public static Classifier load(String fname) throws Exception {
        ObjectInputStream ois =
            new ObjectInputStream (new BufferedInputStream(new FileInputStream (fname)));
        Classifier o  = (Classifier) ois.readObject();
        ois.close();
        return o;
    }

}