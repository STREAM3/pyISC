/*
 --------------------------------------------------------------------------
 Copyright (C) 2014, 2015, 2016 SICS Swedish ICT AB

 Main author: Tomas Olsson <tol@sics.se>

 This code is free software: you can redistribute it and/or modify it
 under the terms of the GNU Lesser General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This code is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Lesser General Public License for more details.

 You should have received a copy of the GNU Lesser General Public License
 along with this code.  If not, see <http://www.gnu.org/licenses/>.
 --------------------------------------------------------------------------
 */

#ifndef DATAOBJECT_HH_
#define DATAOBJECT_HH_

#include <format.hh>
#include <data.hh>
#include "_Format.hh"

namespace pyisc {

//extern double* _to_cpp_array(double* in_array1D, int num_of_columns);
class _DataObject {
	int is_data_obj_created = 0;
	int is_data_format_created = 0;

protected:
	pyisc::Format* data_format;
	::DataObject *isc_data_obj;

public:
	/**
	 * Create an empty DataObject with a Format that specifies the data types of the columns in a row
	 */
	_DataObject(pyisc::Format *f);
	/**
	 * Create an DataObject for the double array with a Format that specifies the data types of the columns in a row
	 */
	_DataObject(pyisc::Format *format, double* in_array2D, int num_of_rows, int num_of_columns);
	virtual ~_DataObject();

	/**
	 * Read isc original data objet from file
	 */
	_DataObject(const char* formatfile, const char* datafile = 0);

	/**
	 * Convert isc original data object to pyisc
	 */
	_DataObject(::DataObject* data_object0);
	/**
	 * Add a 1D numpy array as a row to the data object
	 */
	virtual void add1DArray(double* in_array1D, int num_of_columns);


	/**
	 * Add a 2D numpy array to the data object
	 */
	virtual void add2DArray(double* in_array2D, int num_of_rows, int num_of_columns);

	/**
	 * Returns number of rows.
	 */
	virtual int size();

	/**
	 * Returns number of columns.
	 */
	virtual int length();

	virtual Format* getFormat();

	/**
	 * Returns a 1D array representation of the data rows*cols.
	 */
	virtual void _as1DArray(double* out_1DArray, int num_of_elements);

	/**
	 * Returns a single array at the given row.
	 */
	virtual void _getRow(int row_index, double* out_1DArray, int num_of_elements);

	virtual ::DataObject* get_isc_data_object();

	/**
	 * Takes an numpy array from swig and convert it to a provided intfloat pointer
	 */
	virtual void _convert_to_intfloat(double* in_array1D, int num_of_columns, intfloat* vec);
	/**
	 * Takes an intfloat pointer  from swig and convert it to a provided numpy array.
	 */
	virtual void _convert_to_numpyarray(intfloat* vec, double* ARGOUT_ARRAY1, int DIM1);

	virtual intfloat* _get_intfloat(int index);

	/**
	 * Takes a numpy array and sets it values as the given column values.
	 */
	virtual void set_column_values(int column_index, double* in_array1D, int num_of_columns);

protected:
	void init(pyisc::Format* format);

};

}



#endif /* DATAOBJECT_HH_ */
