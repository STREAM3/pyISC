"""
The Python Wrapper of all ISC classification methods that is compatible with scikit-learn
classifiers (http://scikit-learn.org)
"""
# --------------------------------------------------------------------------
# Copyright (C) 2014, 2015, 2016 SICS Swedish ICT AB
#
# Main author: Tomas Olsson <tol@sics.se>
#
# This code is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this code.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------------

import pyisc
from numpy import percentile

class SklearnOutlierDetector(pyisc.AnomalyDetector):
    threshold_ = None

    def __init__(self,contamination=0.01, *anomaly_detector_params0, **anomaly_detector_params1):
        '''
        This class can be used for classifying anomalies when the contamination fraction is known.
        It is implemented to be used together with the methods listed at
        http://scikit-learn.org/stable/auto_examples/covariance/plot_outlier_detection.html

        :param contamination: fraction of outliers in the data set
        :param anomaly_detector_params0: the same parameters as in the pyisc.AnomalyDetector
        :param anomaly_detector_params1: the same parameters as in the pyisc.AnomalyDetector
        '''
        self.contamination = contamination
        super(pyisc.AnomalyDetector,self).__init__(*anomaly_detector_params0, **anomaly_detector_params1)

    def fit(self,X):
        super(pyisc.AnomalyDetector, self).fit(X)
        ss = self.decision_function(X)
        self.threshold_ = percentile(ss, 100 * self.contamination)
        return self

    def decision_function(self,X):
        '''
        Returns a measure of anomalousness (the log probability of the data) from smallest (most anomalous) to high (least anomalous).
        :param X: an numpy array
        :param y: an numpy array
        :return: numpy array
        '''
        ss = self.compute_logp(X)

        return ss

    def predict(self, X):
        '''
        Returns an numpy array with 1 if a row is not anomlaous and -1 if anomalous
        :param X: an numpy array
        :param y: an numpy array
        :param decision_threshold: float value for deciding whether a point is anomalous
        :return: numpy array
        '''
        return 2 * (self.decision_function(X) > self.threshold_) - 1