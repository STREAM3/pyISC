import unittest
from random import seed

from scipy import stats
import numpy as np
import pyisc

class test_SklearnOutlierDetection(unittest.TestCase):
    def test_outlier_detection(self):
        n_samples = 1000
        norm_dist = stats.norm(0, 1)

        truth = np.ones((n_samples,))
        truth[-100:] = -1

        X0 = norm_dist.rvs(n_samples)
        X = np.c_[X0*5, X0+norm_dist.rvs(n_samples)*2]

        uniform_dist = stats.uniform(-10,10)

        X[-100:] = np.c_[uniform_dist.rvs(100),uniform_dist.rvs(100)]

        outlier_detector = pyisc.SklearnOutlierDetector(
            100.0/n_samples,
            pyisc.P_Gaussian([0,1])
        )

        outlier_detector.fit(X)


        self.assertLess(outlier_detector.threshold_, 0.35)
        self.assertGreater(outlier_detector.threshold_, 0.25)

        predictions = outlier_detector.predict(X)

        accuracy =  sum(truth == predictions)/float(n_samples)

        print "accuracy", accuracy
        self.assertGreater(accuracy, 0.85)



if __name__ == '__main__':
    unittest.main()
