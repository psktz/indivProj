from keras.datasets.mnist import load_data
import numpy as np
import matplotlib.pyplot as plt


(digits_training, labels_training), (digits_test, labels_test) = load_data()

def printImage(image,label):
    plt.title('Label is {label}'.format(label=label))
    plt.axis("off")
    plt.imshow(image, cmap='gray')
    plt.show()

def reverseAndPrintImage(image,number):
    reversedone = (image * 255).astype(int)
    reversed = np.reshape(reversedone, (60000, 28, 28))
    plt.imshow(reversed[number],cmap='gray')
    plt.show()

reverseAndPrintImage(digits_training,0)

# plt.title('Label is {label}'.format(label=labels_training[3]))
# plt.axis("off")
# plt.imshow(digits_training[3], cmap='gray')
# plt.show()

# printImage(digits_training[3],labels_training[3])
#
# print(digits_training[1].shape)