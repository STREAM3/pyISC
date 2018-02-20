/*
 * _JSonExporter.hh
 *
 *  Created on: Feb 9, 2018
 *      Author: tol
 */

#ifndef JSONEXPORTER_HH_
#define JSONEXPORTER_HH_

#include "isc_exportimport.hh"
#include "ArduinoJson.hpp"

namespace pyisc {

// for convenience

class _JSonExporter : ::IscAbstractModelExporter {
public:
	_JSonExporter():root(jsonBuffer.createObject()){};
	virtual ~_JSonExporter(){};

	virtual void notImplemented();

	virtual void addParameter(const char* parameter_name, const char* value);
	virtual void addParameter(const char* parameter_name, int value);
	virtual void addParameter(const char* parameter_name, float value);
	virtual void addParameter(const char* parameter_name, double value);
	virtual void addParameter(const char* parameter_name, int *value, int length);
	virtual void addParameter(const char* parameter_name, float *value, int length);
	virtual void addParameter(const char* parameter_name, double *value, int length);

	virtual IscAbstractModelExporter* createModelExporter(const char * parameter_name);
	virtual IscAbstractModelExporter* createModelExporter(int parameter_id);

	virtual std::string getJSonString();

protected:
	_JSonExporter(ArduinoJson::JsonObject& root):root(root){
	};

private:
	ArduinoJson::DynamicJsonBuffer jsonBuffer;
	ArduinoJson::JsonObject& root;
};

}


#endif /* JSONEXPORTER_HH_ */

