from __future__ import with_statement
import pickle

def runExperiment( unit, steps = None , reset = True, callback = None, *args, **kwargs ):
    """
    Executes the unit.
    
    If steps is specified, only execute at most the specified number of steps.
    
    If execution has not completed before the number of steps specified, reset determines whether or not to initialize the unit.
    
    By default, reset is true.
    
    If callback is specified, the chain is passed as the first argument to callback, with whatever remaining arguments and keyword arguments coming after.
    """
    def doNothing( c, *args, **kwargs ): pass
    if callback is None: callback = doNothing
    for i, chain in enumerate( unit ):
        callback( chain, *args, **kwargs )
        if i is steps:
            break
    if reset: unit.initialize()

def saveUnit( unit, filename ):
    """
    Saves unit as a pickle file.
    It is recommended that you use the .lre extension for clarity.
    """
    unit.initialize()
    with open( filename, 'wb' ) as file:
        pickle.dump( unit, file )
    print 'Saved unit'

def loadUnit( filename ):
    """
    Loads a unit from file
    """
    with open( filename, 'rb' ) as file:
        unit = pickle.load( file )
    return unit

class LRExpError( Exception ):
    """
    Custom Exception
    """
    pass

def contains( parent, target ):
    """
    Looks recursively through the parent to see if the target is among its descendants.
    """
    for child in parent.children:
        if child is target or contains( child, target ): return True
    return False

