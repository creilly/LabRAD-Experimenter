'''
A model/view structure for browsing functions in python packages.

Modules are automatically parsed for information about child modules/functions.
'''
import os, types, inspect, time

from PyQt4 import QtGui, QtCore

from view import TreeView

from zope.interface import Interface, Attribute, implements
from twisted.python import components

class FunctionModel( QtGui.QStandardItemModel ):
    FUNCTION = 0
    MODULE = 1
    NONE = 2
    BUILTIN = 3

class IFunctionModelItem( Interface ):
    """
    An object that can be manipulated by the FunctionModel
    """
    type = Attribute( "Should be either FUNCTION or MODULE type (defined in the FunctionModel class" )
    object = Attribute( "The function or module that you represent" )
    def getInfoWidget():
        """
        Returns a QtGui.QWidget that shows information about the item
        """

class BaseFunctionModelItem( QtGui.QStandardItem ):
    implements( IFunctionModelItem )
    type = FunctionModel.NONE
    object = None
    def __init__( self ):
        super( BaseFunctionModelItem, self ).__init__()
        self.setEditable( False )
    def appendFunctionModelItem( self, obj ):
        fmi = IFunctionModelItem( obj )
        self.appendRow( fmi )
        return fmi
    def getInfoWidget( self ): pass

class FunctionItem( BaseFunctionModelItem ):
    """
    For use with types.FunctionType functions
    """
    type = FunctionModel.FUNCTION
    def __init__( self, obj ):
        super( FunctionItem, self ).__init__()
        self.object = obj
        self.setText( obj.__name__ + ' (F)' )
        self.setToolTip( obj.__module__ )

    def getInfoWidget( self ):
        return InfoWidget( '%s (<b>F</b>)' % self.object.__name__, getFormattedFunctionTypeInfo( self.object ) )

components.registerAdapter( FunctionItem, types.FunctionType, IFunctionModelItem )

class ModuleItem( BaseFunctionModelItem ):

    packageFiles = ( '__init__.py', '__init__.pyc' )
    type = FunctionModel.MODULE
    def __init__( self, obj ):
        super( ModuleItem, self ).__init__()
        self.object = obj
        self.setText( obj.__name__.split( '.' )[-1] + ' (M)' )
        self.setToolTip( obj.__name__ )
        for function in sorted( filter( lambda x: type( x ) is types.FunctionType, obj.__dict__.values() ), key = lambda f: f.__name__ ):
            self.appendFunctionModelItem( function )
        if hasattr( obj, '__file__' ):
            path, file = os.path.split( obj.__file__ )
            if os.path.splitext( file )[0] == '__init__':
                modNames = set( ['.'.join( ( obj.__name__, name ) ) for name, ext in sorted( [os.path.splitext( file ) for file in os.listdir( path )] ) if name and name != '__init__' ] )
                for modName in modNames:
                    try:
                        module = __import__( modName, fromlist = modName )
                        self.appendFunctionModelItem( module )
                    except ImportError:
                        continue
        if not self.rowCount(): self.setText( '%s - Empty' % self.text() )

    def getInfoWidget( self ):
        info = []
        def appendParagraph( p ):
            info.append( '<p>%s</p>' % p )
        appendParagraph( '<i>Full name:</i> <b>%s</b>' % self.object.__name__ )
        appendParagraph( '<i>Documentation:</i> %s' % self.object.__doc__ if self.object.__doc__ else 'No documenation' )
        return InfoWidget( '%s (<b>M</b>)' % self.object.__name__.split( '.' )[-1], ''.join( info ) )

components.registerAdapter( ModuleItem, types.ModuleType, IFunctionModelItem )

class BuiltinModuleItem( ModuleItem ):
    """
    For use with a builtin python module.
    Finds other modules and builtin functions.
    """
    def __init__( self, builtinModule ):
        super( ModuleItem, self ).__init__()
        fullName = builtinModule.__name__
        self.setText( '%s (M)' % fullName.split( '.' )[-1] )
        self.setToolTip( fullName )
        self.object = builtinModule
        for builtinFunction in filter( lambda x: type( x ) is types.BuiltinFunctionType, builtinModule.__dict__.values() ):
            self.appendFunctionModelItem( builtinFunction )

class BuiltinFunctionItem( BaseFunctionModelItem ):
    """
    Because you can not inspect the arguments of a builtin function,
    these can only be used as an input value (for use with a FunctionType called 'call' or something like that).
    """
    type = FunctionModel.BUILTIN
    def __init__( self, bif ):
        super( BuiltinFunctionItem, self ).__init__()
        self.object = bif
        self.setText( '%s (F)' % bif.__name__ )
        self.setToolTip( bif.__module__ )

    def getInfoWidget( self ):
        doc = self.object.__doc__
        doc = doc if doc else 'No documentation'
        return InfoWidget( '%s (<b>F</b>)' % self.object.__name__, '<i>Documentation:</i> %s' % doc )

components.registerAdapter( BuiltinFunctionItem, types.BuiltinFunctionType, IFunctionModelItem )

class Organizer( BaseFunctionModelItem ):
    implements( IFunctionModelItem )
    def __init__( self, text ):
        super( Organizer, self ).__init__()
        self.setText( text )
        self.object = None
        self.type = FunctionModel.NONE
        italics = QtGui.QFont()
        italics.setItalic( True )
        self.setFont( italics )
    def getInfoWidget( self ):
        pass

components.registerAdapter( Organizer, str, IFunctionModelItem )

class FunctionBrowser( TreeView ):
    def __init__( self, parent = None ):
        super( FunctionBrowser, self ).__init__( parent )

    def keyPressEvent( self, event ):
        key = event.key()
        if key == QtCore.Qt.Key_Space:
            self.showInfo()
            return
        super( FunctionBrowser, self ).keyPressEvent( event )

    def showInfo( self ):
        index = self.currentIndex()
        if index.isValid():
            item = self.model().itemFromIndex( index )
            if not IFunctionModelItem.providedBy( item ): return
            w = item.getInfoWidget()
            if w is None: return
            d = QtGui.QDialog( self )
            d.setLayout( QtGui.QVBoxLayout() )
            d.layout().addWidget( w )
            d.exec_()
            self.activateWindow()

def getFormattedFunctionTypeInfo( function ):
    info = []
    def appendParagraph( p ):
        info.append( '<p>%s</p>' % p )
    module = '<i>Module:</i> <b>%s</b>' % function.__module__
    appendParagraph( module )
    argspecs = inspect.getargspec( function )
    args, defs = ['<b>%s</b>' % arg for arg in argspecs[0]], argspecs[3]
    if defs:
        defs = ['<i>%s</i>' % str( defVal ) for defVal in defs]
        defs = [ ' = '.join( ( name, value ) ) for name, value in zip( args[len( args ) - len( defs ):], defs ) ]
        args = ', '.join( ( ', '.join( args[:len( args ) - len( defs )] ), ', '.join( defs ) ) )
    else:
        args = ', '.join( args )
    args = '<i>Arguments:</i> %s' % ( args if args else 'None' )
    appendParagraph( args )
    if argspecs[1]:
        appendParagraph( '<i>List argument:</i> <b>%s</b>' % argspecs[1] )
    if argspecs[2]:
        appendParagraph( '<i>Keyword argument:</i> <b>%s</b>' % argspecs[2] )
    appendParagraph( '<i>Documentation:</i> %s' % function.__doc__.strip() if function.__doc__ else 'No documenation' )
    return ''.join( info )

class InfoWidget( QtGui.QWidget ):
    def __init__( self, title, info ):
        super( InfoWidget, self ).__init__()
        layout = QtGui.QVBoxLayout( self )
        layout.addWidget( QtGui.QLabel( '<big>%s</big>' % title ) )
        infoFrame = QtGui.QFrame()
        infoFrame.setLayout( QtGui.QVBoxLayout() )
        info = info.replace( '\n', '<br>' )
        text = QtGui.QTextEdit( info.replace( '\n', '<br>' ) )
        text.setReadOnly( True )
        infoFrame.layout().addWidget( text )
        infoFrame.setFrameStyle( QtGui.QFrame.Box )
        layout.addWidget( infoFrame, 1 )
