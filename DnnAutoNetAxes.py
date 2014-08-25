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

import time
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
    
    # Resize to 120 height and 80 width
    

    
#    targetsize = (imagedata.shape[2]/4,imagedata.shape[1]/2)
    targetsize = (80,120)    
#    features = np.empty([imagedata.shape[0],imagedata.shape[1]/2,imagedata.shape[2]/4,3])
    features = np.empty([imagedata.shape[0],120,80,3])
    features = np.uint8(features)
    
    for i in range(imagedata.shape[0]):
        features[i] = cv2.resize(imagedata[i],targetsize)
    
    # Slice 1/3 from bottom, this makes the picture square-shaped, the form which
    # is needed for Maxout neural net
    
    features = features[:,0:targetsize[1]-targetsize[1]/3,:,:]


#    features = np.uint8(features)
    
    
    return features


def OneHotEncode(labels):
    
    OHE = np.empty([len(labels),4])
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
    
    shuffledfeatures = np.empty([features.shape[0],features.shape[1],features.shape[2],3])
    shuffledlabels = [None]*features.shape[0]
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


# Returns augmented data

def DataAugmentation(imagedata):

    flippedimages = np.empty([features.shape[0],features.shape[1],features.shape[2],3])
    for i in range(imagedata.shape[0]):
        flippedimages[i] = cv2.flip(imagedata[i],1)
    
    flippedimages = np.uint8(flippedimages)
    
    
    
    cropmultiplier = 8
    croplimitH = features.shape[1]/cropmultiplier
    croplimitW = features.shape[2]/cropmultiplier
     
    croppedimages = np.empty([8,features.shape[0],features.shape[1]-croplimitH,features.shape[2]-croplimitW,3])
    
    
    for i in range(imagedata.shape[0]):
        # top left
        croppedimages[0,i] = imagedata[i,0:features.shape[1]-croplimitH,0:features.shape[2]-croplimitW]
        # top right
        croppedimages[1,i] = imagedata[i,0:features.shape[1]-croplimitH,croplimitW:]
        # bottom left
        croppedimages[2,i] = imagedata[i,croplimitH:,0:features.shape[2]-croplimitW]
        #bottom right
        croppedimages[3,i] = imagedata[i,croplimitH:,croplimitW:]
        
        #same for mirrored images

        # top left
        croppedimages[4,i] = flippedimages[i,0:features.shape[1]-croplimitH,0:features.shape[2]-croplimitW]
        # top right
        croppedimages[5,i] = flippedimages[i,0:features.shape[1]-croplimitH,croplimitW:]
        # bottom left
        croppedimages[6,i] = flippedimages[i,croplimitH:,0:features.shape[2]-croplimitW]
        #bottom right
        croppedimages[7,i] = flippedimages[i,croplimitH:,croplimitW:]
        
    
    return [flippedimages,croppedimages]

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
      
    
    [flippedimages,croppedimages] = DataAugmentation(features)
#    
#    
#    
#    features = np.concatenate([features,flippedimages])    
#    labels = np.append(labels,labels)
    
    print "Shuffling"
    
    [features,labels] = Shuffle(features,labels)
    
    print "Encoding labels"    
    
    labels = OneHotEncode(labels)

    
    features = np.float32(features)
    labels = np.float32(labels)    
    
    print "Feature shape is: " + str(features.shape)
    
    print "Divide into training, validitation, and test data"
      
    


    trainingpart = 0.8
    validpart = 0.1
    
    [trainFeatures,validFeatures,testFeatures,trainLabels,validLabels,testLabels] \
    = DataPartition(features,labels,trainingpart,validpart)
    
    trainFeatures = np.transpose(trainFeatures,(3,1,2,0))
    validFeatures = np.transpose(validFeatures,(3,1,2,0))
    testFeatures = np.transpose(testFeatures,(3,1,2,0))
    
    
    # Create DDM for neural net    
    
    trainDDM = dense_design_matrix.DenseDesignMatrix(\
        topo_view = trainFeatures, \
        y = trainLabels, \
        axes=('c', 0, 1, 'b'))   
    
    validDDM = dense_design_matrix.DenseDesignMatrix(\
        topo_view = validFeatures, \
        y = validLabels, \
        axes=('c', 0, 1, 'b'))

    testDDM = dense_design_matrix.DenseDesignMatrix(\
        topo_view = testFeatures, \
        y = testLabels, \
        axes=('c', 0, 1, 'b'))
    
    # TÄHÄN VÄLIIN PREPROCESSING
    
    preprocessor = Standardize()
    trainDDM.apply_preprocessor(preprocessor = preprocessor, can_fit = True)
    testDDM.apply_preprocessor(preprocessor = preprocessor, can_fit = False)
    validDDM.apply_preprocessor(preprocessor = preprocessor, can_fit = False)

    serial.save('4layermaxoutpreprocessor.pkl', preprocessor)
     
    # Define the input type for the network
    
    imShape = features.shape[1:3]
    numChannels = features.shape[3]
    
    in_space = Conv2DSpace(shape = imShape,
                           num_channels = numChannels,
                           axes=('c', 0, 1, 'b'))

    
    learning_rate = 0.01
    dropout_rate = 0.5

    # Please cite Maxout Networks. Ian J. Goodfellow, David Warde-Farley, Mehdi Mirza, Aaron Courville, and Yoshua Bengio. ICML 2013.




    l1 = maxout.MaxoutConvC01B(layer_name = 'M1',
                     pad =  0,
                     num_channels = 32,
                     num_pieces = 2,
                     kernel_shape = [12, 12],
                     pool_shape = [4, 4],
                     pool_stride = [2, 2],
                     irange=  0.005,
                     max_kernel_norm= 0.9)


    l2 = maxout.MaxoutConvC01B(layer_name = 'M2',
                     pad =  0,
                     num_channels = 16,
                     num_pieces = 2,
                     kernel_shape = [8, 8],
                     pool_shape = [4, 4],
                     pool_stride = [2, 2],
                     irange=  0.005,
                     max_kernel_norm= 0.9)

    l3 = maxout.MaxoutConvC01B(layer_name = 'M3',
                     pad =  0,
                     num_channels = 16,
                     num_pieces = 2,
                     kernel_shape = [6, 6],
                     pool_shape = [4, 4],
                     pool_stride = [2, 2],
                     irange=  0.005,
                     max_kernel_norm= 0.9)
                     
    l4 = maxout.MaxoutConvC01B(layer_name = 'M4',
                     pad =  0,
                     num_channels = 8,
                     num_pieces = 2,
                     kernel_shape = [4, 4],
                     pool_shape = [4, 4],
                     pool_stride = [2, 2],
                     irange=  0.005,
                     max_kernel_norm= 0.9)    
                               
    output = mlp.Softmax(layer_name='y',
                         n_classes=4,
                         irange=.005,
                         max_col_norm=1.9365)
    
    layers = [l1,l2,output]
    
    model = mlp.MLP(layers,
              input_space=in_space)
              
              
    termination_criterion = EpochCounter(max_epochs = 75)
    
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
                                 
                                 
    velocity = learning_rule.MomentumAdjustor(final_momentum=0.7,
                                          start=1,
                                          saturate=75)
    
    experiment = Train(dataset=trainDDM,
                       model=model,
                       algorithm=trainer,
                       extensions=[decay,velocity])

    experiment.main_loop()
    
    serial.save("4layermaxout.mdl", model)