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


#ifndef FORMAT_HH_
#define FORMAT_HH_

#include <format.hh>
#include <formattypes.hh>

#ifndef DEBUGISC
#define DEBUGISC 0
#endif

namespace pyisc {
class FormatSpec{

public:
	FormatSpec(::FormatSpec *isc_format_spec) {_isc_format = isc_format_spec;};
	const char* get_name() {return _isc_format->name;};
	const char* represent(int v) { return _isc_format->represent(intfloat(v)); };
	const char* represent(float v) { return _isc_format->represent(intfloat(v)); };
	int getnum() { return _isc_format->getnum(); };
	void add(const char* str) {_isc_format->add(str);};
	::FormatSpec *_isc_format;
};

class Format {
	int is_format_created = 0;

protected:
	::Format* isc_format;

public:
	enum ColumnType {
		Discrete,
		Continuous,
		Symbol,
		TIME
	};

	Format();
	/**
	 * Convert isc orginial format to pyisc format
	 */
	Format(::Format*);
	virtual ~Format();

	/**
	 * Add a new column to the format with name and type.
	 */
	virtual void addColumn(const char *name, ColumnType type);

	/**
	 * TODO memory leak!
	 */
	virtual FormatSpec* get_nth_column(int n) {return new FormatSpec(isc_format->nth(n));};
	virtual FormatSpec* nth(int n) {return get_nth_column(n);};
	virtual void add(FormatSpec*);
	virtual int size();

	virtual void printColumnNames();

	virtual ::Format* get_isc_format();
};
}



#endif /* FORMAT_HH_ */
