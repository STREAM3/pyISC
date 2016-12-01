import unittest
from unittest import TestCase

from numpy.lib.index_tricks import c_
from numpy.ma.extras import vstack
from numpy.testing.utils import assert_allclose, assert_equal
from scipy.stats.stats import pearsonr

from pyisc import AnomalyDetector, P_Gaussian, P_ConditionalGaussian, P_ConditionalGaussianCombiner, cr_plus
from scipy.stats import norm
from numpy import array

class TestPConditionalGaussian(TestCase):

    def test_conditional_gaussian(self):
        x = array([[x0] for x0 in norm(0,1).rvs(1000)])

        gauss_scores = AnomalyDetector(P_Gaussian(0)).fit(x).anomaly_score(x)
        condgauss_scores = \
            AnomalyDetector(P_ConditionalGaussian([0], [])). \
                fit(x). \
                anomaly_score(x)

        assert_allclose(gauss_scores, condgauss_scores,atol=0.01,rtol=0.01)


        X = array([[x0, x1] for x0,x1 in zip(norm(0, 1).rvs(1000), norm(0, 1).rvs(1000)) ])

        gauss_scores_X = AnomalyDetector(P_Gaussian([0])).fit(X).anomaly_score(X)
        condgauss_scores_X = \
            AnomalyDetector(P_ConditionalGaussian([0],[1])). \
                fit(X). \
                anomaly_score(X)

        assert_allclose(gauss_scores_X, condgauss_scores_X, atol=0.3)


        X = array([[x0, x0+0.1*x1] for x0,x1 in zip(norm(0, 1).rvs(1000), norm(0, 1).rvs(1000)) ])


        # This is not equal at all
        gauss_scores_X = AnomalyDetector(P_Gaussian([0,1])).fit(X).anomaly_score(X)
        condgauss_scores_X = \
            AnomalyDetector(P_ConditionalGaussian([0,1],[])). \
                fit(X). \
                anomaly_score(X)

        assert_equal((pearsonr(gauss_scores_X, condgauss_scores_X) > 0.994), True)
        assert_allclose(gauss_scores_X, condgauss_scores_X, atol=2) # Very bad


        X = array([[x0, x0 + 0.1 * x1, x2] for x0, x1, x2 in c_[norm(0, 1).rvs(1000), norm(0, 1).rvs(1000), norm(0, 1).rvs(1000)]])

        # This is not equal at all
        gauss_scores_X = AnomalyDetector(P_Gaussian([0, 1])).fit(X).anomaly_score(X)
        condgauss_scores_X = \
            AnomalyDetector(P_ConditionalGaussian([0, 1], [])). \
                fit(X). \
                anomaly_score(X)

        assert_equal((pearsonr(gauss_scores_X, condgauss_scores_X) > 0.994), True)
        assert_allclose(gauss_scores_X, condgauss_scores_X, atol=2)  # Very bad


        X = array(
            [[x0, x0 + 0.1 * x1, x2] for x0, x1, x2 in c_[norm(0, 1).rvs(1000), norm(0, 1).rvs(1000), norm(0, 1).rvs(1000)]])

        # This is not equal at all
        gauss_scores_X = AnomalyDetector(P_Gaussian([0, 1,2])).fit(X).anomaly_score(X)
        condgauss_scores_X = \
            AnomalyDetector(
                P_ConditionalGaussianCombiner([
                    P_ConditionalGaussian([0], [1,2]),
                    P_ConditionalGaussian([1], [2]),
                    P_ConditionalGaussian([2], []),
                ])). \
                fit(X). \
                anomaly_score(X)

        assert_equal((pearsonr(gauss_scores_X, condgauss_scores_X) > 0.98), True)
        assert_allclose(gauss_scores_X, condgauss_scores_X, atol=5)  # Very bad


        # This is very much equal
        gauss_scores_X = AnomalyDetector(P_ConditionalGaussian([0, 1, 2], [])).fit(X).anomaly_score(X)
        condgauss_scores_X = \
            AnomalyDetector(
                P_ConditionalGaussianCombiner([
                    P_ConditionalGaussian([0], [1, 2]),
                    P_ConditionalGaussian([1], [2]),
                    P_ConditionalGaussian([2], []),
                ])). \
                fit(X). \
                anomaly_score(X)

        assert_allclose(gauss_scores_X, condgauss_scores_X, atol=0.001)


        # If we combine them using a ordinary combination rule by adding anomaly score together
        condgauss_scores_X2 = \
        AnomalyDetector(
            [
                P_ConditionalGaussian([0], [1, 2]),
                P_ConditionalGaussian([1], [2]),
                P_ConditionalGaussian([2], []),
            ], cr_plus). \
            fit(X). \
            anomaly_score(X)


        assert_equal((pearsonr(condgauss_scores_X, condgauss_scores_X2) > 0.99), True) # Good

        assert_allclose(condgauss_scores_X2, condgauss_scores_X, atol=2) # Bad


        #
        ad1 = AnomalyDetector(
            [P_Gaussian([i]) for i in range(len(X[0]))],
            cr_plus
        ).fit(X)
        s1 = ad1.anomaly_score(X)

        ad2 = AnomalyDetector(
            [P_ConditionalGaussian([i], []) for i in range(len(X[0]))],
            cr_plus
        ).fit(X)
        s2 = ad2.anomaly_score(X)

        print "r:", pearsonr(s1,s2)

        assert_allclose(s1, s2, rtol=0.01)  # OK

if __name__ == '__main__':
    unittest.main()