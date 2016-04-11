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

#ifndef IscPoissonMicroModelOneside_HH_
#define IscPoissonMicroModelOneside_HH_

#include <math.h>
#include <intfloat.hh>
#include <isc_micromodel.hh>
#include <isc_micromodel_poissongamma.hh>

class IscPoissonMicroModelOneside : public IscPoissonMicroModel {
public:
  IscPoissonMicroModelOneside(int ir, int it) : IscPoissonMicroModel(ir, it) {};
  virtual ~IscPoissonMicroModelOneside() {};
  virtual double anomaly(intfloat* vec) {
	  if (vec[indr].f*sumt < sumr*vec[indt].f)
		  return 0.0;
	  else
		  return IscPoissonMicroModel::anomaly(vec);
  };
};

#endif //IscPoissonMicroModelOneside_HH_
