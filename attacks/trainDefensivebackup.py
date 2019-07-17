import numpy as np
import keras.backend as K
import multiprocessing as mp
from sklearn.preprocessing import scale
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics import roc_curve, auc


def noiseFilter(training_dataset):
    noisy_trainig_dataset = np.minimum(
        np.maximum(training_dataset + np.random.normal(loc=0, scale=0.310, size=training_dataset.shape), 0), 1)
    return noisy_trainig_dataset


def mcPrediction(model, X, iterations=50, batch_size=256):
    shape = model.layers[-1].output.shape[-1].value
    get_output = K.function([model.layers[0].input, K.learning_phase()], [model.layers[-1].output])

    def predict():
        batch_number = int(np.ceil(X.shape[0] / float(batch_size)))
        prediction = np.zeros(shape=(len(X), shape))
        for i in range(batch_number):
            prediction[i * batch_size:(i + 1) * batch_size] = get_output([X[i * batch_size:(i + 1) * batch_size], 1])[0]
        return prediction

    predictions = []
    for i in range(iterations):
        predictions.append(predict())
    return np.asarray(predictions)


def densityFeatureEstimationMetric(model, dataset, batch_size=256):
    shape = model.layers[-4].output.shape[-1].value
    hidden_function = K.function([model.layers[0].input, K.learning_phase()], [model.layers[-4].output])
    batch_number = int(np.ceil(dataset.shape[0] / float(batch_size)))
    output = np.zeros(shape=(len(dataset), shape))
    for i in range(batch_number):
        output[i * batch_size:(i + 1) * batch_size] = \
            hidden_function([dataset[i * batch_size:(i + 1) * batch_size], 0])[0]
    return output


def unzip_helper(input):
    array, kernel_density = input
    return kernel_density.score_samples(np.reshape(array, (1, -1)))[0]


def denisityMetric(kernel_density, samples, preds):
    p = mp.Pool()
    results = np.asarray(p.map(unzip_helper, [(array, kernel_density[i]) for array, i in zip(samples, preds)]))
    p.close()
    p.join()
    return results


def normalize(test_dataset, noisy_dataset, adversarial_dataset):
    n_samples = len(test_dataset)
    total = scale(np.concatenate((test_dataset, noisy_dataset, adversarial_dataset)))
    return total[:n_samples], total[n_samples:2 * n_samples], total[2 * n_samples:]


def trainLogisticRegression(postive_density_metric, negative_density_metric, positive_uncertainties,
                            negative_uncertainties):
    values_neg = np.concatenate((negative_density_metric.reshape((1, -1)), negative_uncertainties.reshape((1, -1))),
                                axis=0).transpose([1, 0])
    values_pos = np.concatenate((postive_density_metric.reshape((1, -1)), positive_uncertainties.reshape((1, -1))),
                                axis=0).transpose([1, 0])
    y = np.concatenate((values_neg, values_pos))
    category = np.concatenate((np.zeros_like(negative_density_metric), np.ones_like(postive_density_metric)))
    logisticReg = LogisticRegressionCV(n_jobs=-1).fit(y, category)
    return y, category, logisticReg


def computeReceiverOpChar(negative_probabilities, positive_probabilities):
    probs = np.concatenate((negative_probabilities, positive_probabilities))
    categories = np.concatenate((np.zeros_like(negative_probabilities), np.ones_like(positive_probabilities)))
    fpr, tpr, _ = roc_curve(categories, probs)
    area_under_curve = auc(fpr, tpr)
    return fpr, tpr, area_under_curve


def main():
    print("yes")


if __name__ == '__main__':
    main()
