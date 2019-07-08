from keras.datasets.mnist import load_data
import numpy as np

image_height = 28 # standard
image_width = 28 # standard
num_channels = 1  # value for grayscale images

(digits_training, labels_training), (digits_test, labels_test) = load_data()


training = np.reshape(digits_training, (digits_training.shape[0], image_height, image_width, num_channels))
test = np.reshape(digits_test, (digits_test.shape[0],image_height, image_width, num_channels))

training_dataset_conv = training.astype('float32') / 255.



reversedone = (training_dataset_conv*255).astype(int)
reversed = np.reshape(reversedone,(60000,28,28))
d