# bunbun

import tensorflow as tf
from cleverhans.utils_tf import batch_eval, model_argmax
import keras.backend as K
from keras.models import load_model
import numpy as np
from keras.utils import np_utils
from keras.datasets import mnist


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
    print(training_dataset.shape)
    print(test_dataset.shape)
    print(ohe_labels_training_dataset.shape)
    print(ohe_labels_test_dataset.shape)
    print("test")
    return training_dataset, test_dataset, ohe_labels_training_dataset, ohe_labels_test_dataset


def fgsmTensorGenerator(training_input_placeholder, predicted_values, epsilon, clip_min=None, clip_max=None,
                        training_output_placeholder=None):
    if training_output_placeholder is None:
        training_output_placeholder = tf.to_float(
            tf.equal(predicted_values, tf.reduce_max(predicted_values, 1, keep_dims=True)))
    training_output_placeholder = training_output_placeholder / tf.reduce_sum(training_output_placeholder, 1,
                                                                              keep_dims=True)
    logits, = predicted_values.op.inputs
    loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=training_output_placeholder))
    gradient, = tf.gradients(loss, training_input_placeholder)

    signed_gradient = tf.sign(gradient)

    scaled_signed_grad = epsilon * signed_gradient

    adv_training_tensor = tf.stop_gradient(training_input_placeholder + scaled_signed_grad)
    if (clip_min is not None) and (clip_max is not None):
        adv_training_tensor = tf.clip_by_value(adv_training_tensor, clip_min, clip_max)
    return adv_training_tensor


def fgsmAdvExGenerator(sess, model, training_dataset, labels_training_dataset, epsilon, clip_min=None, clip_max=None,
                       batch_size=256):
    x = tf.placeholder(tf.float32, shape=(None,) + training_dataset.shape[1:])
    y = tf.placeholder(tf.float32, shape=(None,) + labels_training_dataset.shape[1:])
    adv_x = fgsmTensorGenerator(
        training_input_placeholder=x, predicted_values=model(x), epsilon=epsilon, clip_min=clip_min, clip_max=clip_max,
        training_output_placeholder=y
    )
    adversarial_dataset, = batch_eval(
        sess, [x, y], [adv_x], [training_dataset, labels_training_dataset], args={'batch_size': batch_size})
    return adversarial_dataset


def main():
    sess = tf.Session()
    print("1")
    K.set_session(sess)
    print("2")

    K.set_learning_phase(0)
    print("3")

    cnn_model = load_model('CNN_model.h5')
    print("4")

    _, test_dataset, _, labels_test_dataset = loadDataset()
    _, acc = cnn_model.evaluate(test_dataset, labels_test_dataset, batch_size=256, verbose=0)
    print("5")

    print("Accuracy on the test set: %0.2f%%" % (100 * acc))
    adversarial_dataset = fgsmAdvExGenerator(sess, cnn_model, test_dataset, labels_test_dataset, epsilon=0.3)
    print("6")

    np.save('adversarial_test_examples', adversarial_dataset)
    print("7")

    sess.close()
    print("SUCCESS!")


if __name__ == "__main__":
    main()
