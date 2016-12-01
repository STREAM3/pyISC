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

from pyisc import SklearnClassifier, AnomalyDetector, DataObject
from numpy import  array, mod, unique, sqrt, inf, mean,std, c_, argmin, percentile
from sklearn.utils import shuffle

class SklearnClusterer:
    '''
    Sets the maximum number of iterations that is used when doing clustering for each number of clusters.
    '''
    max_num_of_iterations = 1000

    '''
    TODO fix bug when calling fit.. with init_clusters
    '''
    def __init__(self,*anomaly_detector_params0, **anomaly_detector_params1):
        self.ad_parms0 = anomaly_detector_params0
        self.ad_parms1 = anomaly_detector_params1

        '''The scores computed by the last call to method make_score'''
        self.scores = None
        '''The cluster selected for each data point'''
        self.clustering_ = None
        '''Contains the value for each cluster used by the elbow method for selecting best cluster'''
        self.cluster_curve_ = None


    def make_scores(self,X, max_k, start_k=2,verbose=False):
        '''
        Returns an array of the individual anomaly scores for each example for number of each clusters.
        :param X: array of arrays or DataObject
        :param max_k: maximum number of clusters
        :param start_k: start clustering  start_k to max_k (inclusive) number of clusters.
        :return: array of array of anomaly scores for each k from 1 to max_k (inclusive)
        '''
        ad = AnomalyDetector(*self.ad_parms0, **self.ad_parms1)
        ad.fit(X)
        score = ad.anomaly_score(X)
        scores = [list(score)]

        if verbose:
            print "Clusters", 1, "Score", score[score < inf].std(), sum(score == inf)

        min_percentile = percentile(score,20)
        max_percentile = percentile(score,80)

        for k in range(start_k,max_k+1):
            clusters = self._train_clf(ad, X, k,verbose=verbose, marked_as_single_cluster=[s >= min_percentile and s <= max_percentile for s in score])

            score = ad.anomaly_score(X, clusters)
            scores += [list(score)]
            if verbose:
                print "Clusters", k, "Score",  score[score < inf].std(), sum(score == inf)

        self.scores = array(scores)

        return self.scores

    def _train_clf(self, ad, X, k=None, default_labels=None,verbose=False, marked_as_single_cluster=[]):
        '''

        :param ad: anomaly detector that shall be trained
        :param X: a DataObject
        :param k: the number of clusters
        :param default_labels: the clustering is started with the provided clusters/labels, where k is ignored.
        :param marked_as_single_cluster: list of booleans marking if data points should be given the same cluster at initialization
        :return:
        '''
        cluster_labels = default_labels

        count_equal_movements = 0
        num_of_last_movements = 5 # the last 5 number of moments are stored stored
        last_movements = [-1 for _ in range(num_of_last_movements)]
        num_of_iterations = 0

        while True:
            if cluster_labels is None: # Restart the clustering
                cluster_labels = array(shuffle(mod(array(range(len(X))), k)))
                if len(marked_as_single_cluster) > 0:
                    cluster_labels[array(marked_as_single_cluster)] = -1

                last_movements = [-1 for _ in range(num_of_last_movements)]
                num_of_iterations = 0
                if verbose:
                    print unique(cluster_labels)

            ad.fit(X, cluster_labels)
            clf = SklearnClassifier.clf(ad)
            cluster_labels_new = clf.predict(X)

            movements = sum((cluster_labels_new != cluster_labels) * 1.0)

            if movements in last_movements:
                count_equal_movements += 1
            else:
                count_equal_movements = 0
                last_movements = last_movements[1:]+[movements]

            if count_equal_movements >= 20 or num_of_iterations > self.max_num_of_iterations: # Restart the clustering if the number of movements in last_movements are greater or more equal than 20
                cluster_labels = None # Restart clustering
                continue

            if verbose:
                print "movements", movements

            if movements == 0:
                break

            cluster_labels = cluster_labels_new

            num_of_iterations += 1

        return cluster_labels

    def fit_anomaly_detector(self, X, max_k=2, n_repeat=10, scores=None, use_k=None, init_clusters=None, verbose=False, scoring_method=mean):
        '''
        The method uses a variation of the elbow curve to select the number of clusters based on the maximum individual
        anomaly score for each cluster computed by the make_scores method.
        The method is proposed at http://stackoverflow.com/questions/2018178/finding-the-best-trade-off-point-on-a-curve
        :param X: data set to fit, 2 dim numpy array or a DataObject with a class column
        :param n_repeat: repeat clustering n number of times using the mean as elbow curve
        :param scores: an array of arrays with anomaly scores, to use for fitting instead of calling make_scores. Each array corresponds contains 1 or more calls to make_scores for a k number of clusters. For each index i in range(len(scores)) means k=i+1.
        :param use_k: if set, no autmatic selection is made, instead the value of use_k is used as number of clusters
        :param init_clusters: the clustering is initialized with the provided clusters. scores, use_k and n_repeat are ignored.
        :param verbose: print progress info
        :param scoring_method: the method to compute the aggregated evaluation score from teh anomaly scores of the data clustering, e.g. numpy mean or std.
        :return: the anomaly detector with parameters provided in the constructor fitted to the data with the best number of clusters tested
        '''

        best_k = None
        if init_clusters is None:
            if use_k is None:
                ss = []
                if scores is None:
                    for n in xrange(n_repeat):
                        self.make_scores(X, max_k,verbose=verbose)
                        ss.append(map(lambda s: scoring_method(s[s<inf]), self.scores))
                else:
                    ss = [map(lambda s: scoring_method(s[s<inf]), scores[i]) for i in range(len(scores))]

                best_k, y = self.compute_best_elbow_k(ss)
            else:
                best_k = use_k

        ad_list = []
        scores = []
        for i in range(n_repeat):
            ad = AnomalyDetector(*self.ad_parms0, **self.ad_parms1)
            self.clustering_ = self._train_clf(ad, X, best_k,init_clusters,verbose=verbose)
            ad_scores = ad.anomaly_score(X, self.clustering_)
            scores.append(ad_scores[ad_scores < inf].std())
            ad_list.append(ad)
            if init_clusters is not None:
                break

        best_ad = ad_list[argmin(scores)]

        if verbose:
            print "best k", best_k

        if use_k or init_clusters is not None or y is not None:
            self.cluster_curve_ = None
        else:
            self.cluster_curve_ = y

        return ad

    def compute_best_elbow_k(self, ss):
        y = mean(ss, 0)
        x = array(range(1, len(y) + 1)) * 10
        b = array([x[-1] - x[0], y[-1] - y[0]])
        b_len = sqrt(b.dot(b))
        max_dist_sqr = -1
        best_k = -1
        for k in range(1, len(y) + 1):
            p = array([x[k - 1] - x[0], y[k - 1] - y[0]])

            dist_sqr = p.dot(p) - (b.dot(p) / b_len) ** 2
            if dist_sqr > max_dist_sqr:
                max_dist_sqr = dist_sqr
                best_k = k
        return best_k, y

