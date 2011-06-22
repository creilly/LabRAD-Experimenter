'''
Created on May 16, 2011

@author: christopherreilly
'''
from lrexp2 import components

import types

def testAction():
    assert components.IUnit.implementedBy( components.Action )
    action = components.Action( 'My Action' )
    assert action.name == 'My Action'
    action.setFunction( lambda toSquare: toSquare ** 2 )
    assert action.argListEnabled is False
    assert len( action.args ) is 1
    assert action.args[0].name == 'toSquare'
    action.args[0].input.value = 9
    for chain in action:
        lastLink = chain[-1]
        assert lastLink[0] is components.Action
        assert lastLink[1] is 81

def testScan():
    scan = components.Scan( 'My Scan' )
    sequence = scan.scanUnit
    assert type( scan.scanUnit ) is components.Sequence
    action = components.Action( 'My Action' )
    action.setFunction( lambda toSquare: toSquare ** 2 )
    scan.scanUnit = action
    assert scan.configured is False
    scan.setScanInput( action.args[0].input )
    assert scan.scanRange.mode is scan.scanRange.DELTA
    scan.scanRange.components[0].input.value = 0
    scan.scanRange.components[1].input.value = 4
    scan.scanRange.components[2].input.value = 1
    assert scan.configured is True
    def runExp():
        i = 0
        for chain in scan:
            if len( chain ) is 2:
                print chain[0][1], ( 0, 1, 4, 9 )[i]
                assert chain[0][1] == ( 0, 1, 4, 9 )[i]
                i += 1
    runExp()
    scan.scanRange.setMode( scan.scanRange.COLLECTION )
    scan.scanRange.components = [components.Input( i ) for i in range( 4 )]
    runExp()
    scan.scanRange.setMode( scan.scanRange.LIST )
    scan.scanRange.components[0].value = range( 4 )
    runExp()

def testMap():
    sequence = components.Sequence( 'My Sequence' )
    actionA = components.Action( 'Action A' )
    actionB = components.Action( 'Action B' )
    sequence.addUnit( actionA )
    sequence.addUnit( actionB )
    actionA.setFunction( lambda toSquare: toSquare ** 2 )
    actionA.args[0].input.value = 6
    def printAll( *l ):
        for i in l:
            print i
    actionB.setFunction( printAll )
    assert actionB.argListEnabled
    actionB.argList.setMode( components.ArgumentList.MONO )
    assert len( actionB.argList.components ) is 1
    assert len( actionB.argList ) is 0
    map = components.Map()
    actionB.argList.components[0] = map
    map.setFunction( lambda * l: l )
    assert map.argListEnabled
    map.argList.setMode( components.ArgumentList.POLY )
    assert len( map.argList ) is 0
    assert len( map.argList.components ) is 0
    map.argList.components.append( actionA.result )
    map.argList.components.append( components.Input( 'Is the square of 6' ) )
    generator = sequence.__iter__()
    assert type( generator ) is types.GeneratorType
    step = generator.next()
    assert len( step ) is 1
    assert step[0][0] is components.Sequence
    assert step[0][1] is None
    step = generator.next()
    assert len( step ) is 2
    assert step[0][1] is 36
    for rest in generator: pass

from lrexp2.functions.standard import math, printer
from lrexp2.util import saveUnit, loadUnit

def testSave():
    actionA = components.Action( 'Add two' )
    actionA.setFunction( math.summation )
    glob = components.Global( 'Number' )
    glob.value = 10
    actionA.argList.components.append( glob )
    actionA.argList.components.append( components.Input( 2 ) )
    assert actionA.__iter__().next()[0][1] is 12
    actionB = components.Action( 'Print sum' )
    actionB.setFunction( printer.printX )
    actionB.args[0].input = actionA.result
    sequence = components.Sequence( 'Sum and print' )
    sequence.addUnit( actionA )
    sequence.addUnit( actionB )
    saveUnit( sequence, 'tmpSequence.lre' )
    sequence = loadUnit( 'tmpSequence.lre' )









