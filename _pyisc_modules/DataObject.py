"""
The Python Wrapper of all ISC DataObject methods.
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


from numpy import ndarray, array
from numpy.ma.extras import unique

import pyisc
from pyisc import Format

__author__ = 'tol'

class DataObject(pyisc._DataObject):

    '''
    The classes_ used to generate indexes into the class_column
    '''
    classes_ = None
    '''
    The column index that contains the class parameter.
    '''
    class_column = None

    def __init__(self, X, format=None, class_column=None, classes='auto'):
        '''
        The DataObject class represents the data analysed using a AnomalyDetector.

        X can be an Format instance or an numpy array. In the previous case, we assume
        it is used to describe the content that is added to the object using add2Darray
        or add1Darray methods. In the other case, we automatically generate a format instance,
        unless the format argument is provided. If the class_column is specified, we use it
        to generate a column in the auto-generated format where the elements are index into
        the classes_ list. If the classes_ list is set to 'auto', the elements in X of the
        class_column are used to auto-create a classes_ list.

        :param X: a Format instance or a numpy array
        :param format: None or a pyisc Format instance
        :param class_column: None or an integer
        :param classes: 'auto' or a list of elements in X[class_column]
        :return:
        '''
        self.class_column = class_column
        if isinstance(X, pyisc.Format):
            self._format = X
            pyisc._DataObject.__init__(self,X)
            return
        elif isinstance(X, ndarray):
            if format is None:
                format = Format()
                num_cols = len(X.T)
                if class_column is not None:
                    assert class_column >= 0 and class_column < num_cols
                for col in range(num_cols):
                    if col != class_column:
                        format.addColumn("Column %i"%col, Format.Continuous)
                    else:
                        format.addColumn("Column %i"%col, Format.Symbol)
                        A =  X.T.copy()
                        if classes == 'auto':
                            self.classes_ =  list(sorted(unique(A[class_column])))
                        else:
                            self.classes_ = classes
                        class_col = format.get_nth_column(class_column)
                        for c in self.classes_:
                            class_col.add("Class %i"%c if isinstance(c, int) else "Class %s"%c if isinstance(c, str) and len(c) == 1 else str(c))
                        A[class_column] = [self.classes_.index(v) if v in self.classes_ else -1 for v in A[class_column]]
                        X = A.T
                self._format = format
                if X.ndim == 1: # This fixes a problem of converting it to c++ data object
                    X = array([X.copy()]).T

                pyisc._DataObject.__init__(self,format,X.astype(float))
                return
            elif isinstance(format, pyisc.Format):
                self._format = format
                pyisc._DataObject.__init__(self,format,X)
                return
        pyisc._DataObject.__init__(self,X)

    def as_1d_array(self):
        array1D = self._as1DArray(self.size()*self.length()).astype(object)

        #print self.class_column, self.classes_, unique(array1D[range(self.class_column,len(array1D),self.length())])
        if self.class_column is not None:
            array1D[list(range(self.class_column,len(array1D),self.length()))] = \
                [self.classes_[int(c)] if int(c) != -1 else None for c in array1D[list(range(self.class_column,len(array1D),self.length()))] ]

        return array1D

    def as_2d_array(self):
        array1D = self.as_1d_array()
        return array1D.reshape((self.size(),self.length()))

    def set_column_values(self, column_index, values):
        '''
        Sets all values in a column, if the column is the class column, then the values must be one of the ones provieded in the constructor.
        :param column_index:
        :param values:
        :return:
        '''
        if column_index == self.class_column:
            values = [self.classes_.index(c) for c in values]
        pyisc._DataObject.set_column_values(self, column_index, array(values).astype(float))


    def __getitem__(self,index):
        if index <= -1:
            index = self.size()+index
        if index < self.size():
            return self._getRow(index, self.length())
        else:
            return None

    def __len__(self):
        return self.size()
