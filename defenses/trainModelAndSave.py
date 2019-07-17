
from keras.models import Sequential
from keras.utils import np_utils
from keras.datasets import mnist
from keras.layers import Conv2D, Activation, MaxPooling2D, Dropout, Flatten, Dense


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


def main():
    training_dataset, test_dataset, labels_training_dataset, labels_test_dataset = loadDataset()
    cnn_Model = createModel()
    cnn_Model.compile(loss='categorical_crossentropy', optimizer='adadelta', metrics=['accuracy'])
    cnn_Model.fit(training_dataset, labels_training_dataset, epochs=10, batch_size=128, shuffle=True, verbose=1,
                  validation_data=(test_dataset, labels_test_dataset))
    cnn_Model.save('CNN_model.h5')

if __name__ == "__main__":
    main()