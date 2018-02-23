/*
 * _JSonExporter.cc
 *
 *  Created on: Feb 9, 2018
 *      Author: tol
 */

 #include "_JSonExporter.hh"


namespace pyisc {


 void _JSonExporter::notImplemented(){}

 void _JSonExporter::addParameter(const char* parameter_name, const char* value){
	 root[std::string(parameter_name)] = std::string(value);
}

 void _JSonExporter::addParameter(const char* parameter_name, int value){
	 root[std::string(parameter_name)] = value;
}
 void _JSonExporter::addParameter(const char* parameter_name, float value){
	 root[std::string(parameter_name)] = value;
}
 void _JSonExporter::addParameter(const char* parameter_name, double value){
	 root[std::string(parameter_name)] = value;
}
 void _JSonExporter::addParameter(const char* parameter_name, int *values, int length){
	 ArduinoJson::JsonArray& array = root.createNestedArray(std::string(parameter_name));
	 for(int i=0; i < length;i++) {
		 array.add(values[i]);
	 }
}
 void _JSonExporter::addParameter(const char* parameter_name, float *values, int length){
	 ArduinoJson::JsonArray& array = root.createNestedArray(std::string(parameter_name));
	 for(int i=0; i < length;i++) {
		 array.add(values[i]);
	 }
 }
 void _JSonExporter::addParameter(const char* parameter_name, double *values, int length){
	 ArduinoJson::JsonArray& array = root.createNestedArray(std::string(parameter_name));
	 for(int i=0; i < length;i++) {
		 array.add(values[i]);
	 }
}

 IscAbstractModelExporter* _JSonExporter::createModelExporter(const char * parameter_name) {
	 return ( IscAbstractModelExporter*) new _JSonExporter(root.createNestedObject(std::string(parameter_name)));
 }
 IscAbstractModelExporter* _JSonExporter::createModelExporter(int parameter_id){
	 return ( IscAbstractModelExporter*) new _JSonExporter(root.createNestedObject(to_string(parameter_id)));
}

std::string _JSonExporter::getJSonString() {
	std::string str;
	root.prettyPrintTo(str);
	return str;
}
}
