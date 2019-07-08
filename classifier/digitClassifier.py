# Section that loads the MNIST dataset

from keras.datasets.mnist import load_data
import matplotlib.pyplot as plt
import numpy as np
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout


(digits_training, labels_training), (digits_test, labels_test) = load_data()

# Section that displays random images from the loaded dataset to check if the loading was succesful

np.random.seed(21)

random_numbers = np.random.randint(0, digits_training.shape[0],32)
digits = digits_training[random_numbers]
labels = labels_training[random_numbers]


rows = 4
cols = 8
figure, plot_axis = plt.subplots(rows, cols, figsize=(12,5),
                     gridspec_kw={'wspace':0.03, 'hspace':1.4},
                     squeeze=True)

for row in range(rows):
    for column in range(cols):
        index = row * 8 + column
        plot_axis[row,column].axis("off")
        plot_axis[row,column].imshow(digits[index], cmap='gray')
        plot_axis[row,column].set_title('Label: %d' % labels[index])
plt.show()
plt.close()


# Section related to the preprocessing of the MNIST dataset

image_height = 28 # standard
image_width = 28 # standard
num_channels = 1  # value for grayscale images

training = np.reshape(digits_training, (digits_training.shape[0], image_height, image_width, num_channels))
test = np.reshape(digits_test, (digits_test.shape[0],image_height, image_width, num_channels))

# image data conversion
training_dataset_conv = training.astype('float32') / 255.
test_dataset_conv = test.astype('float32') / 255.

# one-hot encoding
total_classes = 10
training_categories = to_categorical(labels_training,total_classes)
test_categories = to_categorical(labels_test,total_classes)
training_categories.shape, test_categories.shape


# Section related to training/testing/validation split

random_shuffle = np.random.permutation(len(training_dataset_conv))

training_dataset = training_dataset_conv[random_shuffle]
training_categories = training_categories[random_shuffle]

# cross-validation splits
split_percentage = 10
split_point = int(split_percentage/100 * len(training_dataset))

validation_dataset = training_dataset[:split_point,:]
validation_categories = training_categories[:split_point,:]

training_dataset = training_dataset[split_point:,:]
training_categories = training_categories[split_point:,:]


def MNIST_convolutional_NN():
    model = Sequential()
    model.add(Conv2D(filters=32, kernel_size=(3,3), activation='relu', padding='same',
                     input_shape=(image_height, image_width, num_channels)))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Conv2D(filters=64, kernel_size=(3,3), activation='relu', padding='same'))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Conv2D(filters=64, kernel_size=(3,3), activation='relu', padding='same'))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Flatten())

    model.add(Dense(128, activation='relu'))
    model.add(Dense(total_classes, activation='softmax'))
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

model = MNIST_convolutional_NN()
print(model.summary())


results = model.fit(training_dataset, training_categories,
                    epochs=15, batch_size=64,
                    validation_data=(validation_dataset, validation_categories))


loss, accuracy = model.evaluate(test_dataset_conv, test_categories, batch_size=64)


model.save("basicMNISTmodel.h5")
model.model.save("basicMNISTmodel2.h5")

print('Test Loss is: ' + str(float(loss)) + " and Test Accuracy is:" + str(float(accuracy)))


