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

from pyisc import SklearnOutlierDetector
from AnomalyClustering import AnomalyClustering

class OutlierClustering(AnomalyClustering,SklearnOutlierDetector):
    max_num_of_iterations = 1000

    def __init__(self, n_clusters=2, n_repeat=10, *anomaly_detector_params0, **anomaly_detector_params1):
        self.n_clusters = n_clusters
        self.n_repeat = n_repeat
        self.ad_parms0 = anomaly_detector_params0
        self.ad_parms1 = anomaly_detector_params1
        self.clf_ = None
        SklearnOutlierDetector.__init__(self,*anomaly_detector_params0, **anomaly_detector_params1)

    def _create_detector(self, *ad_parms0, **ad_parms1):
        return SklearnOutlierDetector(*ad_parms0, **ad_parms1)

    def _detector_fit(self,  X, y):
        return SklearnOutlierDetector.fit(self, X, y)

    def fit(self,X,verbose=False):
        return AnomalyClustering.fit(self,X,verbose=verbose)

    def predict(self, X):
        return SklearnOutlierDetector.predict(self, X, self.clf_.predict(X))

    def anomaly_score(self, X, y=None):
        return SklearnOutlierDetector.anomaly_score(self, X, self.clf_.predict(X) if self.clf_ is not None and y is None else y)

    def loglikelihood(self,X,y=None):
        return AnomalyClustering.loglikelihood(self, X, self.clf_.predict(X) if self.clf_ is not None and y is None else y)
