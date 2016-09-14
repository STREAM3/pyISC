
 %module pyisc

 %{
 #define SWIG_FILE_WITH_INIT

 /* Includes the header in the wrapper code */
 #include "dataformat/format.hh"
 #include "dataformat/formatbinary.hh"
 #include "dataformat/formatcont.hh"
 #include "dataformat/formatdiscr.hh"
 #include "dataformat/formatsymbol.hh"
 #include "dataformat/dynindvector.hh"
 #include "dataformat/data.hh"
 #include "isc2/isc_micromodel.hh"
 #include "isc2/hmatrix.hh"
 #include "isc2/isc_micromodel_gaussian.hh"
 #include "isc2/isc_component.hh"
 #include "isc2/isc_mixture.hh"
 #include "isc2/gamma.hh"
 #include "isc2/isc_micromodel_multigaussian.hh"
 #include "isc2/hgf.hh"
 #include "isc2/isc_micromodel_poissongamma.hh"
 #include "isc2/isc_micromodel_markovgaussian.hh"
 //#include "isc2/isc_micromodel_multidirichlet.hh"
 #include "isc2/anomalydetector.hh"
 #include "src/_Format.hh"
 #include "src/_DataObject.hh"
 #include "src/_AnomalyDetector.hh"
 %}
 %include <typemaps.i>
 %include "numpy.i"
 %init %{
 import_array();
 %}





%inline %{
  /* Create any sort of [size] array */

    int *_int_array(int size) {
     return (int *) new int[size];
  }

  int **_int_pointer_array(int size) {
     return (int **) new int*[size];
  }

  void _free_array_int_pointer(int** array, int length) {
    delete [] array;
  }

  void _set_int_array(int** array2D, int index, int*array1D) {
     array2D[index] = array1D;
  }

  void _set_array_value(int *array1, int index, int val) {
  	array1[index] = val;
  }

  int _get_array_value(int *array1, int index) {
  	return array1[index];
  }

  double* _double_array(int size) {
  	return (double*) new double[size];
  }

  int _get_int_value(int *array1, int index) {
  	return array1[index];
  }


  intfloat* _intfloat_array(int size) {
  	return (intfloat*) new intfloat[size];
  }

  void _free_array_intfloat(intfloat* array) {
    delete [] array;
}

   float _get_intfloat_value(intfloat *array1, int index) {
  	return (float) array1[index];
  }


  double _get_double_value(double* array1, int index) {

  	return array1[index];
  }

  double _set_double_value(double* array1, int index, double value) {
	    array1[index] = value;
  }

  double* _to_cpp_array(double* IN_ARRAY1, int DIM1) {
	double* out_array = new double[DIM1];
	for(int i=0; i < DIM1; i++) {
		out_array[i] = IN_ARRAY1[i];
	}

	return out_array;
 }

 void _free_array_double(double* array) {
    delete [] array;
}

   int* _to_cpp_array_int(int* IN_ARRAY1, int DIM1) {
	int* out_array = new int[DIM1];
	for(int i=0; i < DIM1; i++) {
		out_array[i] = IN_ARRAY1[i];
	}

	return out_array;
 }

void _free_array_int(int* array) {
    delete [] array;
}
 
   void _to_numpy_array_double(double* inarray, double* ARGOUT_ARRAY1, int DIM1) {
	for(int i=0; i < DIM1; i++) {
		ARGOUT_ARRAY1[i] = inarray[i];
	}
 }
 
    void _to_numpy_array_int(int* inarray, int* ARGOUT_ARRAY1, int DIM1) {
	for(int i=0; i < DIM1; i++) {
		ARGOUT_ARRAY1[i] = inarray[i];
	}
 }
 

  char* _get_string_value(char** strings, int i) {
    return strings[i];
  }


  IscMarkovGaussMicroModel** _to_pointer(std::vector<IscMarkovGaussMicroModel*> vec) {
    IscMarkovGaussMicroModel** new_vec = new IscMarkovGaussMicroModel*[vec.size()];
    for(int i=0; i < vec.size(); i++) {
        new_vec[i] = vec[i];
    }
    return new_vec;
  }

  void _free_pointer(IscMarkovGaussMicroModel** new_vec) {
    delete [] new_vec;
  }


  %}

 %apply (double* IN_ARRAY1, int DIM1) {(double* in_array1D, int num_of_columns)}
 %apply (double* IN_ARRAY2, int DIM1, int DIM2) {(double* in_array2D, int num_of_rows, int num_of_columns)}
 %apply (double* ARGOUT_ARRAY1, int DIM1) {(double* deviations, int deviations_length)}
 %apply (int* ARGOUT_ARRAY1, int DIM1) {(int* class_ids, int class_ids_length)}
 %apply (int* ARGOUT_ARRAY1, int DIM1) {(int* cluster_ids, int cluster_ids_length)}
 %apply (double* ARGOUT_ARRAY1, int DIM1) {(double* out_1DArray, int num_of_elements)}
 %apply (double* ARGOUT_ARRAY1, int DIM1) {(double* logp, int size)}

  /* Parse the header file to generate wrappers */

 enum IscCombinationRule {IscMax, IscPlus};


 %ignore IscCombinationRule;
 %ignore IscMax;
 %ignore IscPlus;

 %rename ("_%s", regexmatch$name="^Isc") "";

 %include "std_vector.i"

 %include "src/_Format.hh"
 %include "src/_DataObject.hh"
 %include "src/_AnomalyDetector.hh"
 %include "isc2/isc_component.hh"
 %include "isc2/isc_micromodel.hh"
 %include "isc2/isc_micromodel_multigaussian.hh"
 %include "isc2/isc_micromodel_poissongamma.hh"
 %include "isc2/isc_micromodel_markovgaussian.hh"
 #%include "isc2/isc_micromodel_multidirichlet.hh"

#%template(_IscMicroModelCreator) pyisc::_IscMicroModelCreatorTemplate<IscMicroModel>;
#%template(_IscMarkovGaussMicroModelCreator) pyisc::_IscMicroModelCreatorTemplate<IscMarkovGaussMicroModel>;

%template(_IscMicroModelVector) std::vector<IscMicroModel*>;
%template(_IscMarkovGaussMicroModelVector) std::vector<IscMarkovGaussMicroModel*>;


 %pythoncode %{
from _pyisc_modules.BaseISC import *
from _pyisc_modules.AnomalyDetector import *
from _pyisc_modules.DataObject import *
from _pyisc_modules.SklearnClassifier import *
from _pyisc_modules.SklearnClusterer import *
from numpy import array, dtype, double


def _to_numpy_array(inarray, n, type=double):
    if type == double:
        return _to_numpy_array_double(inarray,n);
    elif type == int:
        return _to_numpy_array_int(inarray,n);
    print "Unknown type ", type

 %}



  %extend pyisc::_DataObject {
    intfloat* _DataObject::__getitem__(int i) {
        return _get_intfloat(i);
    }
  }



