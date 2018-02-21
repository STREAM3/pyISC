import unittest

import pyisc;
import numpy as np
from scipy.stats import poisson, norm

class MyTestCase(unittest.TestCase):
    def test_something(self):
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
                pyisc.P_Gaussian(1),  # columns 1 and 0
                pyisc.P_Gaussian(2),  # columns 2 and 0
                pyisc.P_Gaussian(3)  # column 3
            ],
            output_combination_rule=pyisc.cr_max
        )

        anomaly_detector.fit(data);

        json =  anomaly_detector.exportJSon()

        print json

        anomaly_detector2 = pyisc.AnomalyDetector(
            component_models=[
                pyisc.P_Gaussian(1),  # columns 1 and 0
                pyisc.P_Gaussian(2),  # columns 2 and 0
                pyisc.P_Gaussian(3)  # column 3
            ],
            output_combination_rule=pyisc.cr_max
        )

        anomaly_detector2.importJSon(json)
        
        json2 = anomaly_detector2.exportJSon()

        print json2

        self.assertEqual(json, json2)

        self.assertTrue(np.array_equal(anomaly_detector.anomaly_score(data), anomaly_detector2.anomaly_score(data)))


if __name__ == '__main__':
    unittest.main()
