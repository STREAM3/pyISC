import unittest
import pyisc
import numpy as np
class MyTestCase(unittest.TestCase):
    def test_something(self):

        X = np.array([0.1, -0.1, 0.05, -0.01, 0.0, 0.11]).reshape((-1,1))

        try:
            ad = pyisc.AnomalyDetector(pyisc.P_Gaussian(1)).fit(X)

            self.assertFalse(True, "the probability model use column index that is larger than the data's max column index")
        except AssertionError:
            pass # OK

        ad = pyisc.AnomalyDetector(pyisc.P_Gaussian(0)).fit(X)


        self.assertTrue(np.array_equal(ad.anomaly_score(X), ad.anomaly_score(X)))



if __name__ == '__main__':
    unittest.main()
