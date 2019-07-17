import numpy as np
from sklearn.neighbors import KernelDensity
from keras.models import load_model
from createAdvFgsm import loadDataset
from trainDefensive import *


def main():
    model = load_model("CNN_model.h5")
    training_dataset, test_dataset, labels_training_dataset, labels_test_dataset = loadDataset()
    adversarial_test_dataset = np.load("adversarial_test_examples.npy")
    noisy_dataset = noiseFilter(test_dataset)
    # Check model accuracies on each sample type
    for tested_dataset, dataset in zip(['normal', 'noisy', 'adversarial'],
                                       [test_dataset, noisy_dataset, adversarial_test_dataset]):
        _, acc = model.evaluate(dataset, labels_test_dataset, batch_size=256, verbose=0)
        print("The accuracy of the model on the %s set is: %0.2f%%" % (tested_dataset, 100 * acc))
        if not tested_dataset == 'normal':
            l2_diff = np.linalg.norm(
                dataset.reshape((len(test_dataset), -1)) - test_dataset.reshape((len(test_dataset), -1)),
                axis=1).mean()
            print("Mean norm 2 perturbation size of the %s set is: %0.2f" % (tested_dataset, l2_diff))
    predicted_values = model.predict_classes(test_dataset, verbose=0, batch_size=256)
    correct_predictions = np.where(predicted_values == labels_test_dataset.argmax(axis=1))[0]
    test_dataset = test_dataset[correct_predictions]
    noisy_dataset = noisy_dataset[correct_predictions]
    adversarial_test_dataset = adversarial_test_dataset[correct_predictions]

    bayesian_uncertainty_metric_normal = monteCarloPrediction(model, test_dataset).var(axis=0).mean(axis=1)
    print("mc1 passed debug")
    bayesian_uncertainty_metric_noisy = monteCarloPrediction(model, noisy_dataset).var(axis=0).mean(axis=1)
    print("mc2 passed debug")
    bayesian_uncertainty_metric_adversarial = monteCarloPrediction(model, adversarial_test_dataset).var(axis=0).mean(
        axis=1)
    print("mc3 passed debug")
    training_density_features = densityFeatureEstimationMetric(model, training_dataset, batch_size=256)
    print("b1 passed debug")
    test_normal_density_features = densityFeatureEstimationMetric(model, test_dataset, batch_size=256)
    print("b2 passed debug")
    test_noisy_density_features = densityFeatureEstimationMetric(model, noisy_dataset, batch_size=256)
    print("b3 passed debug")

    test_adv_density_features = densityFeatureEstimationMetric(model, adversarial_test_dataset, batch_size=256)
    print("b4 passed debug")

    class_inds = {}
    for i in range(labels_training_dataset.shape[1]):
        class_inds[i] = np.where(labels_training_dataset.argmax(axis=1) == i)[0]
    kernel_denisities = {}
    for i in range(labels_training_dataset.shape[1]):
        kernel_denisities[i] = KernelDensity(kernel='gaussian', bandwidth=1.2).fit(
            training_density_features[class_inds[i]])

    print('Computing model predictions...')
    model_predictions_test_dataset = model.predict_classes(test_dataset, verbose=0, batch_size=256)
    model_predictions_noisy_dataset = model.predict_classes(noisy_dataset, verbose=0, batch_size=256)
    model_predictions_adversarial_dataset = model.predict_classes(adversarial_test_dataset, verbose=0, batch_size=256)

    print('density estimates')
    densitiy_metric_test = densityMetric(kernel_denisities, test_normal_density_features,
                                         model_predictions_test_dataset)
    densitiy_metric_noisy = densityMetric(kernel_denisities, test_noisy_density_features,
                                          model_predictions_noisy_dataset)
    densitiy_metric_adv = densityMetric(kernel_denisities, test_adv_density_features,
                                        model_predictions_adversarial_dataset)

    mc_z_test, mc_z_noisy, mc_z_adversarial = normalize(bayesian_uncertainty_metric_normal,
                                                        bayesian_uncertainty_metric_noisy,
                                                        bayesian_uncertainty_metric_adversarial)

    densities_z_test, densities_z_noisy, densities_z_adversarial = normalize(densitiy_metric_test,
                                                                             densitiy_metric_noisy,
                                                                             densitiy_metric_adv)

    y, categories, logisticReg = trainLogisticRegression(densities_z_adversarial,
                                                         np.concatenate((densities_z_test, densities_z_noisy)),
                                                         mc_z_adversarial,
                                                         np.concatenate((mc_z_test, mc_z_noisy)))

    probs = logisticReg.predict_proba(y)[:, 1]

    n_samples = len(test_dataset)
    _, _, auc_score = computeReceiverOpChar(probs[:2 * n_samples], probs[2 * n_samples:])
    print('ROC-AUC score: %0.4f' % auc_score)


if __name__ == "__main__":
    main()
