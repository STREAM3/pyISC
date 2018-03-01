# pyISC 

The Python API to the ISC anomaly detection and classification framework. The framework implements Baysian statistical methods for anomaly detection and classification. Currently supported statistical models are: Poisson, Gamma and multivariate Gaussian distributions.

### Email forum(s)

Questions regarding the use of the framework: https://groups.google.com/forum/#!forum/pyisc-users

## Prerequisite:

Notice, pyISC/visISC has only been tested using 64 bit Python.

### Install Python distribution 

Install Python 2.7

Anaconda is the recommended Python distribution : https://www.continuum.io/downloads

Libraries: 
- numpy, scipy, sklearn (required for running pyisc)
- matplotlib, ipython, jupyter, pandas (only required for running tutorial examples)

Install with anaconda:  

(If you want to disable ssl verification when installing, you will find the instructions <a href="https://docs.continuum.io/anaconda-repository/faq#how-do-i-disable-ssl-checking-on-package-installation">here</a>.)

`>> conda install numpy pandas scikit-learn  ipython jupyter`


If you intend to also install visISC, you have to downgrade the numpy installation to version 1.9

`>> conda install numpy==1.9.3`

### Install a c++ compiler if not installed

Windows:

`>> conda install mingw libpython==1.0`

OS X:

Install the Xcode developer tools from App Store.

### Install Swig

(search for suitable version with `>> anaconda search -t conda swig`)

Windows:

`>> conda install --channel https://conda.anaconda.org/salilab swig`

OS X:

`>> conda install --channel https://conda.anaconda.org/minrk swig`


## Installation

For installing from source code, you need a <a href="https://git-scm.com/downloads">git client</a>

Then:

`>> git clone https://github.com/STREAM3/pyisc --recursive`

`>> cd pyisc`

`>> python setup.py install`

## Run tutorial

`>> cd docs`

`>> jupyter notebook pyISC_tutorial.ipynb`

If not opened automatically, click on `pyISC_tutorial.ipynb` in the web page that was opened in a web browser.

### How to Cite 

Emruli, B., Olsson, T., & Holst, A. (2017).  pyISC: A Bayesian Anomaly Detection Framework for Python. In Florida Artificial Intelligence Research Society Conference. Retrieved from https://aaai.org/ocs/index.php/FLAIRS/FLAIRS17/paper/view/15527

