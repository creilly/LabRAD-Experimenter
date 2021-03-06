'''
Created on Feb 24, 2011

@author: christopherreilly
'''
import inspect, numpy, types

from zope.interface import Interface, Attribute, implements
from util import LRExpError, contains
from lr import LabradSetting

class IComponent( Interface ):
    """
    Component interface.
    All components must implement a children attribute to be compatible with the tree structure of experiments.
    """
    children = Attribute( "A list of the unit's children" )

class BaseComponent( object ):
    """
    Abstract base class for components.
    """
    implements( IComponent )

    @property
    def children( self ):
        return []

class Label( BaseComponent ):
    """
    Contains a single component, basically a nametag.
    """
    def __init__( self, name, component ):
        self.name = name
        self.component = component

    @property
    def children( self ):
        return [self.component]

    def __repr__( self ):
        return self.name

class Input( BaseComponent ):
    """
    The basic variable object for lrexp.
    
    An Input is a kind of pointer.  lrexp deferences the Input by accessing its value attribute.
      
    Possesses optional name and description attributes.
    """

    def __init__( self, value = None ):
        self.value = value
        self.description = ''
        self.name = ''

    def __repr__( self ):
        def shortRepr( s ):
            max = 15
            s = str( s )
            if len( s ) > max:
                return s[:max] + '...'
            return s
        return '%s -> %s' % ( self.name if self.name else self.__class__.__name__, shortRepr( self.value ) )

    @property
    def children( self ):
        return []

class Global( Input ):
    """
    A special type of Input.
    
    The Experimenter GUI looks for Globals in the tree and allows top level access to their attributes.
    """
    def __init__( self, name ):
        self.name = name
        self.value = None
        self.description = ''

    def __repr__( self ):
        return '%s (Global) -> %s' % ( self.name, str( self.value ) )

    def __deepcopy__( self, memo ):
        """
        Trying to copy a Global returns the Global itself.
        """
        return self

class ComponentGroup( BaseComponent ):
    """
    Base class for components who hold many components.
    """
    implements( IComponent )
    def __init__( self, name, *components ):
        self.name = name
        self._components = list( components )

    @property
    def children( self ):
        return self.components

    def __len__( self ):
        return len( self.components )

    def __iter__( self ):
        return self.components.__iter__()

    def __repr__( self ):
        return '%s (%d)' % ( self.name, len( self.components ) )
    @property
    def components( self ):
        return self._components

    def emptyComponents( self ):
        while self.components: self.components.pop()

class Arguments( ComponentGroup ):
    """
    Represents the collection of function arguments.
    """
    def __init__( self, *arguments ):
        super( Arguments, self ).__init__( 'Arguments', *arguments )

class ArgumentList( ComponentGroup ):
    """
    Represents a function's list argument (if it has one)
    """
    MONO = 0
    POLY = 1

    def __init__( self ):
        super( ArgumentList, self ).__init__( 'Argument List' )
        self._mode = self.POLY

    @property
    def mode( self ):
        return self._mode

    def setMode( self, mode ):
        self._mode = mode
        self.emptyComponents()
        if mode is self.MONO:
            monoInput = Input()
            monoInput.value = []
            monoInput.description = "MONO mode input: Value should be a collection"
            self.components.append( monoInput )

    def __iter__( self ):
        if self.mode is self.MONO:
            return self.components[0].value.__iter__()
        if self.mode is self.POLY:
            return [input.value for input in self.components].__iter__()

    def __len__( self ):
        if self.mode is self.MONO:
            return len( self.components[0].value )
        if self.mode is self.POLY:
            return len( self.components )

    def __repr__( self ):
        return '%s (%s mode)' % ( self.name, {self.MONO:'Mono', self.POLY:'Poly'}[self.mode] )

class Parameter( BaseComponent ):
    """
    Holds function arguments and special Unit attributes.
    """
    implements( IComponent )
    def __init__( self, name, input = None, description = '' ):
        self._name = name
        if input is None: input = Input( None )
        self.input = input
        self.description = description

    @property
    def name( self ):
        return self._name

    def __repr__( self ):
        def shortRepr( s ):
            max = 35
            s = s if isinstance( s, str ) else repr( s )
            if len( s ) > max:
                return s[:max] + '...'
            return s
        name = self.name if isinstance( self.name, str ) else repr( self.name )
        return ( '%s (%s)' % ( name, shortRepr( self.description ) ) ) if self.description else name

    @property
    def children( self ):
        return [self.input]

class Keyword( Parameter ):
    """
    For use with a functions dictionary argument.
    """
    pass

class KeywordArguments( ComponentGroup ):
    """
    Represents a function's dictionary argument (if it has one)
    """
    implements( IComponent )
    def __init__( self ):
        super( KeywordArguments, self ).__init__( 'Key-value pairs' )
    def toDict( self ):
        d = {}
        for child in self.components:
            d[child.name] = child.input.value
        return d

class Function( BaseComponent ):
    """
    Abstract class that encapsulates the action of a python function
    
    Automatic creation of parameters and enabling/disabling of list arguments
    """

    def getArgs( self ):
        args = [parameter.input.value for parameter in self.args]
        if self.argListEnabled:
            args.extend( self.argList )
        return args, ( self.kwargDict.toDict() if self.keywordEnabled else {} )

    #===========================================================================
    # Properties
    #===========================================================================
    @property
    def argListEnabled( self ):
        if self.function is None: return False
        if type( self.function ) is LabradSetting: return False
        return bool( inspect.getargspec( self.function )[1] )

    @property
    def keywordEnabled( self ):
        if self.function is None: return False
        if type( self.function ) is LabradSetting: return True
        return bool( inspect.getargspec( self.function )[2] )

    def getFunction( self ):
        if not hasattr( self, '_function' ):
            self._function = None
        return self._function
    def setFunction( self, function ):
        self._function = function
        self.argList.emptyComponents()
        self.kwargDict.emptyComponents()
        self.args.emptyComponents()
        if type( function ) is types.FunctionType:
            argNames, defs = ( inspect.getargspec( function )[i] for i in ( 0, 3 ) )
            defs = [] if defs is None else defs
            argVals = [None for i in range( len( argNames ) - len( defs ) )]
            argVals.extend( defs )
            args = []
            for name, defaultValue in zip( argNames, argVals ):
                args.append( Parameter( name, Input( defaultValue ) ) )
        elif type( function ) is LabradSetting:
            args = [Parameter( name ) for name in function.parameters]
        for arg in args:
            self.args.components.append( arg )

    @property
    def args( self ):
        if not hasattr( self, '_args' ):
            self._args = Arguments()
        return self._args

    @property
    def argList( self ):
        if not hasattr( self, '_argList' ):
            self._argList = ArgumentList()
        return self._argList

    @property
    def kwargDict( self ):
        if not hasattr( self, '_kwargDict' ):
            self._kwargDict = KeywordArguments()
        return self._kwargDict

    function = property( getFunction, setFunction )

    @property
    def children( self ):
        children = []
        if len( self.args ):
            children.append( self.args )
        if self.argListEnabled:
            children.append( self.argList )
        if self.keywordEnabled:
            children.append( self.kwargDict )
        return children

class Map( Function, Input ):
    """
    An Input that maps many inputs to a single value using a function
    """
    def __init__( self ):
        self.name = ''
        self.description = ''

    #===========================================================================
    # Properties
    #===========================================================================
    @property
    def value( self ):
        args, kwargs = self.getArgs()
        if self.function:
            return self.function( *args, **kwargs )
        else:
            raise LRExpError( 'No function assigned to Map' )

    def __repr__( self ):
        return '%s -> %s' % ( ( '%s (Map)' % self.name ) if self.name else 'Map', self.function.__name__ if self.function else 'No function' )

class IUnit( IComponent ):
    """
    An object capable of incremental execution; experiments are composed of trees of units.
    """
    configured = Attribute( "A boolean indicating if the unit is ready for execution" )

    def __iter__():
        """
        Must be able to iterate over a unit.
        """

class Unit( BaseComponent ):
    """
    Base class for units.
    
    Defines the modes of execution:
    
        PROBE: Execute child units without altering their mode.
        STEP: Execute child units as though they were in ALL mode.
        ALL: Completes unit execution all at once.
    """
    implements( IUnit )

    #Smallest step
    PROBE = 0
    #Unit by unit
    STEP = 1
    #All units
    ALL = 2

    def __init__( self, name = 'Unnamed unit' ):
        self.name = name

    @classmethod
    def signal( cls, state = None ):
        return ( cls, state )

    def __iter__( self ):
        class Iterator( object ):
            def __iter__( self ): return self
            def next( self ): raise StopIteration
        return Iterator()

    def initialize( self ):
        """
        Override this, calling the superclass method and 
        deleting/resetting any other necessary values, as 
        well as the values of any Units in possession.
        """
        pass

    def __repr__( self ):
        return self.name

    @property
    def children( self ):
        return []

    @property
    def configured( self ):
        return False

    def getMode( self ):
        if not hasattr( self, '_mode' ):
            self._mode = self.PROBE
        return self._mode
    def setMode( self, mode ):
        self._mode = mode

    mode = property( getMode, setMode )

nullInstance = None
class NullUnit( Unit ):
    """
    Does nothing.  Is a singleton (like python's None).
    
    Useful in Conditions, as place holders, etc.
    """
    def __new__( cls, name = 'Doesnt Matter' ):
        global nullInstance
        if nullInstance:
            return nullInstance
        nullInstance = super( NullUnit, cls ).__new__( cls )
        super( NullUnit, cls ).__init__( nullInstance, 'Null Unit' )
        return nullInstance
    def __init__( self, name = 'Doesnt Matter' ):
        pass
    @property
    def configured( self ):
        return True
    def __deepcopy__( self, memo ):
        return self
    def __nonzero__( self ):
        return False

class Action( Function, Unit ):
    """
    A Unit that calls a function with specified arguments when the next() method is called.
    
    Completes execution in one step regardless of mode.
    """
    class Result( Input ):
        def __init__( self, parentAction ):
            self.parentAction = parentAction
            self.value = None
            self.description = ''

        def __repr__( self ):
            return 'Result for Action: %s' % self.parentAction.name

    def __init__( self, name ):
        super( Function, self ).__init__( name )
        self.result = self.Result( self )

    def __iter__( self ):
        args, kwargs = self.getArgs()
        resultValue = self.function( *args, **kwargs )
        self.result.value = resultValue
        yield [self.signal( resultValue )]

    @property
    def children( self ):
        children = [self.result]
        children.extend( super( Action, self ).children )
        return children

    @property
    def configured( self ):
        return bool( self.function )

    def initialize( self ):
        self.result.value = None

Result = Action.Result

class ScanRange( ComponentGroup ):
    """
    Contains the values for the Scan Unit to scan over.
    
    There exist four different scan modes:
    
        DELTA: Specify beginning, end, and distance between steps
        STEPS: Specify beginning, end, and number of steps in between
        COLLECTION: Iterate over the value attributes of a group of inputs.
        LIST: Iterate over a single input, whose value attribute is a collection.
    """

    DELTA = 0
    STEPS = 1
    COLLECTION = 2
    LIST = 3
    def __init__( self, mode = DELTA ):
        super( ScanRange, self ).__init__( 'Scan range' )
        self.setMode( mode )

    def setMode( self, mode ):
        self._mode = mode
        self.emptyComponents()
        if mode is self.DELTA:
            self._components.extend( Parameter( name, Input( 1 ), '' ) for name in ( 'Start', 'End', 'Delta' ) )
        if mode is self.STEPS:
            self._components.extend( Parameter( name, Input( 0 ), '' ) for name in ( 'Start', 'End', 'Steps' ) )
        if mode is self.COLLECTION:
            pass
        if mode is self.LIST:
            listInput = Input()
            listInput.value = []
            listInput.description = 'Contains list to iterate over'
            self.components.append( listInput )

    def __iter__( self ):
        mode = self.mode
        components = self.components
        if mode is self.DELTA:
            beginning, end, delta = ( parameter.input.value for parameter in components )
            if beginning <= end:
                return numpy.arange( beginning, end, delta ).__iter__()
            else:
                return ( -1 * numpy.arange( -1 * beginning, -1 * end, delta ) ).__iter__()
        if mode is self.STEPS:
            args = tuple( parameter.input.value for parameter in components )
            return numpy.linspace( args[0], args[1], int( args[2] ) ).__iter__()
        if mode is self.COLLECTION:
            return ( input.value for input in components )
        if mode is self.LIST:
            return self.components[0].value.__iter__()

    def __len__( self ):
        mode, components = self.mode, self.components
        if mode is self.DELTA:
            return int( abs( components[1].input.value - components[0].input.value ) / components[2].input.value )
        if mode is self.STEPS:
            return int( components[2].input.value )
        if mode is self.COLLECTION:
            return len( components )
        if mode is self.LIST:
            return len( components[0].value )

    @property
    def mode( self ):
        return self._mode

    def __repr__( self ):
        modes = ( 'Delta', 'Steps', 'Collection', 'List' )
        return '%s (%s mode)' % ( super( ScanRange, self ).__repr__(), modes[self.mode] )

class Scan( Unit ):
    """
    The analog of a python 'for' loop.
    
    Possesses a configurable Scan Range that specifies what you iterate over.
    Possesses a Scan Input whose value attribute is set to each item in the Scan Range's collection.
    Possesses a Scan Unit that is executed for each time the Scan Input's value is set to a new item in the Scan Range's collection. 
    """

    MARKEDFORSCANNING = '*** Marked for scanning ***'

    def __init__( self, name ):
        super( Scan, self ).__init__( name )
        self.scanRange = ScanRange()
        self.scanUnit = Sequence( 'Unnamed sequence' )
        self._tmpDescription = ''
        self._tmpValue = None
        self._scanInput = Label( 'Scan Input', Input( None ) )

    def __iter__( self ):
        unit, input, mode, length = self.scanUnit, self.scanInput, self.mode, len( self.scanRange )
        yield [self.signal()]
        for i, scanValue in enumerate( self.scanRange ):
            input.value = scanValue
            for chain in unit:
                if mode is self.PROBE:
                    chain.append( self.signal( ( i + 1, length ) ) )
                    yield chain
            if mode in ( self.PROBE, self.STEP ):
                yield [self.signal( ( i + 1, length ) )]

    def initialize( self ):
        if self.scanInput:
            self.scanInput.value = self._tmpValue
        self.scanUnit.initialize()

    @property
    def children( self ):
        children = [ self.scanUnit, self.scanRange ]
        if self.scanInput: children.append( self._scanInput )
        return children

    @property
    def configured( self ):
        return ( self.scanUnit is not None and
                 self.scanUnit.configured and
                 self.scanInput is not None and
                 contains( self.scanUnit, self.scanInput ) )

    def getScanInput( self ):
        return self._scanInput.component
    def setScanInput( self, input ):
        if self.scanInput is not None:
            self.scanInput.description = self._tmpDescription
            self.scanInput.value = self._tmpValue
        self._tmpDescription = input.description if input else ''
        self._tmpValue = input.value if input else None
        self._scanInput.component = input
        if input:
            self.scanInput.description = self.MARKEDFORSCANNING
    scanInput = property( getScanInput, setScanInput )

class Sequence( Unit ):
    """
    Executes an ordered sequence of units.
    """
    def __iter__( self ):
        mode, length = self.mode, len( self.sequence )
        yield [self.signal()]
        for i, unit in enumerate( self.sequence ):
            for chain in unit:
                if mode is self.PROBE:
                    chain.append( self.signal( ( i + 1, length ) ) )
                    yield chain
            if mode in ( self.PROBE, self.STEP ):
                yield [self.signal( ( i + 1, length ) )]

    def initialize( self ):
        for step in self.sequence:
            step.initialize()

    def addUnit( self, unit, index = None ):
        """
        Add unit to sequence at specified index.
        If no index specified, append sequence with unit.
        """
        if index is None: self.sequence.append( unit )
        else: self.sequence.insert( index, unit )

    @property
    def configured( self ):
        return bool( self.sequence ) and all( [unit.configured for unit in self.sequence] )
    @property
    def children( self ):
        return self.sequence
    @property
    def sequence( self ):
        if not hasattr( self, '_sequence' ): self._sequence = []
        return self._sequence

class Repeat( Unit ):
    """
    Executes a unit a specified number of times.
    """
    def __init__( self, name = None, repeatUnit = None, repeats = 1 ):
        super( Repeat, self ).__init__( name )
        self.repeatUnit = repeatUnit if repeatUnit else Sequence( 'Unnamed sequence' )
        self.repeats = Parameter( 'Repeats', Input( repeats ) )

    def __iter__( self ):
        unit, mode, length = self.repeatUnit, self.mode, self.repeats.input.value
        yield [self.signal()]
        for i in range( length ):
            for chain in unit:
                if mode is self.PROBE:
                    chain.append( self.signal( ( i + 1, length ) ) )
                    yield chain
            if mode in ( self.PROBE, self.STEP ):
                yield [self.signal( ( i + 1, length ) )]

    def initialize( self ):
        self.repeatUnit.initialize()

    @property
    def configured( self ):
        return self.repeatUnit.configured
    @property
    def children( self ):
        return self.repeatUnit, self.repeats

class Conditional( Unit ):
    """
    Executes one of two units based on result of a condition
    """
    def __init__( self, name ):
        super( Conditional, self ).__init__( name )
        self.trueUnit = Label( 'True Unit', Sequence( 'If True' ) )
        self.falseUnit = Label( 'False Unit', NullUnit() )
        self.condition = Parameter( 'Condition', Input( True ) )

    def __iter__( self ):
        true, false, condition, mode = self.trueUnit.component, self.falseUnit.component, bool( self.condition.input.value ), self.mode
        yield [self.signal( condition )]
        for chain in ( true if condition else false ):
            if mode is self.PROBE:
                chain.append( self.signal( condition ) )
                yield chain
        if mode in ( self.PROBE, self.STEP ):
            yield [self.signal()]

    @property
    def configured( self ):
        return ( self.trueUnit.component.configured and self.falseUnit.component.configured )

    @property
    def children( self ):
        return self.trueUnit, self.falseUnit, self.condition
