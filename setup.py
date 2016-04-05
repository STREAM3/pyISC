import os
import sys
from distutils.core import setup, Extension

from numpy.distutils.misc_util import get_numpy_include_dirs
from distutils.sysconfig import get_python_lib;


'''
In order to create a source distribution run setup build_ext sdist, otherwise the pyisc.py will not be generated from
pyisc.i, which is not distributed in the source distribution, only the generated sources are distributed.
'''

######## import numpy.i ##########
# Import numpy.i from current version. 
# See http://stackoverflow.com/questions/21855775/numpy-i-is-missing-what-is-the-recommended-way-to-install-it


np_file_name = 'numpy.i'

if not os.path.exists(np_file_name):
    import re
    import requests
    import numpy

    np_version = re.compile(r'(?P<MAJOR>[0-9]+)\.'
                            '(?P<MINOR>[0-9]+)') \
                            .search(numpy.__version__)
    np_version_string = np_version.group()
    np_version_info = {key: int(value)
                       for key, value in np_version.groupdict().items()}


    np_file_url = 'https://raw.githubusercontent.com/numpy/numpy/maintenance/' + \
                  np_version_string + '.x/tools/swig/' + np_file_name
    if(np_version_info['MAJOR'] == 1 and np_version_info['MINOR'] < 9):
        np_file_url = np_file_url.replace('tools', 'doc')

    chunk_size = 8196
    with open(np_file_name, 'wb') as file:
        for chunk in requests.get(np_file_url,
                                  stream=True).iter_content(chunk_size):
            file.write(chunk)

###### END numpy.i import #######

extra_flags = []

disc_dir = "."

dataframe_src_dir = os.path.join(disc_dir,'dataformat')
isc_src_dir = os.path.join(disc_dir, 'isc2')
pyisc_src_dir = "src"
pyisc_module_dir = "_pyisc_modules"
isclibraries = []

numpyincdir = get_numpy_include_dirs()

py_modules = [os.path.join(pyisc_module_dir, src) for src in ["__init__","BaseISC", "AnomalyDetector","DataObject", "SklearnClassifier"]]+["pyisc"]


pylib = get_python_lib()

# Must be updated if file structure has changed
if "uninstall" in sys.argv:

    from glob import glob
    files = [os.path.join(pylib, mod)+".py" for mod in py_modules] + \
            [os.path.join(pylib, mod)+".pyc" for mod in py_modules] + \
            [os.path.join(pylib,pyisc_module_dir)] + \
            [os.path.join(pylib, "pyisc-1.0-py2.7.egg-info")] + \
            glob(os.path.os.path.join(pylib, "_pyisc.*"))


    for file in files:
        if os.path.exists(file):
            if os.path.isdir(file):
                os.removedirs(file)
            else:
                os.remove(file)
            print "removing "+file

    sys.exit()

#add extra flags as needed, look in file our-g++

if sys.platform  == 'darwin':
    isclibraries += ["z"]
    extra_flags = ["-DPLATFORM_MAC"]
elif sys.platform == "win32":
    extra_flags = ["-DPLATFORM_MSW"]
else: # Default, works for Linux
    isclibraries += ["z"]
    extra_flags = ["-Wmissing-declarations","-DUSE_WCHAR -DPLATFORM_GTK"]


dataframe_sources = [os.path.join(dataframe_src_dir, src)
                     for src in "readtokens.o table.o format.o formatdispatch.o formatbinary.o " \
                                "formatdiscr.o formatcont.o formatsymbol.o formattime.o formatunknown.o " \
                                "data.o datafile.o datadispatch.o".replace(".o", ".cc").split()]
dataframe_headers = [s.replace(".cc", ".hh") for s in dataframe_sources]
isc_sources = [os.path.join(isc_src_dir, src)
               for src in "anomalydetector.o isc_mixture.o isc_component.o isc_micromodel_poissongamma.o " \
                          "isc_micromodel_gaussian.o isc_micromodel_multigaussian.o hmatrix.o gamma.o hgf.o"
                   .replace(".o", ".cc").split()]
isc_headers = [s.replace(".cc", ".hh") for s in isc_sources]

pyisc_sources = [os.path.join(pyisc_src_dir, src) for src in ["_Format.cc", "_DataObject.cc", "_AnomalyDetector.cc"]]
pyisc_headers = [s.replace(".cc", ".hh") for s in pyisc_sources]

# Only run when creating the distribution, not when installing it on someone else computer. Removes dependency on Swig
if os.path.exists('pyisc.i'):
    setup(name="pyisc",
          author="Tomas Olsson",
          author_email="tol@sics.se",
          url="http://www.sics.se",
          version="1.0",
          ext_modules=[
              Extension("_pyisc",
                        headers=dataframe_headers+isc_headers+pyisc_headers,
                        sources=dataframe_sources+isc_sources+pyisc_sources+["pyisc.i"],
                        include_dirs=[disc_dir, isc_src_dir, dataframe_src_dir, pyisc_src_dir]+numpyincdir,
                        extra_compile_args=extra_flags,
                        swig_opts=['-c++','-I'+str(disc_dir)])
          ],
          license="LGPLv3",
          classifiers=[
              'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)'
          ]
          )

# The following overlapping setup is only run in order to inlcude pyisc.py when all *.py files are copied to the same folder.

setup(name="pyisc",
      author="Tomas Olsson",
      author_email="tol@sics.se",
      url="http://www.sics.se",
      version="1.0",
      ext_modules=[
          Extension("_pyisc",
                    headers=dataframe_headers+isc_headers+pyisc_headers,
                    sources=dataframe_sources+isc_sources+pyisc_sources+["pyisc_wrap.cpp"],
                    include_dirs=[disc_dir, isc_src_dir,dataframe_src_dir,pyisc_src_dir]+numpyincdir,
                    extra_compile_args=extra_flags,
                    swig_opts=['-c++'])
      ],
      py_modules=py_modules,
      license="LGPLv3+",
      classifiers=[
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)'
      ]
      )


