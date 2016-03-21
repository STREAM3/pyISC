/*
 * DataObject.cc
 *
 *  Created on: Mar 6, 2015
 *      Author: tol
 */

#include "_DataObject.hh"
#include <formattypes.hh>


namespace pyisc {

//double* _to_cpp_array(double* in_array1D, int num_of_columns) {
//      return in_array1D;
//}

void _DataObject::init(pyisc::Format* format) {
	is_data_obj_created = 1;
	is_data_format_created = 0;

	isc_data_obj = new ::DataObject(format->get_isc_format());
	data_format = format;

	if(DEBUG)
		printf("Create _DataObject\n");
}

_DataObject::_DataObject(pyisc::Format *format) {
	init(format);
}

_DataObject::_DataObject(pyisc::Format *format, double* in_array2D, int num_of_rows,
		int num_of_columns) {
	init(format);
	add2DArray(in_array2D, num_of_rows, num_of_columns);
}

_DataObject::_DataObject(const char* formatfile, const char* datafile) {
	isc_data_obj = new ::DataObject(formatfile,datafile);
	data_format = new Format(isc_data_obj->format());
	is_data_obj_created = 1;
	is_data_format_created = 1;
}
_DataObject::_DataObject(::DataObject* data_object) {
	isc_data_obj = data_object;
	data_format = new Format(isc_data_obj->format());
	is_data_obj_created = 0;
	is_data_format_created = 1;
}

_DataObject::~_DataObject() {
	printf("Delete object");
	if (is_data_obj_created && isc_data_obj) {
		delete isc_data_obj;
	}
	if(	is_data_format_created && data_format) {
		delete data_format;
	}
}

void _DataObject::add2DArray(double* in_array2D, int num_of_rows, int num_of_columns) {
	intfloat* vec;
	for (int i = 0; i < num_of_rows; i++) {
		vec = isc_data_obj->newentry();
		_convert_to_intfloat((in_array2D+i*num_of_columns), num_of_columns, vec);
	}
}


void _DataObject::_convert_to_intfloat(double* in_array1D, int num_of_columns, intfloat* vec) {
	for (int j = 0; j < num_of_columns; j++) {
		switch(data_format->get_isc_format()->nth(j)->type()) {
		case FORMATSPEC_DISCR:
		case FORMATSPEC_SYMBOL:
		case FORMATSPEC_BINARY:
		case FORMATSPEC_UNKNOWN:
		case FormatSpecDatetimeType:
			vec[j].i = (int) in_array1D[j];
			break;
		case FORMATSPEC_CONT:
			vec[j].f = (float) in_array1D[j];
			break;
		default:
			printf("An unhandled isc format %i for value %f\n",data_format->get_isc_format()->nth(j)->type(), in_array1D[j]);
		}
	}
}

void _DataObject::add1DArray(double* in_array1D, int num_of_columns) {
	add2DArray(in_array1D, 1, num_of_columns);
}


int _DataObject::size() {
	return isc_data_obj->size();
}


int _DataObject::length() {
	return isc_data_obj->length();
}

Format* _DataObject::getFormat() {
	return data_format;
}

void pyisc::_DataObject::_as1DArray(double* out_1DArray, int num_of_elements) {
	int num_of_rows = isc_data_obj->size();
	int num_of_columns = isc_data_obj->length();
	if(num_of_elements != num_of_rows*num_of_columns) {
		printf("Wrong number of elements");
	}

	intfloat* vec;
	for (int i = 0; i < num_of_rows; i++) {
		vec = (*isc_data_obj)[i];
		_convert_to_numpyarray(vec, (out_1DArray+num_of_columns*i), num_of_columns);

	}
}

void pyisc::_DataObject::_convert_to_numpyarray(intfloat* vec, double* out_1DArray, int num_of_elements) {
	for (int j = 0; j < num_of_elements; j++) {
		switch(data_format->get_isc_format()->nth(j)->type()) {
		case FORMATSPEC_DISCR:
		case FORMATSPEC_SYMBOL:
		case FORMATSPEC_BINARY:
		case FORMATSPEC_UNKNOWN:
		case FormatSpecDatetimeType:
			out_1DArray[j] = (double) vec[j].i;
			break;
		case FORMATSPEC_CONT:
			out_1DArray[j] = (double) vec[j].f;
			break;
		default:
			printf("An unhandled isc format %i for value %i or %f\n",data_format->get_isc_format()->nth(j)->type(), vec[j].i, vec[j].f);
		}
	}
}

::DataObject* _DataObject::get_isc_data_object() {
	return isc_data_obj;
}

} /* namespace pyisc */

void pyisc::_DataObject::_getRow(int row_index, double* out_1DArray,
		int num_of_elements) {
	int num_of_columns = length();
	if(num_of_elements != num_of_columns) {
		printf("Wrong number of elements specified");
	}
	intfloat* vec = (*isc_data_obj)[row_index];
	_convert_to_numpyarray(vec, out_1DArray, num_of_columns);
}

intfloat* pyisc::_DataObject::_get_intfloat(int index) {
	return (*isc_data_obj)[index];
}
