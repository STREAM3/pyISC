# pyISC 

The Python API to the ISC anomaly detection and classification framework.


##Prerequisite:

###Install Python distribution 

Anaconda is the recommended Python distribution: https://www.continuum.io/downloads

Libraries: 
- numpy (required for running pyisc)
- ipython, jupyter, pandas, scikit-learn (only required for running tutorial examples)
           
Install on anacond:  

`>> conda install numpy pandas scikit-learn  ipython jupyter`

### Install a c++ compiler if not installed

Windows:

`>> conda install mingw libpython`

###Install Swig

(search for suitable version with `>> anaconda search -t conda swig`)

Windows:

`>> conda install --channel https://conda.anaconda.org/salilab swig`

OS X:

`>> conda install --channel https://conda.anaconda.org/minrk swig`


## Installation:

`>> git clone https://github.com/STREAM3/pyisc -recursive`

`>> cd pyisc`

`>> python setup.py install`

## Run tutorial

`>> cd docs`

`>> jupyter notebook`
