import unittest

import pyisc;
import numpy as np
from scipy.stats import norm
from numpy.testing.utils import assert_allclose
import pickle

class MyTestCase(unittest.TestCase):
    def test_multivariate_gaussian(self):
        po_normal = norm(1.1, 5)
        po_anomaly = norm(1.5, 7)

        po_normal2 = norm(2.2, 10)
        po_anomaly2 = norm(3, 12)

        gs_normal = norm(1, 12)
        gs_anomaly = norm(2, 30)

        normal_len = 100
        anomaly_len = 15

        data = np.column_stack(
            [
                list(po_normal.rvs(normal_len)) + list(po_anomaly.rvs(anomaly_len)),
                list(po_normal2.rvs(normal_len)) + list(po_anomaly2.rvs(anomaly_len)),
                list(gs_normal.rvs(normal_len)) + list(gs_anomaly.rvs(anomaly_len)),
            ]
        )

        anomaly_detector = pyisc.AnomalyDetector(
            component_models=[
                pyisc.P_Gaussian(0),  # columns 1 and 0
                pyisc.P_Gaussian(1),  # columns 2 and 0
                pyisc.P_Gaussian(2)  # column 3
            ],
            output_combination_rule=pyisc.cr_max
        )

        anomaly_detector.fit(data);

        json = anomaly_detector.exportJSon()


        p =  pickle.dumps(anomaly_detector)

        print p

        anomaly_detector2 = pickle.loads(p)

        json2 = anomaly_detector2.exportJSon()

        print json2

        assert_allclose(anomaly_detector.anomaly_score(data), anomaly_detector2.anomaly_score(data))
        self.assertEqual(json, json2)



    def test_conditional_gaussian(self):
        po_normal = norm(1.1, 5)
        po_anomaly = norm(1.5, 7)

        po_normal2 = norm(2.2, 10)
        po_anomaly2 = norm(3, 12)

        gs_normal = norm(1, 12)
        gs_anomaly = norm(2, 30)

        normal_len = 100
        anomaly_len = 15

        data = np.column_stack(
            [
                list(po_normal.rvs(normal_len)) + list(po_anomaly.rvs(anomaly_len)),
                list(po_normal2.rvs(normal_len)) + list(po_anomaly2.rvs(anomaly_len)),
                list(gs_normal.rvs(normal_len)) + list(gs_anomaly.rvs(anomaly_len)),
            ]
        )

        anomaly_detector = pyisc.AnomalyDetector(
            component_models=[
                pyisc.P_ConditionalGaussianCombiner([pyisc.P_ConditionalGaussian([0], [1]), pyisc.P_ConditionalGaussian([1], [2])])
            ],
            output_combination_rule=pyisc.cr_max
        )

        anomaly_detector.fit(data);

        json = anomaly_detector.exportJSon()

        print json

        p = pickle.dumps(anomaly_detector)

        print p

        anomaly_detector2 = pickle.loads(p)

        json2 = anomaly_detector2.exportJSon()

        print json2

        self.assertEqual(json, json2)

        assert_allclose(anomaly_detector.anomaly_score(data), anomaly_detector2.anomaly_score(data))
if __name__ == '__main__':
    unittest.main()
