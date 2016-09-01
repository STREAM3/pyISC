from unittest import TestCase

from numpy import  array,r_

from numpy.ma.testutils import assert_close
from numpy.testing.utils import assert_allclose, assert_equal
from scipy.stats import norm
from scipy.stats.stats import pearsonr
from sklearn.utils import shuffle

from pyisc import AnomalyDetector, \
    P_ConditionalGaussianDependencyMatrix, \
    P_ConditionalGaussianCombiner, \
    P_ConditionalGaussian, \
    P_Gaussian, cr_plus, cr_max, \
    SklearnClassifier, SklearnClusterer

import pylab as plt

norm_dist = norm(0, 1)


def sample_markov_chain(length, noise=0.1):
    global norm_dist
    sample = []
    sample.append(norm_dist.rvs(1)[0])
    for i in range(1,length):
        sample.append(norm_dist.rvs(1)[0]*noise+sample[i-1])

    return sample

class TestPConditionalGaussianDependencyMatrix(TestCase):



    def test_conditional_gaussian_dependency_matrix(self):
        length = 100
        n_samples = 1000
        X = array([sample_markov_chain(length) for _ in range(n_samples)])


        # Next two should be equal
        s0 = AnomalyDetector(
            P_ConditionalGaussianDependencyMatrix(range(length),length)
        ).fit(X).anomaly_score(X)

        ad1=AnomalyDetector(
            P_ConditionalGaussianCombiner([P_ConditionalGaussian([i + 1], [i]) for i in range(length - 1)]+[P_ConditionalGaussian([0], [])]),
            cr_plus
        ).fit(X)
        s1 = ad1.anomaly_score(X)

        assert_allclose(s0, s1, rtol=0.0001)  # OK

        # Most likely, these two are not equal but highly correlated
        ad2=AnomalyDetector(
            [P_ConditionalGaussian([i], []) for i in range(length)],
            cr_plus
        ).fit(X)
        s2 = ad2.anomaly_score(X)

        ad3=AnomalyDetector(
            P_ConditionalGaussianCombiner([P_ConditionalGaussian([i], []) for i in range(length)]),
            cr_plus
        ).fit(X)
        s3 = ad3.anomaly_score(X)

        assert_equal(pearsonr(s2,s3)> 0.985, True)


        # Test classification
        Y = array([sample_markov_chain(length,0.2) for _ in range(n_samples)])
        Z = array([sample_markov_chain(length,0.3) for _ in range(n_samples)])


        data = r_[X,Y,Z]
        labels = r_[['X']*len(X), ['Y']*len(Y), ['Z']*len(Z)]

        data_index = shuffle(range(len(data)))
        training_set = data_index[:n_samples*2]
        test_set = data_index[n_samples*2:]

        models = {
            'independent gaussian':
                AnomalyDetector([P_Gaussian([i]) for i in range(length)],cr_plus),
            'independent conditional gaussian':
                AnomalyDetector([P_ConditionalGaussian([i], []) for i in range(length)],cr_plus),
            'independent conditional gaussian with combiner':
                AnomalyDetector(P_ConditionalGaussianCombiner([P_ConditionalGaussian([i], []) for i in range(length)])),
            'single conditional gaussian with combiner':
                AnomalyDetector(P_ConditionalGaussianCombiner([P_ConditionalGaussian([i], [i-1]) for i in range(1, length)]+
                                                              [P_ConditionalGaussian([0], [])])),
            'dependency matrix':
                AnomalyDetector(P_ConditionalGaussianDependencyMatrix(range(length),length))
        }

        all_acc = {}
        for key in models:
            ad=models[key].fit(data[training_set], labels[training_set])

            adclf = SklearnClassifier.clf(ad)

            labels_predicted = adclf.predict(data[test_set])
            accuracy = sum(labels[test_set]==labels_predicted)/float(len(test_set))
            all_acc[key] = accuracy
            print key, "accuracy = ", accuracy


        assert_close(all_acc['independent gaussian'],all_acc['independent conditional gaussian'],decimal=2)
        assert_close(all_acc['independent gaussian'], all_acc['independent conditional gaussian with combiner'],decimal=2)
        assert_close(all_acc['single conditional gaussian with combiner'], all_acc['dependency matrix'],decimal=2)


        # Test clustering

        # Add fourth class/cluster

        U = array([sample_markov_chain(length,0.5) for _ in range(n_samples)])

        data = r_[data, U]
        labels = r_[labels, ['U']*len(U)]

        clusterer = SklearnClusterer(P_ConditionalGaussianDependencyMatrix(range(length),length))
        clusterer.fit_anomaly_detector(data,10)

        plt.plot(range(1,len(clusterer.cluster_curve_)+1),clusterer.cluster_curve_)

        import sklearn.datasets

        iris = sklearn.datasets.load_iris()

        clusterer_iris = SklearnClusterer(P_Gaussian(range(4)))
        clusterer_iris.fit_anomaly_detector(iris['data'],20)

        plt.plot(range(1,len(clusterer_iris.cluster_curve_)+1),clusterer_iris.cluster_curve_)
