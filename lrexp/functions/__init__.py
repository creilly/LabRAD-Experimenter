import os, types
from .. import LREXPHOME

class ModuleWrapper( object ):
    def __init__( self, module ):
        self.module = module
        self.doc = module.__doc__
        self.childFunctions = filter( lambda x: type( x ) is types.FunctionType, module.__dict__.values() )
        self.childModules = []

    def __name__( self ):
        return self.module.__name__.split( '.' )[-1]

__path__.append( os.environ[LREXPHOME] )
