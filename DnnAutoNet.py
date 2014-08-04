# -*- coding: utf-8 -*-
"""
Created on Fri Aug  1 09:25:56 2014

@author: vartiai6
"""

import numpy as np
from scipy.io import loadmat, savemat


from pylearn2 import monitor
from pylearn2.datasets import dense_design_matrix
from pylearn2.models import mlp, maxout
from pylearn2.costs.mlp.dropout import Dropout
from pylearn2.training_algorithms import sgd, learning_rule
from pylearn2.termination_criteria import EpochCounter, MonitorBased, And
from pylearn2.datasets.preprocessing import Pipeline, ZCA
from pylearn2.datasets.preprocessing import GlobalContrastNormalization
from pylearn2.space import Conv2DSpace
from pylearn2.train import Train
from pylearn2.train_extensions import best_params
from pylearn2.utils import serial
from scipy.signal import lfilter
from pylearn2.expr.normalize import CrossChannelNormalizationBC01
from pylearn2.datasets.preprocessing import Standardize


import pickle 
import os
import sys
import random
from PIL import Image
import cv2
import csv
from random import shuffle


def ReadImages(annotFile,heigth,width,imagenumber):
          

    imagedata = np.empty([imagenumber,height,width,3])
    labels =[]
    i = 0
    with open(annotFile, 'rb') as csvfile:
       datareader = csv.reader(csvfile, delimiter=',', quotechar='|')
       for row in datareader:
           img = cv2.imread(row[0], cv2.IMREAD_COLOR)
           if img == None:
               raise IOError("could not read image "+filename)
           imagedata[i] = img
           i += 1
           
           labels.append(int(row[1]))
           
    imagedata = np.uint8(imagedata)
    return [imagedata,labels]
    
    
def FeatureExtraction(imagedata):
    
    # Resize to half size
    

    
    targetsize = (imagedata.shape[2]/2,imagedata.shape[1]/2)
    features = np.empty([imagenumber,height/2,width/2,3])
    for i in range(shape(imagedata)[0]):
        features[i] = cv2.resize(imagedata[i],targetsize)
    
    # Slice 1/3 from bottom
    
    features = features[:,0:targetsize[1]-targetsize[1]/3,:,:]

#    cv2.imshow('image',imagedata[0])    
#    cv2.waitKey()
#    cv2.destroyAllWindows()
    features = np.uint8(features)
    
#    features = np.transpose(features, (0, 2, 3, 1))
    
    return features


def OneHotEncode(labels,imagenumber):
    
    OHE = np.empty([imagenumber,4])
    for i in range(len(labels)):
        if labels[i] == 0:
            OHE[i] = [0,0,0,1]            
        elif labels[i] == 1:
            OHE[i] = [0,0,1,0]
        elif labels[i] == 2:
            OHE[i] = [0,1,0,0]
        else:
            OHE[i] = [1,0,0,0]
            
    return OHE
    
    


def Shuffle(features,labels):
    
    shuffledfeatures = np.empty([imagenumber,features.shape[1],features.shape[2],3])
    shuffledlabels = [None]*imagenumber
    shuffleindexes = range(len(labels))
    shuffle(shuffleindexes)
    
    for i in shuffleindexes:
        shuffledfeatures[i] = features[shuffleindexes[i]]
        shuffledlabels[i] = labels[shuffleindexes[i]]

    
    return [shuffledfeatures,shuffledlabels]


def DataPartition(data,labels,trainingpart,validpart):
    
    training = int(np.floor(trainingpart*len(labels)))
    trainFeatures  = data[0:training]
    trainLabels = labels[0:training]
    valid = training + int(np.ceil(validpart*len(labels)))
    validFeatures = data[training:valid]
    validLabels = labels[training:valid]
    testFeatures = data[valid:]
    testLabels = labels[valid:]
    
    return [trainFeatures,validFeatures,testFeatures,trainLabels,validLabels,testLabels]
  
if __name__ == '__main__':

    # open annotationfile  
    annotFile = sys.argv[1]
    
    # KOON PITÄÄ OLLA KAHDEN POTENSSI    
    height = 288
    width = 768
    imagenumber = 1500
    # Lisää oikeat parametrint myöhemmin
    print "Reading annotationfile"    
    
    [imagedata,labels] = ReadImages(annotFile,height,width,imagenumber)
    
    print "Creating features"    
    #Feature creation here

    features = FeatureExtraction(imagedata)

    print "Shuffling"
    
    [features,labels] = Shuffle(features,labels)
    
    print "Encoding labels"    
    
    labels = OneHotEncode(labels,imagenumber)

    
    features = np.float32(features)
    labels = np.float32(labels)    
    
    print "Feature shape is: " + str(shape(features))
    
    print "Divide into training, validitation, and test data"
      
    


    trainingpart = 0.8
    validpart = 0.1
    
    [trainFeatures,validFeatures,testFeatures,trainLabels,validLabels,testLabels] \
    = DataPartition(features,labels,trainingpart,validpart)
    
    # Create DDM for neural net    
    
    trainDDM = dense_design_matrix.DenseDesignMatrix(\
        topo_view = trainFeatures, \
        y = trainLabels, \
        axes=('b', 0, 1, 'c'))   
    
    validDDM = dense_design_matrix.DenseDesignMatrix(\
        topo_view = validFeatures, \
        y = validLabels, \
        axes=('b', 0, 1, 'c'))

    testDDM = dense_design_matrix.DenseDesignMatrix(\
        topo_view = testFeatures, \
        y = testLabels, \
        axes=('b', 0, 1, 'c'))
    
    # TÄHÄN VÄLIIN PREPROCESSING
    
    preprocessor = Standardize()
    trainDDM.apply_preprocessor(preprocessor = preprocessor, can_fit = True)
    testDDM.apply_preprocessor(preprocessor = preprocessor, can_fit = False)
    validDDM.apply_preprocessor(preprocessor = preprocessor, can_fit = False)     
    # Define the input type for the network
    
    imShape = features.shape[1:3]
    numChannels = features.shape[3]
    
    in_space = Conv2DSpace(shape = imShape,
                           num_channels = numChannels,
                           axes=('b', 0, 1, 'c'))

    
    w = 5
    channels = 16
    num_units = 300
    poolSize = 5

    learning_rate = 0.01
    dropout_rate = 0.5

    l1 = mlp.ConvRectifiedLinear(layer_name='L1',
                               output_channels=channels,
                               kernel_shape=(imShape[0],w),
                               pool_shape=(1,poolSize),
                               pool_stride=(1,poolSize),
                               irange = 0.005,
                               max_kernel_norm=1.9365,
                               detector_normalization = CrossChannelNormalizationBC01())
                               
                               
    output = mlp.Softmax(layer_name='y',
                         n_classes=4,
                         irange=.005,
                         max_col_norm=1.9365)
    
    layers = [l1, output]
    
    model = mlp.MLP(layers,
              input_space=in_space)
              
              
    termination_criterion = EpochCounter(max_epochs = 50)
    
    trainer = sgd.SGD(learning_rate=learning_rate,
                  batch_size=64,
                  learning_rule=learning_rule.Momentum(.5),
                  cost=Dropout(default_input_include_prob = dropout_rate,
                               default_input_scale = 1./(1.-dropout_rate)),
                  termination_criterion = termination_criterion,
                  monitoring_dataset={'valid': validDDM,
                                      'test': testDDM,
                                      'train': trainDDM})

    decay = sgd.LinearDecayOverEpoch(start=1,
                                 saturate=100,
                                 decay_factor=.1)
                                 
                                 
    velocity = learning_rule.MomentumAdjustor(final_momentum=.65,
                                          start=1,
                                          saturate=50)
    
    experiment = Train(dataset=trainDDM,
                       model=model,
                       algorithm=trainer,
                       extensions=[decay,velocity])

    experiment.main_loop()