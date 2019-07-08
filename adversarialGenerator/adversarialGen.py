import os
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, '../classifier/basicMNISTmodel.h5')
from imagePrinter import printImage
import numpy as np
from keras.datasets.mnist import load_data
from keras.engine.saving import load_model

import keras.backend as K


(digits_training, labels_training), (digits_test, labels_test) = load_data()


image_height = 28 # standard
image_width = 28 # standard
num_channels = 1  # value for grayscale images



test = np.reshape(digits_test, (digits_test.shape[0],image_height, image_width))
test_dataset_conv = test.astype('float32') / 255.

print(test_dataset_conv.shape)



model = load_model(filename)

x= test_dataset_conv[0]
print(x.shape)

# Get current session (assuming tf backend)
sess = K.get_session()
# Initialize adversarial example with input image
x_adv = x
print(x_adv.shape)
printImage(x_adv,1)
# Added noise
x_noise = np.zeros_like(x)


# printImage(digits_test[0],labels_test[0])

epochs = 400
epsilon = 0.05
target_class = 2
prev_probs = []

for i in range(epochs):
    # One hot encode the target class
    target = K.one_hot(target_class, 10)

    # Get the loss and gradient of the loss wrt the inputs
    loss = -1 * K.categorical_crossentropy(target, model.output)
    grads = K.gradients(loss, model.input)
    grads = np.asarray(grads)
    # grads = np.reshape(grads,(1,784))

    # Get the sign of the gradient
    delta = np.sign(grads)
    x_noise = x_noise + delta

    # Perturb the image
    x_adv = x_adv + epsilon * delta

    # Get the new image and predictions
    # x_adv = sess.run(np.array(x_adv,ndmin=4), feed_dict={model.input: np.array(x_adv,ndmin=4)})
    # preds = model.predict(x_adv)

    # Store the probability of the target class
    # prev_probs.append(preds[0][target_class])

    if i % 20 == 0:
        print(i)
        print(x_adv.shape)
# print(i, model.predict_classes(np.array(x_adv,ndmin=4)))

printImage(x_adv,1)


prediction = model.predict_classes(np.array(x_adv,ndmin=4))
print(prediction) #2


