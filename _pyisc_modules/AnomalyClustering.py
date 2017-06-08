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
# ------------------------------------------------------------------------

from pyisc import AnomalyDetector, SklearnClassifier
from sklearn import utils
import numpy as np


class AnomalyClustering(AnomalyDetector):
    max_num_of_iterations = 1000

    def __init__(self, n_clusters=2, n_repeat=10, *anomaly_detector_params0, **anomaly_detector_params1):
        self.n_clusters = n_clusters
        self.n_repeat = n_repeat
        self.ad_parms0 = anomaly_detector_params0
        self.ad_parms1 = anomaly_detector_params1
        self.clf_ = None
        AnomalyDetector.__init__(self,*anomaly_detector_params0, **anomaly_detector_params1)

    def _create_detector(self, *ad_parms0, **ad_parms1):
        return AnomalyDetector(*ad_parms0, **ad_parms1)

    def _detector_fit(self,  X, y):
        return AnomalyDetector.fit(self, X, y)

    def fit(self,X,verbose=False):
        ss =[]
        labels_list = []
        for i in xrange(self.n_repeat):
            od = self._create_detector(*self.ad_parms0, **self.ad_parms1)
            labels = self._train_clf(od, X, self.n_clusters,verbose=verbose)

            ss += [od.loglikelihood(X,labels)]

            labels_list += [labels]

        #print ss, labels

        self._detector_fit(X, np.array(labels_list[np.argmax(ss)]))

        self.clf_ = SklearnClassifier.clf(self)

        return self



    def _train_clf(self, ad, X, k=None, default_labels=None, verbose=False):
        '''

        :param ad: anomaly detector that shall be trained
        :param X: a DataObject
        :param k: the number of clusters
        :param default_labels: the clustering is started with the provided clusters/labels, where k is ignored.
        :return:
        '''
        cluster_labels = default_labels

        count_equal_movements = 0
        num_of_last_movements = 5  # the last 5 number of moments are stored
        last_movements = [-1 for _ in range(num_of_last_movements)]
        num_of_iterations = 0

        while True:
            if cluster_labels is None:  # Restart the clustering
                cluster_labels = np.array(utils.shuffle(np.mod(np.array(range(len(X))), k))) if k > 1 else np.array([0 for _ in range(len(X))])
                last_movements = [-1 for _ in range(num_of_last_movements)]
                num_of_iterations = 0
                if verbose:
                    print "Initialized clusters",np.unique(cluster_labels)

            ad.fit(X, cluster_labels)
            if ad.classes_ == []:
                ad.fit(X, np.zeros((len(X)),))

            clf = SklearnClassifier.clf(ad)
            cluster_labels_new = clf.predict(X)

            movements = sum((cluster_labels_new != cluster_labels) * 1.0)

            if movements in last_movements:
                count_equal_movements += 1
            else:
                count_equal_movements = 0
                last_movements = last_movements[1:] + [movements]

            if count_equal_movements >= 20 or num_of_iterations > self.max_num_of_iterations:  # Restart the clustering if the number of movements in last_movements are greater or more equal than 20
                cluster_labels = None  # Restart clustering
                continue

            if verbose:
                print "movements", movements

            if movements == 0:
                break

            cluster_labels = cluster_labels_new

            num_of_iterations += 1

        return cluster_labels

    def anomaly_score(self, X,y=None):
        return AnomalyDetector.anomaly_score(self, X, self.clf_.predict(X) if self.clf_ is not None and y is None else y)

    def loglikelihood(self,X,y=None):
        return AnomalyDetector.loglikelihood(self, X, self.clf_.predict(X) if self.clf_ is not None and y is None else y)
