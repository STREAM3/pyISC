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

#ifndef ANOMALYDETECTOR2_HH_
#define ANOMALYDETECTOR2_HH_

#include <math.h>
#include <isc_component.hh>
#include <isc_mixture.hh>
#include <isc_micromodel.hh>
#include <anomalydetector.hh>
#include "_DataObject.hh"
#include <isc_micromodel_markovgaussian.hh>
#include <vector>


namespace pyisc {


class _AnomalyDetector : ::AnomalyDetector {
public:
	_AnomalyDetector(
			int off,
			int splt,
			double th,
			int cl,
			::IscCombinationRule cr,
			 std::vector<IscMicroModel*> vector);
	/**
	 * n is number of isc mixture components
	 * off is the first column containing features used by the detector
	 * splt is a the column containing a known class
	 * th is a threshold on when to consider a vector of data as anomalous
	 * cl is a variable if zero indicate no clustering else indicates that clustering should be done
	 * cr is variable indicating how the anomaly scores for the different isc mixture components should be combined
	 * cf is a function that creates a isc micro component for each of the n isc mixture component.
	 *
	 *
	 * An isc micro model uses or more columns as input.
	 *
	 * Pattern of input data vector: (ignored columns(header), distribution components, #distribution input values per component)
	 *
	 */
	//	_AnomalyDetector(int n, int off, int splt, double th, int cl,
	//			::IscCombinationRule cr, ::IscCreateFunc cf); // Or a creation function for the appropriate micromodels can be used
	virtual ~_AnomalyDetector();
	virtual void _SetParams(int off, int splt, double th, int cl);
	virtual void _Reset();
	virtual void _TrainOne(Format* format, double* in_array1D, int num_of_columns);
	virtual void _UntrainOne(Format* format, double* in_array1D, int num_of_columns);
	virtual void _TrainData(_DataObject* d);
	virtual void _TrainDataIncrementally(_DataObject* d);
	virtual void _UntrainDataIncrementally(_DataObject* d);

	virtual void _CalcAnomaly(class _DataObject* d, double* deviations, int deviations_length);
	virtual void _ClassifyData(class _DataObject* d, int* class_ids, int class_ids_length, int* cluster_ids, int cluster_ids_length);

	virtual int _CalcAnomalyDetails(union intfloat* vec, double* anom, int* cla,
			int* clu, double* devs = 0, union intfloat* peak = 0,
			union intfloat* min = 0, union intfloat* max = 0,
			double* expect = 0, double* var = 0);
	/*virtual int CalcAnomalyDetailsSingle(union intfloat* vec, int mmind,
			int cla, int clu, double* devs = 0, union intfloat* peak = 0,
			union intfloat* min = 0, union intfloat* max = 0,
			double* expect = 0, double* var = 0);*/

	virtual ::IscMicroModel *_CreateMixtureComponet(int mixtureComponentIndex);

	virtual ::AnomalyDetector* get_isc_anomaly_detector() {return this;};

	virtual void _CalcAnomalyDetailPerformanceTest(pyisc::_DataObject* obj);

	virtual void _LogProbabilityOfData(class _DataObject* d, double* logp, int size);

private:
	std::vector<IscMicroModel*> component_distribution_creators;
};


} /* namespace pyisc */

#endif /* ANOMALYDETECTOR2_HH_ */
