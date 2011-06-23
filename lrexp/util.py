'''
Created on Feb 10, 2011

@author: christopherreilly
'''
from __future__ import with_statement
import pickle

def runExperiment( unit, steps = None , reset = True, callback = None, *args, **kwargs ):
    def doNothing( c, *args, **kwargs ): pass
    if callback is None: callback = doNothing
    for i, chain in enumerate( unit ):
        callback( chain, *args, **kwargs )
        if i is steps:
            break
    if reset: unit.initialize()

def saveUnit( unit, filename ):
    """
    Saves unit as a pickle file with .lre extension.
    
    So don't put .lre at the end of filename argument.
    """
    unit.initialize()
    with open( filename, 'wb' ) as file:
        pickle.dump( unit, file )
    print 'Saved unit'

def loadUnit( filename ):
    """
    Loads an unit from a .lre file with name filename.
    
    Returns an instance of the unit.
    """
    with open( filename, 'rb' ) as file:
        unit = pickle.load( file )
    return unit

class LRExpError( Exception ):
    """
    Custom Exception
    """
    pass

class LRExpSignal( Exception ):
    """
    Used to track execution state.
    """
    def __init__( self, chain ):
        self.chain = chain

    def __repr__( self ):
        return repr( self.chain )

def contains( parent, target ):
    for child in parent.children:
        if child is target or contains( child, target ): return True
    return False

