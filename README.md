# pyISC 

The Python API to the ISC anomaly detection and classification framework.


##Prerequisite:

Notice, pyISC/visISC is only been tested on 64 bits machines.

###Install Python distribution 

Install Python 2.7

Anaconda is the recommended Python distribution : https://www.continuum.io/downloads

Libraries: 
- numpy (required for running pyisc)
- matplotlib, ipython, jupyter, pandas, scikit-learn (only required for running tutorial examples)
           
Install with anacond:  

`>> conda install numpy pandas scikit-learn  ipython jupyter`

If you intend to also install visISC, you have to downgrade the numpy installation to version 1.9

`>> conda install numpy==1.9.3`

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

`>> git clone https://github.com/STREAM3/pyisc --recursive`

`>> cd pyisc`

`>> python setup.py install`

## Run tutorial

`>> cd docs`

`>> jupyter notebook pyISC_tutorial.ipynb`

If not opened automatically, click on `pyISC_tutorial.ipynb` in the web page that was opened in a web browser.
