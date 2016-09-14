import unittest

from pyisc import DataObject
from numpy import array, c_,unique
from scipy.stats import norm
from numpy.testing.utils import assert_allclose, assert_equal

class test_DataObject(unittest.TestCase):
    def test_dataobject_set_column_values(self):
        X = array([norm(1.0).rvs(10) for _ in range(1000)])
        y = [None] * 1000

        DO = DataObject(c_[X,y], class_column=len(X[0]))
        assert_equal(len(X[0]), DO.class_column)
        assert_equal(unique(y), DO.classes_)

        classes=[None] + ['1', '2', '3', '4', '5']
        DO = DataObject(c_[X,y], class_column=len(X[0]), classes=classes)
        assert_equal(len(X[0]), DO.class_column)
        assert_equal(classes, DO.classes_)

        X2 = DO.as_2d_array()
        assert_allclose(X2.T[:-1].T.astype(float), X)
        assert_equal(X2.T[-1],y)

        new_y = ["%i"%(divmod(i,5)[1]+1) for i in range(len(X))]
        DO.set_column_values(len(X[0]), new_y)

        assert_equal(len(X[0]), DO.class_column)
        assert_equal([None]+list(unique(new_y)), DO.classes_)

        X2 = DO.as_2d_array()
        assert_allclose(X2.T[:-1].T.astype(float), X)
        assert_equal(X2.T[-1], new_y)



if __name__ == '__main__':
    unittest.main()
