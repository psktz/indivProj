import warnings

import numpy as np
import tensorflow as tf
import os

from keras.engine.saving import load_model
from cleverhans.compat import reduce_max, reduce_sum, softmax_cross_entropy_with_logits
from cleverhans import utils_tf

from cleverhans.attacks import Attack
from cleverhans.attacks import FastGradientMethod
from cleverhans.dataset import MNIST
from cleverhans.attacks import fgm
from cleverhans.utils_keras import KerasModelWrapper, cnn_model
from tensorflow import keras
from imagePrinter import reverseAndPrintImage
from keras import backend as K

dirname = os.path.dirname(__file__)
filename_model = os.path.join(dirname, '../classifier/basicMNISTmodel2.h5')
# model = load_model(filename_model)

NB_EPOCHS = 6
BATCH_SIZE = 128
LEARNING_RATE = .001
TRAIN_DIR = 'train_dir'
FILENAME = 'mnist.ckpt'
LOAD_MODEL = False

train_start = 0
train_end = 10  # changed from 60000
test_start = 0
test_end = 10000
nb_epochs = NB_EPOCHS
batch_size = BATCH_SIZE
learning_rate = LEARNING_RATE
train_dir = TRAIN_DIR
filename = FILENAME
# load_model = LOAD_MODEL
testing = False
label_smoothing = 0.1

mnist = MNIST(train_start=train_start, train_end=train_end,
              test_start=test_start, test_end=test_end)
x_train, y_train = mnist.get_set('train')
x_test, y_test = mnist.get_set('test')

img_rows, img_cols, nchannels = x_train.shape[1:4]
print(img_rows, img_cols, nchannels)
nb_classes = y_train.shape[1]
print(filename)
sess = tf.Session()
keras.backend.set_session(sess)

model2 = cnn_model(img_rows=img_rows, img_cols=img_cols, channels=nchannels, nb_filters=64, nb_classes=nb_classes)
print("Defined Keras Model")

item = mnist.x_train

wrap = KerasModelWrapper(model2)

fgsm = FastGradientMethod(wrap, sess=sess)

fgsm_params = {'eps': 0.3, 'clip_min': 0., 'clip_max': 1.}

conv_tens = tf.convert_to_tensor(item,dtype=np.float32)

with tf.Session() as sess:
    K.set_session(sess)
    model = load_model(filename_model)
    adv = fgsm.generate(x_train, **fgsm_params)
    adv_images = adv.eval(session=sess, feed_dict={x: conv_tens})

reverseAndPrintImage(item, 0)

reverseAndPrintImage(adv, 0)

print(img_rows)
print(img_cols)
print(nchannels)
print(nb_classes)
