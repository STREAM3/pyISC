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
#include "_Format.hh"
#include <formatcont.hh>
#include <formatdiscr.hh>
#include <formattime.hh>
#include <formatsymbol.hh>


namespace pyisc {

Format::Format() {
	isc_format = new ::Format();
	is_format_created = 1;
	if(DEBUG)
		printf("Create isc format\n");

}

Format::Format(::Format *isc_format0) {
	isc_format = isc_format0;

}

Format::~Format() {
	if(is_format_created && isc_format) {
		if(DEBUG)
			printf("Delete isc format\n");
		delete isc_format;
	}
}

void Format::addColumn(const char* name, ColumnType type) {
	switch(type) {
	case Continuous:
		isc_format->add(new ::FormatSpecCont(name));
		break;
	case Discrete:
		isc_format->add(new ::FormatSpecDiscr(name));
		break;
	case TIME:
		isc_format->add(new ::FormatSpecDatetime(name));
		break;
	case Symbol:
		isc_format->add(new ::FormatSpecSymbol(name));
		break;
	default:
		printf("Unknown column type %i", type);
	};
}

void Format::add(FormatSpec* format_spec) {
	isc_format->add(format_spec->_isc_format->copy());
}


} /* namespace pyisc */

::Format* pyisc::Format::get_isc_format() {
	return isc_format;
}

void pyisc::Format::printColumnNames() {
	printf("Column names:\n");
	for(int j=0; j < size(); j++) {
		printf("  %s Type %i\n",isc_format->nth(j)->name, isc_format->nth(j)->type());
	}
}

int pyisc::Format::size() {
	return isc_format->length();
}

