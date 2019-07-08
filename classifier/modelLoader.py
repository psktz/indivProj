from keras.utils import to_categorical
import numpy as np
from keras.models import load_model
from keras.datasets.mnist import load_data

image_height = 28 # standard
image_width = 28 # standard
num_channels = 1  # value for grayscale images


model = load_model('basicMNISTmodel.h5')
print(model.summary())


(digits_training, labels_training), (digits_test, labels_test) = load_data()


training = np.reshape(digits_training, (digits_training.shape[0], image_height, image_width, num_channels))
test = np.reshape(digits_test, (digits_test.shape[0],image_height, image_width, num_channels))

total_classes = 10
training_categories = to_categorical(labels_training,total_classes)
test_categories = to_categorical(labels_test,total_classes)
training_categories.shape, test_categories.shape


test_dataset_conv = test.astype('float32') / 255.

# evaluate the model
loss, accuracy = model.evaluate(test_dataset_conv, test_categories, batch_size=64)
print('Test Loss is: ' + str(loss) + " and Test Accuracy is: " + str(accuracy))