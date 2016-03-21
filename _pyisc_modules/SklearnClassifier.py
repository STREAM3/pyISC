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


from numpy import array, ndarray
from numpy.ma.core import exp
from scipy.misc.common import logsumexp

from sklearn.base import ClassifierMixin, BaseEstimator
from pyisc import P_Gaussian, BaseISC, cr_max
import pyisc


class SklearnClassifier(BaseISC, BaseEstimator, ClassifierMixin):
    classification_threshold = None

    def __init__(self, component_models=P_Gaussian(0),
                 classification_threshold=1e12,
                 output_combination_rule=cr_max,
                 training_anomaly_threshold = 0.0,
                 clustering = False):

        '''

        :param classification_threshold: (optional) a threshold for specifying that instances with anomaly scores below
        the threshold should be classified. If not specified, the anomaly threshold is set to very large.
        :return:
        '''
        self.classification_threshold = classification_threshold
        super(SklearnClassifier, self).__init__(component_models,output_combination_rule,training_anomaly_threshold,clustering)

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
        assert self.class_column > -1

        if self.classification_threshold > -1:
            self._anomaly_detector._SetParams(
                0,
                self.class_column,
                self.classification_threshold,
                1 if self.is_clustering else 0
            )

        if isinstance(X, pyisc._DataObject):
            classes, clusters = self._anomaly_detector._ClassifyData(X, len(X), len(X)) # TODO clusters ignored for now
            if self.classification_threshold > -1:
                self._anomaly_detector._SetParams(
                    0,
                    self.class_column,
                    self.anomaly_threshold,
                    1 if self.is_clustering else 0
                )
            return [self.classes_.index(c) if c > -1 else None for c in classes]
        elif isinstance(X, pyisc.DataObject):
            return self.predict(X._as_super_class())
        elif isinstance(X, ndarray):
            data_object = self.\
                _convert_to_data_object_in_scoring(
                X,
                y=(array([-1]*len(X)) if self.class_column == X.ndim else self.class_column) # An unknown class
            )
            if data_object is not None:
                return self.predict(data_object)
        elif isinstance(X, list):
            return self.predict(array(X))

        raise ValueError("Unknown type of data to score:", type(X) )


    def predict_log_proba(self,X):
        if isinstance(X, ndarray):
            logps = []
            for clazz in self.classes_:
                data_object = self.\
                    _convert_to_data_object_in_scoring(
                    X,
                    y=array([clazz]*len(X))
                )

                logps += [self._anomaly_detector._LogProbabilityOfData(data_object._as_super_class(), len(X))]

            LogPs = [x-logsumexp(x) for x in array(logps).T]

            return array(LogPs)

    def predict_proba(self,X):
        Ps = exp(self.predict_log_proba(X))

        return array([p/s for p,s in zip(Ps,Ps.sum(1))])
