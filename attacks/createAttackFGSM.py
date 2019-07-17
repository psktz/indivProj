import os

import tensorflow as tf
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt

from cleverhans.attacks import FastGradientMethod
from cleverhans.compat import flags
from cleverhans.dataset import MNIST
from cleverhans.loss import CrossEntropy
from cleverhans.train import train
from cleverhans.utils import AccuracyReport
from cleverhans.utils_keras import cnn_model
from cleverhans.utils_keras import KerasModelWrapper
from cleverhans.utils_tf import model_eval


FLAGS = flags.FLAGS


def loadDataset(training_starting_point, training_end_point, testing_starting_point, testing_end_point):
    mnist = MNIST(train_start=training_starting_point, train_end=training_end_point,
                  test_start=testing_starting_point, test_end=testing_end_point)
    training_dataset, label_training_dataset = mnist.get_set('train')
    testing_dataset, label_testing_dataset = mnist.get_set('test')
    return training_dataset, label_training_dataset, testing_dataset, label_testing_dataset


def getDatasetParameters(training_dataset, label_training_dataset):
    rows, columns, channels = training_dataset.shape[1:4]
    categories = label_training_dataset.shape[1]
    return rows, columns, channels, categories


def generateNeuralNet(rows, columns, channels, filters, categories):
    neural_net_model = cnn_model(img_rows=rows, img_cols=columns, channels=channels, nb_filters=filters,
                                 nb_classes=categories)
    return neural_net_model

def main(argv=None):
    NB_EPOCHS = 1
    BATCH_SIZE = 128
    LEARNING_RATE = .001
    train_dir = "train_dir"
    filename = "mnist.ckpt"
    load_model = False
    testing = False
    tf.keras.backend.set_learning_phase(0)

    report = AccuracyReport()

    tf.set_random_seed(1234)
    label_smoothing = 0.1

    if keras.backend.image_data_format() != 'channels_last':
        raise NotImplementedError("this tutorial requires keras to be configured to channels_last format")


    sess = tf.Session()
    keras.backend.set_session(sess)
    fgsm_params = {'eps': 0.3,
                   'clip_min': 0.,
                   'clip_max': 1.}
    training_dataset, label_training_dataset, testing_dataset, label_testing_dataset = loadDataset(0, 60000, 0, 10000)
    rows, columns, channels, categories = getDatasetParameters(training_dataset, label_training_dataset)

    x = tf.placeholder(tf.float32, shape=(None, rows, columns,
                                          channels))
    y = tf.placeholder(tf.float32, shape=(None, categories))

    neural_net_model = generateNeuralNet(rows, columns, channels, 64, categories)

    preds = neural_net_model(x)

    def evaluate():
        print("Skipped evaluation")
    train_params = {
        'nb_epochs': NB_EPOCHS,
        'batch_size': BATCH_SIZE,
        'learning_rate': LEARNING_RATE,
        'train_dir': train_dir,
        'filename': filename
    }

    rng = np.random.RandomState([2017, 8, 30])
    if not os.path.exists(train_dir):
        os.mkdir(train_dir)
    ckpt = tf.train.get_checkpoint_state(train_dir)
    print(train_dir, ckpt)
    ckpt_path = False if ckpt is None else ckpt.model_checkpoint_path
    wrap = KerasModelWrapper(neural_net_model)

    loss = CrossEntropy(wrap, smoothing=label_smoothing)
    train(sess, loss, training_dataset, label_training_dataset, evaluate=evaluate, args=train_params, rng=rng)


    fgsm = FastGradientMethod(wrap, sess = sess )
    adv_x = fgsm.generate(x, **fgsm_params)
    adv_x = tf.stop_gradient(adv_x)

    x_train2 = training_dataset[0:100]
    advy = adv_x.eval(session=sess, feed_dict={x: x_train2})
    def reverseAndPrintImage(image, number):
        reversedone = (image * 255).astype(int)
        reversed = np.reshape(reversedone, (100, 28, 28))
        plt.imshow(reversed[number], cmap='gray')
        plt.show()

    reverseAndPrintImage(advy,0)
    reverseAndPrintImage(advy,1)
    reverseAndPrintImage(advy,2)
    reverseAndPrintImage(advy,3)
if __name__ == '__main__':
    tf.app.run()
