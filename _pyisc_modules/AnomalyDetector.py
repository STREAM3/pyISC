"""
The Python Wrapper of all ISC anomaly scoring methods.
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

from numpy import ndarray, array, log, inf

from pyisc import BaseISC

import pyisc


class AnomalyDetector(BaseISC):

    def anomaly_score(self,X, y=None):
        '''
        Score each row in X,y with an anomaly score.
        :param X: a single array, an array of arrays, or an instance of pyisc DataObject
        :param y: must be an array,list or None, cannot be a column_index as when fitting the data
        :return:
        '''

        if isinstance(X, pyisc.DataObject):
            return self._anomaly_detector._CalcAnomaly(X,X.size())
        elif isinstance(X, ndarray) or isinstance(X, list):
            data_object = self._convert_to_data_object_in_scoring(array(X), y)

            if data_object is not None:
                return self.anomaly_score(data_object)

        raise ValueError("Unknown type of data to score X, y", type(X), type(y))


    def anomaly_score_details(self,X,y=None,index=None):
        '''
        Computes the detailed anomaly scores of each element in X, that is, anomaly score for each used statistical component\n
        :param X: is a DataObject or numpy array or list\n
        :param y: is None or an array of classes, must be consistent with how the data was fitted, cannot be a column_index
        :param index: is None or an index into X\n\n
        :return: a list with (a list for each element in X if X is two dimensional, otherwise only a single list):\n
                [\n
                a double value with total deviation, \n
                an int value with predicted class (if class_column was set to true in constructor),\n
                an int value with predicted cluster (if clustering was set to true in constructor), \n
                an array with deviations for each individual component,\n
                an array with the peak, that is, the most probable feature value for each feature column,\n
                an array with the least acceptable value for each feature column,\n
                an array with the largest acceptable value for each feature column\n
                ]
        '''
        if isinstance(X, pyisc._DataObject) and y is None:
            if isinstance(index,int):
                return self._anomaly_score_intfloat(X._get_intfloat(index),X.length(), X)
            else:
                return [self.anomaly_score_details(X,index=i) for i in range(X.size())]
        elif isinstance(X, ndarray):
            data_object = self._convert_to_data_object_in_scoring(X, y)
            if data_object is not None:
                return self.anomaly_score_details(data_object,index)

        elif isinstance(X, list):
            return self.anomaly_score(array(X),y,index)

        raise ValueError("Unknown type of data to score?", type(X) ) if not isinstance(X, pyisc._DataObject) and not isinstance(X, list) and not isinstance(X, ndarray) else ""



    def _anomaly_score_intfloat(self, x_intfloat, length, data_object):
        deviations = pyisc._double_array(self.num_of_partitions)
        min = pyisc._intfloat_array(length)
        max = pyisc._intfloat_array(length)
        peak = pyisc._intfloat_array(length)
        anom = pyisc._double_array(1)
        cla = pyisc._int_array(1)
        clu = pyisc._int_array(1)

        self._anomaly_detector._CalcAnomalyDetails(x_intfloat,anom, cla, clu, deviations, peak, min, max)

        if self.is_clustering and self.class_column > -1:
            result = [pyisc._get_double_value(anom,0),
                    pyisc._get_int_value(cla,0),
                    pyisc._get_int_value(clu,0),
                    list(pyisc._to_numpy_array(deviations,self.num_of_partitions)),
                    list(data_object._convert_to_numpyarray(peak, length)),
                    list(data_object._convert_to_numpyarray(min, length)),
                    list(data_object._convert_to_numpyarray(max, length))]
        elif self.is_clustering:
            result = [pyisc._get_double_value(anom,0),
                    pyisc._get_int_value(clu,0),
                    list(pyisc._to_numpy_array(deviations,self.num_of_partitions)),
                    list(data_object._convert_to_numpyarray(peak, length)),
                    list(data_object._convert_to_numpyarray(min, length)),
                    list(data_object._convert_to_numpyarray(max, length))]
        elif self.class_column > -1:
            result = [pyisc._get_double_value(anom,0),
                    pyisc._get_int_value(cla,0),
                    list(pyisc._to_numpy_array(deviations,self.num_of_partitions)),
                    list(data_object._convert_to_numpyarray(peak, length)),
                    list(data_object._convert_to_numpyarray(min, length)),
                    list(data_object._convert_to_numpyarray(max, length))]
        else:
            result = [pyisc._get_double_value(anom,0),
                    list(pyisc._to_numpy_array(deviations,self.num_of_partitions)),
                    list(data_object._convert_to_numpyarray(peak, length)),
                    list(data_object._convert_to_numpyarray(min, length)),
                    list(data_object._convert_to_numpyarray(max, length))]

        pyisc._free_array_double(deviations);
        pyisc._free_array_intfloat(min)
        pyisc._free_array_intfloat(max)
        pyisc._free_array_intfloat(peak)
        pyisc._free_array_double(anom)
        pyisc._free_array_int(cla)
        pyisc._free_array_int(clu)


        return result
