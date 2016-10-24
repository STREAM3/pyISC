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
from numpy import ndarray, array
from pyisc import _to_cpp_array_int, _AnomalyDetector, \
    _IscMultiGaussianMicroModel, \
    _IscPoissonMicroModel, \
    _IscPoissonMicroModelOneside, \
    _IscMicroModelVector, _IscGammaMicroModel, \
    _IscMarkovGaussMicroModel, \
    _IscMarkovGaussMicroModelVector, \
    _IscMarkovGaussCombinerMicroModel, \
    _IscMarkovGaussMatrixMicroModel
import pyisc

__author__ = 'tol'

cr_max = pyisc.IscMax
cr_plus= pyisc.IscPlus

class P_ProbabilityModel:
    _saved_model = None
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
        column_array = _to_cpp_array_int(self.column_index)
        self._saved_model = _IscMultiGaussianMicroModel(len(self.column_index), column_array)
        pyisc._free_array_int(column_array)
        return self._saved_model


class P_Poisson(P_ProbabilityModel):

    def __init__(self, frequency_column, period_column):
        '''
        A Poisson distribution using frequency_column as column index into the data object for the frequency and
        period_column into the data object for the period where frequency was counted.
        This probability model checks for both unusual high frequency values and unusual small values.
        :param frequency_column:
        :param period_column:
        '''
        self.column_index = [frequency_column,period_column]


    def create_micromodel(self):
        self._saved_model = _IscPoissonMicroModel(self.column_index[0], self.column_index[1])
        return self._saved_model


class P_PoissonOnesided(P_ProbabilityModel):

    def __init__(self, frequency_column, period_column):
        '''
        A Poisson distribution using frequency_column as column index into the data object for the frequency and
        period_column into the data object for the period where frequency was counted.
        This probability model only checks for unusual high frequency values, but not unusual small values.
        :param frequency_column:
        :param period_column:
        :return:
        '''
        self.column_index = [frequency_column,period_column]


    def create_micromodel(self):
        self._saved_model = _IscPoissonMicroModelOneside(self.column_index[0], self.column_index[1])
        return self._saved_model


class P_Gamma(P_ProbabilityModel):

    def __init__(self, frequency_column, period_column):
        '''
        An approximation of the Gamma distribution by the use of Poisson distribution that uses the frequency_column as column index into the data object for the frequency and
        period_column into the data object for the period where frequency was counted.
        :param frequency_column:
        :param period_column:
        :return:
        '''

        self.frequency_column = frequency_column
        self.period_column = period_column

    def create_micromodel(self):
        self._saved_model =  _IscGammaMicroModel(self.frequency_column,self.period_column)
        return self._saved_model

class P_ConditionalGaussian(P_ProbabilityModel):

    def __init__(self, prediction_column, conditional_column):
        '''
        Implements a conditional multivariate Gaussian distribution.

        :param prediction_column: an integer or an list of integers
        :param condition_column: an integer or an list of integers
        '''

        self.prediction_column = prediction_column
        self.conditional_column = conditional_column


    def create_micromodel(self):
        pred_index = _to_cpp_array_int(self.prediction_column)
        cond_index= _to_cpp_array_int(self.conditional_column)
        self._saved_model = _IscMarkovGaussMicroModel(pred_index, len(self.prediction_column),
                                         cond_index, len(self.conditional_column))

        pyisc._free_array_int(pred_index)
        pyisc._free_array_int(cond_index)

        return self._saved_model

class P_ConditionalGaussianCombiner(P_ProbabilityModel):

    def __init__(self, gaussian_components):
        '''
        Combines the contributions from conditionally independent multivariate conditional Gaussian distributions, so that
        a Bayesian belief net or Markov chain can be created. The components must form a directed acyclic graph.

        :param gaussian_components: a single P_ConditionalGauss or a list of P_ConditionalGauss.
        '''

        assert isinstance(gaussian_components, P_ConditionalGaussian) or \
               isinstance(gaussian_components,list) and \
               all([isinstance(comp, P_ConditionalGaussian) for comp in gaussian_components])

        self.gaussian_components = gaussian_components

    def create_micromodel(self):
        num_of_components = len(self.gaussian_components)
        creator = _IscMarkovGaussMicroModelVector()
        for i in range(num_of_components):
            creator.push_back(self.gaussian_components[i].create_micromodel())
        ptr_creator = pyisc._to_pointer(creator)
        self._saved_model = _IscMarkovGaussCombinerMicroModel(ptr_creator, num_of_components)
        pyisc._free_pointer(ptr_creator)
        return self._saved_model

class P_ConditionalGaussianDependencyMatrix(P_ProbabilityModel):

    def __init__(self, value_columns, elements_per_row):
        '''
        Creates a dependency matrix where each element is only dependent on its right neighbour and the element directly
        below in all cases where they are present. Otherwise the elements are only dependent on the element of the two
        neighbours that is present, or no element.

        :param value_columns: the column indexes that are contained in the matrix as a sequence of the elements
        from left to the right and from the first row to the last row.
        :param elements_per_row: the number of column indexes (elements) that constitutes a row in the matrix,
        all rows are equally long.
        '''

        self.value_columns = value_columns
        self.slots_per_row = elements_per_row

    def create_micromodel(self):
        value_array = _to_cpp_array_int(self.value_columns)
        self._saved_model = _IscMarkovGaussMatrixMicroModel(value_array, len(self.value_columns), self.slots_per_row)
        pyisc._free_array_int(value_array)
        return self._saved_model

class BaseISC(object):
    component_models = None

    def __init__(self, component_models=P_Gaussian(0), output_combination_rule=cr_max, anomaly_threshold = 0.0):
        '''
        The base class for all pyISC classes for statistical inference

        :param component_models: a statistical model reused for all mixture components, or an list of statistical models.
        Available statistical models are: P_Gaussian, P_Poisson, P_PoissonOneside.
        :param output_combination_rule: an input defining which type of rule to use for combining the anomaly score
        output from each model in component_model. Available combination rules are: cr_max and cr_plus.
        :param anomaly_threshold: the threshold at which a row in the input is considered a anomaly during training,
        might differ from what is used for anomaly decision.
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
        self.is_clustering = False #clustering not used in the python wrapper since it does not seem to work in the C++ code.
        self.output_combination_rule = output_combination_rule

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
        cl = 1 if self.is_clustering else 0

        if isinstance(component_models, P_ProbabilityModel):
            n = 1
            component_models = [component_models]
        else:
            n = len(component_models)

        self.component_models = component_models

        # Map argument to C++ argument
        comp_distributions = _IscMicroModelVector()

        for i in range(n):
            comp_distributions.push_back(self.component_models[i].create_micromodel())

        self.classes_ = None
        self.num_of_partitions = n
        self._anomaly_detector = _AnomalyDetector(off, splt, th, cl, output_combination_rule, comp_distributions);


    def fit(self, X, y=None):
        '''
        Train the anomaly detector using a DataObject or an array of arrays

        :param X: a single array, an array of arrays, or an instance of pyisc DataObject
        :param y: must be an array,list, a column index (integer) or None
        :return:
        '''

        if isinstance(X, pyisc.DataObject) and y is None:
            assert y is None # Contained in the data object
            self.class_column = X.class_column
            if self.class_column >= 0:
                self.classes_ = X.classes_

            self._anomaly_detector._SetParams(
                0,
                -1 if X.class_column is None else X.class_column,
                self.anomaly_threshold,
                1 if self.is_clustering else 0
            )
            self._anomaly_detector._TrainData(X)
            return self
        if isinstance(X, ndarray):
            class_column = -1
            data_object = None
            assert X.ndim <= 2
            if X.ndim == 2:
                max_class_column = X.shape[1]
            else:
                max_class_column = 1
            if isinstance(y, list) or isinstance(y, ndarray):
                assert len(X) == len(y)
                class_column = max_class_column
                data_object = pyisc.DataObject(numpy.c_[X, y], class_column=class_column)
            elif y is None or int(y) == y and y > -1 and y <= max_class_column:
                self.class_column = y
                data_object = pyisc.DataObject(X,class_column=y)

            if data_object is not None:
                return self.fit(data_object)

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

        if isinstance(X, pyisc.DataObject) and y is None and X.class_column == self.class_column:
            self._anomaly_detector._TrainDataIncrementally(X)
            return self
        elif isinstance(X, ndarray) or isinstance(X, list):
            data_object = self._convert_to_data_object_in_scoring(array(X), y)

            if data_object is not None:
                return self.fit_incrementally(data_object)

        raise ValueError("Unknown type of data to fit X, y", type(X), type(y))

    def unfit_incrementally(self, X, y=None):
        if isinstance(X, pyisc.DataObject) and y is None and X.class_column == self.class_column:
            self._anomaly_detector._UntrainDataIncrementally(X)
            return self
        elif isinstance(X, ndarray) or isinstance(X, list):
            data_object = self._convert_to_data_object_in_scoring(array(X), y)

            if data_object is not None:
                return self.unfit_incrementally(data_object)

        raise ValueError("Unknown type of data to fit X, y", type(X), type(y))

    def _convert_to_data_object_in_scoring(self, X, y):
        data_object = None
        if isinstance(y, list) or isinstance(y, ndarray):
            assert X.ndim == 2 and self.class_column == X.shape[1] or X.ndim == 1 and self.class_column == 1
            data_object = pyisc.DataObject(numpy.c_[X, y], class_column=self.class_column,classes=self.classes_)
        else:
            assert self.class_column == y
            data_object = pyisc.DataObject(X, class_column=self.class_column,classes=self.classes_ if y is not None else None)
        return data_object

    def reset(self):
        self._anomaly_detector._Reset();


    def compute_logp(self, X1):
        if self.class_column is not None and not isinstance(X1, pyisc._DataObject):
            if X1.ndim == 2 and self.class_column >= 0 and self.class_column < X1.shape[1]:
                data_object = self. \
                    _convert_to_data_object_in_scoring(
                    X1,
                    y=self.class_column
                )
            else:
                data_object = self. \
                    _convert_to_data_object_in_scoring(
                    X1,
                    y=array([None] * len(X1))
                )
            logps = []
            for clazz in self.classes_:
                pyisc._DataObject.set_column_values(data_object, self.class_column, [clazz] * len(data_object))

                logps += [self._anomaly_detector._LogProbabilityOfData(data_object, len(X1))]

            return logps
        else:
            data_object = pyisc.DataObject(X1) if not isinstance(X1, pyisc._DataObject) else X1
            return self._anomaly_detector._LogProbabilityOfData(data_object, len(X1))
