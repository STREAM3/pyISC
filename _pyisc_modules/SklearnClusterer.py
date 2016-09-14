from pyisc import SklearnClassifier, AnomalyDetector, DataObject
from numpy import  array, mod, unique, sqrt, inf, mean,std, c_
from sklearn.utils import shuffle

class SklearnClusterer:
    '''
    TODO fix bug when calling fit.. with init_clusters
    '''
    def __init__(self,*anomaly_detector_params):
        self.ad_parms = anomaly_detector_params
        '''The scores computed by the last call to method make_score'''
        self.scores = None
        '''The cluster selected for each data point'''
        self.clustering_ = None
        '''Contains the value for each cluster used by the elbow method for selecting best cluster'''
        self.cluster_curve_ = None

    def make_scores(self,X, max_k, start_k=2):
        '''
        Returns an array of the individual anomaly scores for each example for number of each clusters.
        :param X: array of arrays or DataObject
        :param max_k: maximum number of clusters
        :param start_k: start clustering  start_k to max_k (inclusive) number of clusters.
        :return: array of array of anomaly scores for each k from 1 to max_k (inclusive)
        '''
        ad = AnomalyDetector(*self.ad_parms)


        ad.fit(X)
        score = ad.anomaly_score(X)
        scores = [list(score)]
        print "Clusters", 1, "Score", score[score < inf].std(), sum(score == inf)

        for k in range(start_k,max_k+1):
            clusters = self._train_clf(ad, X, k)

            score = ad.anomaly_score(X, clusters)
            scores += [list(score)]
            print "Clusters", k, "Score",  score[score < inf].std(), sum(score == inf)

        self.scores = array(scores)

        return self.scores

    def _train_clf(self, ad, X, k=None, default_labels=None):
        '''

        :param ad: anomaly detector that shall be trained
        :param X: a DataObject
        :param k: the number of clusters
        :param default_labels: the clustering is started with the provided clusters/labels, where k is ignored.
        :return:
        '''
        cluster_labels = default_labels

        count_equal_movements = 0
        old_movements = -1

        while True:
            if cluster_labels is None: # Restart the clustering
                cluster_labels = array(shuffle(mod(array(range(len(X))), k)))
                print unique(cluster_labels)

            ad.fit(X, cluster_labels)
            clf = SklearnClassifier.clf(ad)
            cluster_labels_new = clf.predict(X)

            movements = sum((cluster_labels_new != cluster_labels) * 1.0)

            if old_movements == movements:
                count_equal_movements += 1
            else:
                count_equal_movements = 0

            if count_equal_movements >= 10: # Restart the clustering if the number of equal movements are greater or more equal than 10
                cluster_labels = None
                continue

            print "movements", movements

            if movements == 0:
                break

            cluster_labels = cluster_labels_new
            old_movements = movements

        return cluster_labels

    def fit_anomaly_detector(self, X, max_k=2, n_repeat=10, scores=None, use_k=None, init_clusters=None):
        '''
        The method uses a variation of the elbow curve to select the number of clusters based on the maximum individual
        anomaly score for each cluster computed by the make_scores method.
        The method is proposed at http://stackoverflow.com/questions/2018178/finding-the-best-trade-off-point-on-a-curve
        :param X: data set to fit, 2 dim numpy array or a DataObject with a class column
        :param n_repeat: repeat clustering n number of times using the mean as elbow curve
        :param scores: an array of arrays with anomaly scores, to use for fitting instead of calling make_scores. Each array corresponds contains 1 or more calls to make_scores for a k number of clusters. For each index i in range(len(scores)) means k=i+1.
        :param use_k: if set, no autmatic selection is made, instead the value of use_k is used as number of clusters
        :param init_clusters: the clustering is initialized with the provided clusters. scores, use_k and n_repeat are ignored.
        :return: the anomaly detector with parameters provided in the constructor fitted to the data with the best number of clusters tested
        '''

        best_k = None
        if init_clusters is None:
            if use_k is None:
                ss = []
                if scores is None:
                    for n in xrange(n_repeat):
                        self.make_scores(X, max_k)
                        ss.append(map(lambda s: std(s[s<inf]), self.scores))
                else:
                    ss = [map(lambda s: std(s[s<inf]), scores[i]) for i in range(len(scores))]

                best_k, y = self.compute_best_elbow_k(ss)
            else:
                best_k = use_k

        ad = AnomalyDetector(*self.ad_parms)

        self.clustering_ = self._train_clf(ad, X, best_k,init_clusters)

        print "best k", best_k

        if use_k:
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

