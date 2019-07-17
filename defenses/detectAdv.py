from __future__ import division, absolute_import, print_function

import os
import multiprocessing as mp
from subprocess import call
import warnings
import numpy as np
import scipy.io as sio
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from sklearn.linear_model import LogisticRegressionCV
from sklearn.preprocessing import scale
import keras.backend as K
from keras.datasets import mnist, cifar10
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.regularizers import l2
import pickle


# STDEVS = {
#     'mnist': {'fgsm': 0.310, 'bim-a': 0.128, 'bim-b': 0.265}, }


def normalizeDataset(training_dataset, test_dataset):
    training_dataset = training_dataset.astype('float32')
    training_dataset = training_dataset / 255
    test_dataset = test_dataset.astype('float32')
    test_dataset = test_dataset / 255
    return training_dataset, test_dataset


def oneHotEncode(labels_training_dataset, labels_test_dataset):
    labels_training_dataset = np_utils.to_categorical(labels_training_dataset, 10)
    labels_test_dataset = np_utils.to_categorical(labels_test_dataset, 10)
    return labels_training_dataset, labels_test_dataset


def loadDataset():
    (training_dataset, labels_training_dataset), (test_dataset, labels_test_dataset) = mnist.load_data()
    # reshape to (n_samples, 28, 28, 1)
    training_dataset = training_dataset.reshape(-1, 28, 28, 1)
    test_dataset = test_dataset.reshape(-1, 28, 28, 1)
    training_dataset, test_dataset = normalizeDataset(training_dataset, test_dataset)
    ohe_labels_training_dataset, ohe_labels_test_dataset = oneHotEncode(labels_training_dataset, labels_test_dataset)
    return training_dataset, test_dataset, ohe_labels_training_dataset, ohe_labels_test_dataset


def createModel():
    model = Sequential()
    model.add(Conv2D(64, (3, 3), padding='valid', input_shape=(28, 28, 1)))
    model.add(Activation('relu'))
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.5))
    model.add(Flatten())
    model.add(Dense(128))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(10))
    model.add(Activation('softmax'))
    return model


def noisyFilter(training_dataset):
    noisy_trainig_dataset = np.minimum(
        np.maximum(training_dataset + np.random.normal(loc=0, scale=0.310, size=training_dataset.shape), 0), 1)
    return noisy_trainig_dataset


def fgsmGenerator(sess,x,predictions,test_dataset,eps_list,model_name,no_of_adv_ex,result_folder):
    test_dataset=test_dataset[:no_of_adv_ex,:]
