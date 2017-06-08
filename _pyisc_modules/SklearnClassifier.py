"""
The Python Wrapper of all ISC classification methods that is compatible with scikit-learn
classifiers (http://scikit-learn.org)
"""
# --------------------------------------------------------------------------
# Copyright (C) 2014, 2015, 2016, 2017 SICS Swedish ICT AB
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
from _pyisc import _AnomalyDetector__ClassifyData

from numpy import array, ndarray
from numpy.ma.core import exp
from scipy.misc import logsumexp

from sklearn.base import ClassifierMixin, BaseEstimator
from pyisc import P_Gaussian, BaseISC, cr_max
import pyisc


class SklearnClassifier(BaseISC, BaseEstimator, ClassifierMixin):
    classification_threshold = None

    def __init__(self, component_models=P_Gaussian(0),
                 classification_threshold=1e12,
                 output_combination_rule=cr_max,
                 training_anomaly_threshold = 0.0):

        '''

        :param classification_threshold: (optional) a threshold for specifying that instances with anomaly scores below
        the threshold should be classified. If not specified, the anomaly threshold is set to very large.
        :return:
        '''
        self.classification_threshold = classification_threshold
        super(SklearnClassifier, self).__init__(component_models,output_combination_rule,training_anomaly_threshold)

    @staticmethod
    def clf(anomaly_detector,classification_threshold=1e12):
        '''
        Converts a pyisc AnomalyDetector into a SklearnClassifier
        :param self:
        :param anomaly_detector:
        :param classification_threshold:
        :return:
        '''
        assert isinstance(anomaly_detector, pyisc.AnomalyDetector)
        classifier =  SklearnClassifier()
        classifier._anomaly_detector = anomaly_detector._anomaly_detector
        classifier.class_column = anomaly_detector.class_column
        classifier.anomaly_threshold = anomaly_detector.anomaly_threshold
        classifier.classes_ = anomaly_detector.classes_
        classifier.is_clustering = anomaly_detector.is_clustering
        classifier.num_of_partitions = anomaly_detector.num_of_partitions
        classifier.classification_threshold = classification_threshold

        return classifier

    def predict(self, X):
        '''
        This method classifies each instance in X with a class, if the anomaly detector was trained with classes.

        :param X: a numpy array or a pyisc DataObject
        :return: an array with a classification for each instance in X, an anomalous instance below given classification threshold is classified as None.
        '''

        probs = self.predict_log_proba(X)
        return array(self.classes_)[probs.argmax(1)]

        # assert self.class_column > -1
        #
        # DO = None
        # if isinstance(X, pyisc.DataObject):
        #     assert X.class_column == self.class_column
        #     DO = X
        # elif isinstance(X, ndarray):
        #     if self.class_column == len(X[0]):
        #         DO = self._convert_to_data_object_in_scoring(X, [None]*len(X))
        #     else:
        #         X1 = X.copy()
        #         X1.T[self.class_column] = None
        #         DO = self._convert_to_data_object_in_scoring(X1, self.class_column)
        #
        # class_ids, _ = self._anomaly_detector._ClassifyData(DO, len(X), len(X))
        #
        # return array(self.classes_)[class_ids]#[probs.argmax(1)]



    def predict_log_proba(self,X):
        assert self.class_column > -1

        X1 = None
        if isinstance(X, pyisc.DataObject):
            assert X.class_column == self.class_column
            X1 = X.as_2d_array()
        elif isinstance(X, ndarray):
            X1 = X.copy()


        if X1 is not None:

            logps = self.compute_logp(X1)

            LogPs = [x-logsumexp(x) for x in array(logps).T] #normalized

            return array(LogPs)
        else:
            raise ValueError("Unknown type of data to score:", type(X))


    def predict_proba(self,X):
        Ps = exp(self.predict_log_proba(X))

        return array([p/s for p,s in zip(Ps,Ps.sum(1))])
