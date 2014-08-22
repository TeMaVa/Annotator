import numpy as np
import subprocess
import os
import cv2

class Nnforge(object):

    """This class is used to predict the class of input image.
       Internally, it uses nnForge, convolutional and fully-connected
       neural networks C++ library."""

    # underlying network needs to be custom build to use special input subdirectory
    # in prediction
    def __init__(self,
                 lock,
                 isColor = True,
                 bin_dir = "/home/johannes/Lataukset/nnForge/bin",
                 input_directory="/home/johannes/nnforge_git/input_data/autoverkko/",
                 working_directory="/home/johannes/nnforge_git/working_data/autoverkko/",
                 ):

        self.bin_dir = bin_dir
        self.isColor = isColor
        self.binary = os.path.join(self.bin_dir, "autoverkko")
        self.i_dir = input_directory
        self.image_dir = os.path.join(input_directory, "special")
        self.w_dir = working_directory
        self.annotationfile = os.path.join(self.image_dir, "annotation.csv")
        self.lock = lock
        self.predictionfile = os.path.join(self.w_dir, "prediction.csv")
        self.classfile = os.path.join(self.w_dir, "submission.csv")

    #def fit(self, X, y):

        #X_all = np.concatenate([X, X_test])
        #y_all = y
        #y[y==0] = -1
        #y_all = np.concatenate([y_all, np.zeros(X_test.shape[0])])

        #dump_svmlight_file(X_all, y_all, self.inputfile, zero_based=False)


        #cmd = []
        #if self.C:
            #cmd = ["svm_learn",
                #"-c", str(self.C),
                #"-t", str(self.kernel),
                #"-d", "2",
                #"-g", "1",
                #"-s", "1",
                #"-r", "1",
                #self.inputfile,
                #self.modelfile]
        #else:
            #cmd = ["svm_learn",
                #"-t", str(self.kernel),
                #"-d", "2",
                #"-g", "1",
                #"-s", "1",
                #"-r", "1",
                #self.inputfile,
                #self.modelfile]

        #subprocess.call(cmd)
        #os.remove(self.inputfile)

    # returns probabilities
    # X is matrix of images, with dtype=uint8
    def predict_proba(self, X):
        lines = []
        with self.lock:
            self.__writeImages__(X)
            cmd_prep = [self.binary,
                   "prepare_testing_data",
                    "--prediction_annotation", os.path.basename(self.annotationfile),
                    "--testing_folder", "special",
                    "--is_color", "true" if self.isColor else "false",
                       ]
            cmd_predict = [self.binary,
                        "test"]
            subprocess.call(cmd_prep)
            subprocess.call(cmd_predict)
            lines = open(self.predictionfile, "r").readlines()
        predictions = [",".join(line.split(",")[1:]) for line in lines]
        predVek = [np.fromstring(line, sep=",") for line in predictions]
        predVek = np.vstack(predVek)

        return predVek

    # returns class labels
    def predict(self, X):
        lines = []
        with self.lock:
            self.__writeImages__(X)
            cmd_prep = [self.binary,
                   "prepare_testing_data",
                    "--prediction_annotation", os.path.basename(self.annotationfile),
                    "--testing_folder", "special",
                    "--is_color", "true" if self.isColor else "false",
                        ]
            cmd_predict = [self.binary,
                        "test"]
            subprocess.call(cmd_prep)
            subprocess.call(cmd_predict)
            lines = open(self.classfile, "r").readlines()
        predictions = [",".join(line.split(",")[1:]) for line in lines]
        predVek = [np.fromstring(line, dtype=np.int, sep=",") for line in predictions]
        predVek = np.vstack(predVek)

        return predVek

    def __writeImages__(self, X):
        f = open(self.annotationfile, "w")
        for i in range(X.shape[0]):
            imgName = os.path.join(self.image_dir, "image{0}.png".format(i))
            cv2.imwrite(imgName, X[i,...])
            f.write(imgName + ",0\n")
        f.close()

