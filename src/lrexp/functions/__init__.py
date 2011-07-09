"""
Append LREXPHOME to our module's search path to allow the package to find the custom module
"""
import os
from .. import LREXPHOME

__path__.append( os.environ[LREXPHOME] )
