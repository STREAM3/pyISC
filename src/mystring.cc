/*
 * mystring.cc
 *
 *  Created on: 23 Feb 2018
 *      Author: tol
 */
#include "mystring.hh"

std::string to_string(int i) {
    std::ostringstream stm ;
    stm << i;
    return stm.str();
}
