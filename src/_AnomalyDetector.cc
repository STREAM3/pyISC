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
#include <math.h>
#ifdef WIN32
#define _USE_MATH_DEFINES
#include <cmath>
#endif


/**
 * This is a function used to create a micro model for a given mixture component
 *
 * co is the creating object, that is, the inner anomaly detector.
 */
::IscMicroModel *inner_create_micro_model(const void* co, int mixtureCompIndex)
{
	return ((pyisc::_AnomalyDetector*)co)->_CreateMixtureComponet(mixtureCompIndex);
}

namespace pyisc {

::IscMicroModel *_AnomalyDetector::_CreateMixtureComponet(int mixtureComponentIndex) {
	return this->component_distribution_creators[mixtureComponentIndex]->create();
}


_AnomalyDetector::_AnomalyDetector(
		int off, int splt, double th,
		int cl, ::IscCombinationRule cr,
		std::vector<IscMicroModel*> component_distribution_creators) :
				::AnomalyDetector(component_distribution_creators.size(),off,splt,th,cl,cr, inner_create_micro_model) {

	for(int i=0; i <  component_distribution_creators.size(); i++) {
		this->component_distribution_creators.push_back(component_distribution_creators[i]->create());
	}
	if(DEBUG)
		printf("_AnomalyDetector created\n");
}


void _AnomalyDetector::importModel(IscAbstractModelImporter *importer) {
    if(DEBUG)
        printf("_AnomalyDetector calling importer\n");

	IscAbstractModelImporter *innerImporter = importer->getModelImporter("AnomalyDetector");

	if(DEBUG)
        printf("_AnomalyDetector importer cannot reach this far \n");

	::AnomalyDetector::importModel(innerImporter);

    delete innerImporter;


	for(int i=0; i <  component_distribution_creators.size(); i++) {
		IscAbstractModelImporter *compImporter = importer->getModelImporter(i);
		this->component_distribution_creators[i]->importModel(compImporter);
		//delete compImporter;
	}

	if(DEBUG)
		printf("_AnomalyDetector imported\n");
}


void _AnomalyDetector::exportModel(IscAbstractModelExporter *exporter) {
    IscAbstractModelExporter *innerExporter = exporter->createModelExporter("AnomalyDetector");
	::AnomalyDetector::exportModel(innerExporter);
    delete innerExporter;

	for(int i=0; i <  component_distribution_creators.size(); i++) {
		IscAbstractModelExporter *compExporter = exporter->createModelExporter(i);
		this->component_distribution_creators[i]->exportModel(compExporter);
		delete compExporter;
	}

	if(DEBUG)
		printf("_AnomalyDetector exported\n");


}

_AnomalyDetector::~_AnomalyDetector() {
	if(DEBUG)
		printf("_AnomalyDetector deletion started\n");

	for(int i=0; i <  this->component_distribution_creators.size(); i++) {
		delete this->component_distribution_creators[i];
	}

	if(DEBUG)
		printf("_AnomalyDetector deleted\n");
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

void _AnomalyDetector::_UntrainOne(Format* format, double* in_array1D, int num_of_columns) {
	intfloat* vec = new intfloat[num_of_columns];
	for (int j = 0; j < num_of_columns; j++) {
		if (format->get_isc_format()->nth(j)->type() == FORMATSPEC_DISCR) {
			vec[j].i = (int) in_array1D[j];
		} else if (format->get_isc_format()->nth(j)->type()
				== FORMATSPEC_CONT) {
			vec[j].f = (float) in_array1D[j];
		}
	}
	::AnomalyDetector::UntrainOne(vec);

	delete [] vec;
}

void _AnomalyDetector::_TrainDataIncrementally(pyisc::_DataObject* d) {
	for(int i=0; i < d->size(); i++) {
		::AnomalyDetector::TrainOne((*d->get_isc_data_object())[i]);
	}

}

void _AnomalyDetector::_UntrainDataIncrementally(pyisc::_DataObject* d) {
	for(int i=0; i < d->size(); i++) {
		::AnomalyDetector::UntrainOne((*d->get_isc_data_object())[i]);
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
		printf("Wrong number of classes or clusters");
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

	delete [] devs;
	delete [] expect2;

}



} /* namespace pyisc */


