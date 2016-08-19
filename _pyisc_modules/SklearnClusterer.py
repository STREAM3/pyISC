
from pyisc import SklearnClassifier
from numpy import  array, mod, unique, sqrt, inf
from sklearn.utils import shuffle

class SklearnClusterer:
    def __init__(self,anomaly_detector):
        self.ad = anomaly_detector
        self.scores = None
        self.clustering_ = None

    def make_scores(self,X, max_k):
        '''
        Returns an array of the individual anomaly scores for each example for number of each clusters.
        :param X: array of arrays
        :param max_k: maximum number of clusters
        :return: array of array of anomaly scores for each k from 1 to max_k (inclusive)
        '''
        ad = self.ad
        ad.fit(X)
        score = ad.anomaly_score(X)
        scores = [list(score)]

        print "Clusters", 1, "Score", score[score < inf].max(), sum(score == inf)

        for k in range(2,max_k):
            cluster_labels_new = self._train_clf(X, k)

            score = ad.anomaly_score(X,cluster_labels_new)
            scores += [list(score)]
            print "Clusters", k, "Score",  score[score < inf].max(), sum(score == inf)

        self.scores = array(scores)

        return self.scores

    def _train_clf(self, X, k):
        ad = self.ad
        cluster_labels = array(shuffle(mod(array(range(len(X))), k)))
        print unique(cluster_labels)
        while True:
            ad.fit(X, cluster_labels)
            clf = SklearnClassifier.clf(ad)
            cluster_labels_new = clf.predict(X)

            movements = sum((cluster_labels_new != cluster_labels) * 1.0)

            print "movements", movements

            if movements == 0:
                break

            cluster_labels = cluster_labels_new
        return cluster_labels

    def fit_anomaly_detector(self,X, max_k=2, make_scores=True):
        '''
        The method uses a variation of the elbow curve to select the number of clusters based on the maximum individual
        anomaly score for each cluster computed by the make_scores method.
        The method is proposed at http://stackoverflow.com/questions/2018178/finding-the-best-trade-off-point-on-a-curve
        :param X: data set to fit
        :param make_scores: indicating if the make_scores method has already been called, otherwise it is called with max_k > 1.
        :return: the anomaly detector provided in the constructor fitted to the data with the best number of clusters tested
        '''
        if make_scores:
            self.make_scores(X, max_k)

        y = self.scores.max(1)
        x = array(range(1,len(y)+1))*10

        b = array([x[-1]-x[0], y[-1] - y[0]])
        b_len= sqrt(b.dot(b))

        max_dist_sqr = -1
        best_k = -1
        for k in range(1, len(y)+1):
            p = array([x[k-1]-x[0], y[k - 1] - y[0]])

            dist_sqr = p.dot(p)-(b.dot(p)/b_len)**2
            if dist_sqr > max_dist_sqr:
                max_dist_sqr = dist_sqr
                best_k = k

        self.clustering_ =self._train_clf(X,best_k)

        print "best k", best_k


        return self.ad
