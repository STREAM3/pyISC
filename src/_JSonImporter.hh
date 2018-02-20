/*
 * _JSonImporter.hh
 *
 *  Created on: 19 Feb 2018
 *      Author: tol
 */

#ifndef SRC__JSONIMPORTER_HH_
#define SRC__JSONIMPORTER_HH_

#include "isc_exportimport.hh"
#include "ArduinoJson.hpp"
#ifndef DEBUG
#define DEBUG 1
#endif

namespace pyisc {


class _JSonImporter : IscAbstractModelImporter {
public:
	_JSonImporter(){
	};
	virtual ~_JSonImporter(){};
	virtual void notImplemented();

	// Methods that sets the values to the provided data structure
	virtual void fillParameter(const char* parameter_name, int &value);
	virtual void fillParameter(const char* parameter_name, float &value);
	virtual void fillParameter(const char* parameter_name, double &value);

	virtual void fillParameter(const char* parameter_name, int *value, int length);
	virtual void fillParameter(const char* parameter_name, float *value, int length);
	virtual void fillParameter(const char* parameter_name, double *value, int length);
	virtual IscAbstractModelImporter* getModelImporter(const char * parameter_name);
	virtual IscAbstractModelImporter* getModelImporter(int parameter_id);

	// Return True if succeeds
	bool parseJSon(std::string json) {
		root = &jsonBuffer.parseObject(json);
		return root->success();
	}
protected:
	_JSonImporter(ArduinoJson::JsonObject* root):root(root){
	};

private:
	ArduinoJson::DynamicJsonBuffer jsonBuffer;
	ArduinoJson::JsonObject* root;

};

}  // namespace pyisc





#endif /* SRC__JSONIMPORTER_HH_ */
