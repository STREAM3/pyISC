import unittest

import pyisc;
import numpy as np
from scipy.stats import norm
from numpy.testing.utils import assert_allclose
import pickle

class MyTestCase(unittest.TestCase):
    def test_multivariate_gaussian(self):
        from scipy.stats import poisson, norm

        po_normal = poisson(10)
        po_anomaly = poisson(25)

        po_normal2 = poisson(2)
        po_anomaly2 = poisson(3)

        gs_normal = norm(1, 12)
        gs_anomaly = norm(2, 30)

        normal_len = 10000
        anomaly_len = 15

        data = np.column_stack(
            [
                [1] * (normal_len + anomaly_len),
                list(po_normal.rvs(normal_len)) + list(po_anomaly.rvs(anomaly_len)),
                list(po_normal2.rvs(normal_len)) + list(po_anomaly2.rvs(anomaly_len)),
                list(gs_normal.rvs(normal_len)) + list(gs_anomaly.rvs(anomaly_len)),
            ]
        )
        anomaly_detector = pyisc.AnomalyDetector(
            component_models=[
                pyisc.P_PoissonOnesided(1, 0),  # columns 1 and 0
                pyisc.P_Poisson(2, 0),  # columns 2 and 0
                pyisc.P_Gaussian(3)  # column 3
            ],
            output_combination_rule=pyisc.cr_max
        )

        anomaly_detector.fit(data);
        # This above should fail this test if the problem still occurs:
        '''
        ---------------------------------------------------------------------------
AssertionError                            Traceback (most recent call last)
<ipython-input-5-ecd0c0a2a8d4> in <module>()
----> 1 anomaly_detector.fit(data);

C:\ProgramData\Anaconda3\envs\pyISC_py27\lib\site-packages\_pyisc_modules\BaseISC.pyc in fit(self, X, y)
    313         
    314
--> 315         return self._fit(X,y)
    316
    317     def _fit(self,X,y=None):

C:\ProgramData\Anaconda3\envs\pyISC_py27\lib\site-packages\_pyisc_modules\BaseISC.pyc in _fit(self, X, y)
    352
    353             if data_object is not None:
--> 354                 assert self._max_index < data_object.length()  # ensure that data distribution has not to large index into the data
    355
    356                 return self._fit(data_object)

AssertionError:
        '''

        assert True;



if __name__ == '__main__':
    unittest.main()
