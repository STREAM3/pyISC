/*
 * _JSonImporter.cc
 *
 *  Created on: 19 Feb 2018
 *      Author: tol
 */


#include "_JSonImporter.hh"

namespace pyisc {

void _JSonImporter::notImplemented(){printf("JSon importer not implemented\n");}

void _JSonImporter::fillParameter(const char* parameter_name, int& value){
	if(DEBUG)
		printf("Import %s as int:%i", parameter_name, value);
	value = (*root)[std::string(parameter_name)];
}
void _JSonImporter::fillParameter(const char* parameter_name, float& value){
	if(DEBUG)
		printf("Import %s as float:%f", parameter_name, value);
	value = (*root)[std::string(parameter_name)];
}
void _JSonImporter::fillParameter(const char* parameter_name, double& value){
	if(DEBUG)
		printf("Import %s as double:%d", parameter_name, value);
	value = (*root)[std::string(parameter_name)];
}
void _JSonImporter::fillParameter(const char* parameter_name, int *values, int length){
	if(DEBUG)
		printf("Import %s as int array", parameter_name);

	ArduinoJson::JsonArray& array = (*root)[std::string(parameter_name)];
	for(int i=0; i < length;i++) {
		values[i] = array[i];
	}
}
void _JSonImporter::fillParameter(const char* parameter_name, float *values, int length){
	if(DEBUG)
		printf("Import %s as float array", parameter_name);

	ArduinoJson::JsonArray& array = (*root)[std::string(parameter_name)];
	for(int i=0; i < length;i++) {
		values[i] = array[i];
	}
}
void _JSonImporter::fillParameter(const char* parameter_name, double *values, int length){
	if(DEBUG)
		printf("Import %s as double array", parameter_name);

	ArduinoJson::JsonArray& array = (*root)[std::string(parameter_name)];
	for(int i=0; i < length;i++) {
		values[i] = array[i];
	}
}

IscAbstractModelImporter* _JSonImporter::getModelImporter(const char * parameter_name) {
	if(DEBUG)
		printf("Import %s as json object", parameter_name);

	ArduinoJson::JsonObject& object = (*root)[std::string(parameter_name)];
	return ( IscAbstractModelImporter*) new _JSonImporter(&object);
}
IscAbstractModelImporter* _JSonImporter::getModelImporter(int parameter_id){
	if(DEBUG)
		printf("Import %i as json object", parameter_id);

	ArduinoJson::JsonObject& object = (*root)[std::to_string(parameter_id)];
	return ( IscAbstractModelImporter*) new _JSonImporter(&object);
}

}  // namespace pyisc

