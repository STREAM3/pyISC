import os
import shutil
from distutils.sysconfig import get_python_lib;
pylib = get_python_lib()

for file in os.listdir('.'):
    if not file.startswith('setup'):
        print("copy", file, "to", os.path.join(pylib, file))
        if os.path.isdir(file):
            dst = os.path.join(pylib, file)
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(file,dst)
        else:
            shutil.copy(file,pylib)
