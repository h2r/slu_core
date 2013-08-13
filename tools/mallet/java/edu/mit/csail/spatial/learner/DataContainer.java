package edu.mit.csail.spatial.learner;
import cc.mallet.types.InstanceList;

public class DataContainer
{
    public InstanceList trainingData = null;
    public InstanceList testData = null;
    
    public DataContainer(InstanceList trainingData, InstanceList testData){
	this.trainingData = trainingData;
	this.testData = testData;
    }
}
