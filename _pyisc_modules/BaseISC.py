"""
The Python Wrapper of all ISC anomaly detector training methods.
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
from _pyisc import _to_cpp_array
from abc import abstractmethod
import numpy
from numpy import ndarray
from pyisc import _to_cpp_array_int, _AnomalyDetector, \
    _IscMultiGaussianMicroModel, \
    _IscPoissonMicroModel, \
    _IscPoissonMicroModelOneside, \
    _IscMicroModelCreator
import pyisc

__author__ = 'tol'

cr_max = pyisc.IscMax
cr_plus= pyisc.IscPlus

class P_ProbabilityModel:
    column_index=None
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def create_micromodel(self):
        pass

class P_Gaussian(P_ProbabilityModel):

    def __init__(self, value_column):
        '''
        A Multivaritae Gaussian distribution using value_columns as column index into the data object
        :param value_index: an integer (single variable) or an array of integers (multivariate)
        :return:
        '''
        if isinstance(value_column, list):
            self.column_index = value_column
        else:
            self.column_index = [value_column]

    def create_micromodel(self):
        return _IscMultiGaussianMicroModel(len(self.column_index), _to_cpp_array_int(self.column_index))

class P_Poisson(P_ProbabilityModel):

    def __init__(self, frequency_column, period_column):
        '''
        A Poisson distribution using frequency_column as column index into the data object for the frequency and period_column into the data object for the period where frequency was counted.
        This probability model checks for both unusual high frequency values and unusual small values.
        :param frequency_column:
        :param period_column:
        '''
        self.column_index = [frequency_column,period_column]


    def create_micromodel(self):
        return _IscPoissonMicroModel(self.column_index[0], self.column_index[1])


class P_PoissonOnesided(P_ProbabilityModel):

    def __init__(self, frequency_column, period_column):
        '''
        A Poisson distribution using frequency_column as column index into the data object for the frequency and period_column into the data object for the period where frequency was counted.
        This probability model only checks for unusual high frequency values, but not unusual small values.
        :param frequency_column:
        :param period_column:
        :return:
        '''
        self.column_index = [frequency_column,period_column]


    def create_micromodel(self):
        return _IscPoissonMicroModelOneside(self.column_index[0], self.column_index[1])


class BaseISC:

    def __init__(self, component_models=P_Gaussian(0), output_combination_rule=cr_max, anomaly_threshold = 0.0, clustering = False):
        '''
        The base class for all pyISC classes for statistical inference

        :param component_models: a statistical model reused for all mixture components, or an list of statistical models. Available statistical models are: PGaussian, PPoisson, PPoissonOneside.
        :param output_combination_rule: an input defining which type of rule to use for combining the anomaly score output from each model in component_model. Available combination rules are: cr_max and cr_plus.
        :param anomaly_threshold: the threshold at which a row in the input is considered a anomaly during training, might differ from what is used for anomaly decision.

        :param clustering: boolean indicating whether to cluster the data.
        :return:
        '''

        feature_column_start=0


        assert isinstance(anomaly_threshold, float) and anomaly_threshold >= 0
        assert isinstance(feature_column_start, int) and feature_column_start >= 0
        assert isinstance(component_models, P_ProbabilityModel) or \
               isinstance(component_models, list) and len(component_models) > 0 and \
               all([isinstance(m, P_ProbabilityModel) for m in component_models])
        assert output_combination_rule in [cr_max, cr_plus]



        self.anomaly_threshold = anomaly_threshold
        self.is_clustering = clustering

        #//AnomalyDetector(int n, int off, int splt, double th, int cl); // Sublasses must know the numbers and types of micromodels

        #/**
        #* n is number of isc mixture components
        # * off is the first column containing features used by the detector
        # * splt is a the column containing a known class
        # * th is a threshold on when to consider a vector of data as anomalous
        # * cl is a variable if zero indicate no clustering else indicates that clustering should be done
        # * cr is variable indicating how the anomaly scores for the different isc mixture components should be combined
        # * cf is a function that creates a isc micro component for each of the n isc mixture component.

        off = feature_column_start

        # no split class
        self.class_column = None
        splt = -1

        th = anomaly_threshold
        cl = 1 if clustering else 0

        if isinstance(component_models, P_ProbabilityModel):
            n = 1
            component_models = [component_models]
        else:
            n = len(component_models)


        # Map argument to C++ argument
        comp_distributions = _IscMicroModelCreator(n)

        for i in range(n):
            comp_distributions.add(i,component_models[i].create_micromodel())

        self.num_of_partitions = n
        self._anomaly_detector = _AnomalyDetector(off, splt, th, cl, output_combination_rule, comp_distributions);

    def fit(self, X, y=None):
        '''
        Train the anomaly detector using a DataObject or an array of arrays

        :param X: a single array, an array of arrays, or an instance of pyisc DataObject
        :param y: must be an array,list, a column index (integer) or None
        :return:
        '''

        if isinstance(X, pyisc._DataObject):
            assert not isinstance(y, list) and not isinstance(y, ndarray)
            self.class_column = y
            self._anomaly_detector._SetParams(0,-1 if self.class_column is None else self.class_column ,self.anomaly_threshold,1 if self.is_clustering else 0)
            self._anomaly_detector._TrainData(X)
            return self
        elif isinstance(X, pyisc.DataObject):
            assert y is None or X.class_column == y
            return self.fit(X._as_super_class(),X.class_column)

        if isinstance(X, ndarray):
            class_column = -1
            data_object = None
            if isinstance(y, list) or isinstance(y, ndarray):
                assert len(X) == len(y)
                class_column=X.ndim
                data_object = pyisc.DataObject(numpy.c_[X, y], class_column=class_column)
            elif y is None or int(y) == y and y > -1:
                class_column = y
                data_object = pyisc.DataObject(X,class_column=y)

            if class_column > -1:
                self.classes_ = data_object.classes_

            if data_object is not None:
                return self.fit(data_object, y=class_column)

        raise ValueError("Unknown type of data to fit X, y:", type(X), type(y))

    def fit_incrementally(self, X, y=None):
        '''
        Incrementally train the anomaly detector. Call reset() to restart learning. Requires being trained using the fit
        method before first call.

        :param format: a Format describing the types of the data per single array
        :param X: a single array, an array of arrays, or an instance of pyisc DataObject
        :param y: a single array with classes or None, optional, only required if previously trained with classes
        :return: self
        '''


        if y is not self.class_column:
            raise ValueError('y is not equal to the class_column:', y, ' is not ', self.class_column)

        if isinstance(X, pyisc._DataObject):
            self._anomaly_detector._TrainDataIncrementally(X)
            return self
        elif isinstance(X, pyisc.DataObject):
            return self.fit_incrementally(X._as_super_class(),y)
        elif isinstance(X, ndarray):
            data_object = self._convert_to_data_object_in_scoring(X, y)

            if data_object is not None:
                return self.fit_incrementally(data_object,self.class_column)

        raise ValueError("Unknown type of data to fit X, y", type(X), type(y))

    def _convert_to_data_object_in_scoring(self, X, y):
        data_object = None
        if isinstance(y, list) or isinstance(y, ndarray):
            assert self.class_column == X.ndim
            data_object = pyisc.DataObject(numpy.c_[X, y], class_column=self.class_column,classes=self.classes_)
        else:
            assert self.class_column == y
            data_object = pyisc.DataObject(X, class_column=self.class_column,classes=self.classes_ if y is not None else None)
        return data_object

    def reset(self):
        self._anomaly_detector._Reset();
