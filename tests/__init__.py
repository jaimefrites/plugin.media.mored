import os
from os import path
import sys
import unittest

_libs = path.join(path.dirname(__file__), os.pardir, 'resources', 'lib')
sys.path.insert(0, _libs)
_stubs = path.join(path.dirname(__file__), 'stublibs')
sys.path.insert(0, _stubs)
