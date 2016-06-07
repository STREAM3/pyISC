from unittest import TestCase

from numpy import histogram2d, zeros
from sklearn import mixture
from scipy.stats import norm

from pyisc import AnomalyDetector, P_ConditionalGaussianDependencyMatrix


class TestPConditionalGaussianDependencyMatrix(TestCase):

    def test_conditional_gaussian_dependency_matrix(self):
        X1 = mixture.sample_gaussian(mean=[2,2],covar=[[1.0,0.0],[0.0,1.0]], covariance_type='full',n_samples=1000,
                                     random_state=1001)

        X2 = mixture.sample_gaussian(mean=[7, 7], covar=[[1.0, 0.0], [0.0, 1.0]], covariance_type='full', n_samples=1000,
                                     random_state=1002)

        x,_,_ = histogram2d(list(X1[0]) + list(X2[0]), list(X1[1]) + list(X2[1]), range=[[0, 10], [0, 10]])
        x_mean = x.flatten()
        x_std = ((x_mean > 0)*2.0).flatten()


        sample_len = 100
        X = zeros((len(x_mean),sample_len))

        for i in range(len(x_mean)):
            X.T[i] = norm(x_mean[i], x_std[i]).rvs(sample_len,random_state=1003)


        ad = AnomalyDetector(
            P_ConditionalGaussianDependencyMatrix(range(len(x_mean)),10)
        ).fit(X)