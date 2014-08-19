# -*- coding: utf-8 -*-
"""
Created on Wed Aug 13 13:40:04 2014

@author: vartiai6
"""
import numpy as np


from pylearn2.datasets import dense_design_matrix
from pylearn2.space import Conv2DSpace
from pylearn2.utils import serial
from pylearn2.expr.normalize import CrossChannelNormalizationBC01
from pylearn2.datasets.preprocessing import Standardize

from theano import tensor as T
from theano import function

import threading
import pickle 
import os
import sys
import cv2
import csv


# Class for neural network that predicts auto types

class AutoNet(object):
    
    # Initialize class, load trained model    
    
    def __init__(self):
        
        # Mites tämä määritellään? Jotain ympäristömuuttujia?
        modelpath = "/home/vartiai6/Autoproject/4layermaxout.mdl"
        self.model = serial.load(modelpath)
        processorpath = "/home/vartiai6/Autoproject/4layermaxoutpreprocessor.pkl"
        self.preprocessor = serial.load(processorpath)

    # This feature extraction function must be exactly the same as in training phase
        
    def __feature_extraction__(self,imagedata):
    
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
       
       
       
    # Public function, predicts class according to given image
    
    def predict_proba(self,imagedata):
        
        features = self.__feature_extraction__(imagedata)
        
        features = np.float32(features)
        features = np.transpose(features,(3,1,2,0))      
        
        DDM = dense_design_matrix.DenseDesignMatrix(
        topo_view = features,
        axes=('c', 0, 1, 'b'))
        
        # Esikäsittely
    
        DDM.apply_preprocessor(self.preprocessor, can_fit = True)
        
        
        imShape = features.shape[1:3]
        numChannels = features.shape[3]
    
        in_space = Conv2DSpace(shape = imShape,
                           num_channels = numChannels,
                           axes=('c', 0, 1, 'b'))
        
#        return features

        # Theano stuff, pitäisikö nämä luoda jo olion alustuksessa

        X = self.model.get_input_space().make_theano_batch()
        Y = self.model.fprop( X )
        f = function( [X], Y )

        predictions = f(DDM.get_topological_view(DDM.X))
        predictions = np.fliplr(predictions)
            
        predictions = np.float64(predictions)
        
        
        
        return predictions
