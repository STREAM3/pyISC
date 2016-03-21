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

#include "_AnomalyDetector.hh"
#include <isc_micromodel_multigaussian.hh>
#include <isc_micromodel_poissongamma.hh>
#include "IscPoissonMicroModelOneside.hh"
#include <math.h>
#ifdef WIN32
#define _USE_MATH_DEFINES
#include <cmath>
#endif

/**
 * co is the creating object, that is, the inner anomaly detector.
 */
::IscMicroModel *inner_create_micro_model(const void* co, int mixtureCompIndex)
{
	return ((pyisc::_AnomalyDetector*)co)->GetMixtureComponet(co, mixtureCompIndex);
}



namespace pyisc {



//AnomalyDetector::AnomalyDetector(int n, int off, int splt, double th,
//		int cl) {
//	isc_anomaly_detector = new ::AnomalyDetector(n,off,splt,th,cl);
//}
/**
 * component_distributions and num_of_features_per_component are freed in this class deconstructor
 */
_AnomalyDetector::_AnomalyDetector(int n, int off, int splt, double th,
		int cl, ::IscCombinationRule cr,  int *component_distributions, int **component_feature_index, int* component_feature_length) : ::AnomalyDetector(n,off,splt,th,cl,cr, ::inner_create_micro_model) {
	this->component_distributions = component_distributions;
	this->component_feature_index = component_feature_index;
	this->component_feature_length = component_feature_length;
}

void _AnomalyDetector::_SetParams(int off, int splt, double th, int cl) {
	::AnomalyDetector::SetParams(off,splt,th,cl);
}

void _AnomalyDetector::_Reset() {
	::AnomalyDetector::Reset();
}

void _AnomalyDetector::_TrainOne(Format* format, double* in_array1D, int num_of_columns) {
	intfloat* vec = new intfloat[num_of_columns];
	for (int j = 0; j < num_of_columns; j++) {
		if (format->get_isc_format()->nth(j)->type() == FORMATSPEC_DISCR) {
			vec[j].i = (int) in_array1D[j];
		} else if (format->get_isc_format()->nth(j)->type()
				== FORMATSPEC_CONT) {
			vec[j].f = (float) in_array1D[j];
		}
	}
	::AnomalyDetector::TrainOne(vec);

	delete [] vec;
}

void _AnomalyDetector::_TrainDataIncrementally(pyisc::_DataObject* d) {
	for(int i=0; i < d->size(); i++) {
		::AnomalyDetector::TrainOne((*d->get_isc_data_object())[i]);
	}

}


void _AnomalyDetector::_TrainData(_DataObject* d) {
	::AnomalyDetector::TrainData(d->get_isc_data_object());
}

void _AnomalyDetector::_CalcAnomaly(class _DataObject* d,  double* deviations, int deviantions_length) {
	if(	deviantions_length != d->size()) {
		printf("Wrong deviations lengths");
	}
	::AnomalyDetector::CalcAnomaly(d->get_isc_data_object(), deviations);
}

void _AnomalyDetector::_ClassifyData(class _DataObject* d, int* class_ids, int class_ids_length,
		int* cluster_ids, int cluster_ids_length) {
	if(	class_ids_length !=  d->size() && cluster_ids_length !=  d->size()) {
		printf("Wrong number of clasess or clusters");
	}
	::AnomalyDetector::ClassifyData(d->get_isc_data_object(), class_ids, cluster_ids);
}

int _AnomalyDetector::_CalcAnomalyDetails(union intfloat* vec,
		double* anom, int* cla, int* clu, double* devs, union intfloat* peak,
		union intfloat* min, union intfloat* max, double* expect, double* var) {
	return ::AnomalyDetector::CalcAnomalyDetails(vec, *anom, *cla, *clu, devs, peak, min, max, expect, var);
}

void _AnomalyDetector::_LogProbabilityOfData(class _DataObject* data, double* logp, int size) {
	::DataObject *d = data->get_isc_data_object();
	int i, id = -1;
	intfloat* vec;
	int n = d->size();
	double min_logp=HUGE_VALF;
	for (i=0; i<n; i++) {
		vec = (*d)[i];
		if (split_attr != -1)
			id = vec[split_attr].i;
		logp[i] = isc->logp(vec+offset, id);
		if(logp[i] < min_logp) {
			min_logp = logp[i];
		}
	}
}

/*
int AnomalyDetector::CalcAnomalyDetailsSingle(union intfloat* vec,
		int mmind, int cla, int clu, double* devs, union intfloat* peak,
		union intfloat* min, union intfloat* max, double* expect, double* var) {
}*/


::IscMicroModel *_AnomalyDetector::GetMixtureComponet(const void* co, int mixtureComponentIndex) {
	switch(this->component_distributions[mixtureComponentIndex]) {
	case Gaussian:
		return new IscMultiGaussianMicroModel(this->component_feature_length[mixtureComponentIndex], this->component_feature_index[mixtureComponentIndex]);
	case Poisson:
		return new IscPoissonMicroModel(this->component_feature_index[mixtureComponentIndex][0],this->component_feature_index[mixtureComponentIndex][1]);
	case PoissonOneside:
		return new IscPoissonMicroModelOneside(this->component_feature_index[mixtureComponentIndex][0],this->component_feature_index[mixtureComponentIndex][1]);
	default:
		printf("Unknown component distribution %d", this->component_distributions[mixtureComponentIndex]);
		return NULL;
	}
}
_AnomalyDetector::~_AnomalyDetector(){
	if(component_feature_index) {
		for(int i=0; i < len; i++) {
			if(component_feature_index[i]) {
				delete [] component_feature_index[i];
			}
		}
		delete [] component_feature_index;
	}
}


void _AnomalyDetector::_CalcAnomalyDetailPerformanceTest(pyisc::_DataObject* d) {
	::DataObject* data = d->get_isc_data_object();
	double* expect2 = new double[d->length()];
	double dum3;
	int dum1, dum2;

	double *devs = new double[::AnomalyDetector::len];

	for(int i=0; i < d->size(); i++) {
		::AnomalyDetector::CalcAnomalyDetails((*data)[i], dum3, dum1, dum2, devs,
				0,0,0,expect2,0);
	}

}

} /* namespace pyisc */


