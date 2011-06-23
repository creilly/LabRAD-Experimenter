'''
Created on Apr 29, 2011

@author: christopherreilly
'''
import yaml, types, __builtin__, math, time, os
from PyQt4 import QtGui, QtCore

from zope.interface import Interface, Attribute, implements
from dialogs.function import FunctionDialog, LabradDialog
from functionbrowser import BuiltinModuleItem, getFormattedFunctionTypeInfo
from component import updateModel
from labradconnection import LRConnectionManager

from ..lr import LabradSetting

class Edit( object ):
    def __init__( self, requestedEdit ):
        self.value = requestedEdit

class IEditGetter( Interface ):
    """
    Provides Edits to the Editor.  Users access EditGetters through an Editor
    """
    editCreated = Attribute( 'Signal emitting an Edit object.' )

    def getEdit():
        """
        Initiates creation of an Edit.  If an Edit is created, EditGetter emits editCreated signal.
        """

class BaseEditGetter( QtCore.QObject ):
    implements( IEditGetter )

    editCreated = QtCore.pyqtSignal( Edit )

    def getEdit( self ):
        pass

class TextGetter( BaseEditGetter ):

    default = ''

    def __init__( self, prompt, parent ):
        super( TextGetter, self ).__init__( parent )
        self.prompt = prompt

    def getEdit( self ):
        text, result = QtGui.QInputDialog.getText( self.parent(), 'New text input', self.prompt if self.prompt else 'Enter string', text = self.default )
        if result:
            self.editCreated.emit( Edit( str( text ) ) )
            self.setDefault( text )

    def setDefault( self, default ):
        self.default = default

class YamlGetter( TextGetter ):
    def getEdit( self ):
        text, result = QtGui.QInputDialog.getText( self.parent(), 'New text input', self.prompt if self.prompt else 'Enter string', text = self.default if self.default else '' )
        if result:
            try:
                value = yaml.load( str( text ) )
                self.editCreated.emit( Edit( value ) )
                self.setDefault( str( text ) )
            except yaml.parser.ParserError:
                self.prompt = 'Bad value'
                self.getEdit()

class FunctionGetter( BaseEditGetter ):
    def __init__( self, parent, *functionItems ):
        super( FunctionGetter, self ).__init__( parent )
        fd = self.functionDialog = FunctionDialog( parent )
        for functionItem in functionItems:
            fd.addFunctionModelItem( functionItem )
        def functionSelected( function ):
            fd.accept()
            self.editCreated.emit( Edit( function ) )
        fd.functionSelected.connect( functionSelected )
    def getEdit( self ):
        self.functionDialog.show()

class BuiltinFunctionGetter( BaseEditGetter ):
    def __init__( self, parent, *functionItems ):
        super( BuiltinFunctionGetter, self ).__init__( parent )
        fd = self.functionDialog = FunctionDialog( parent, 'Builtin python functions' )
        for functionItem in functionItems:
            fd.addFunctionModelItem( functionItem )
        def functionSelected( function ):
            fd.accept()
            self.editCreated.emit( Edit( function ) )
        fd.builtinFunctionSelected.connect( functionSelected )
    def getEdit( self ):
        self.functionDialog.show()

class LabradSettingGetter( BaseEditGetter ):
    def __init__( self, parent ):
        super( LabradSettingGetter, self ).__init__( parent )
        ld = self.labradDialog = LabradDialog( parent )
        def functionSelected( lrSetting ):
            ld.accept()
            self.editCreated.emit( Edit( lrSetting ) )
        ld.labradSettingSelected.connect( functionSelected )
    def getEdit( self ):
        self.labradDialog.show()
class IEditor( Interface ):
    editCreated = Attribute( "Signal" )
    def addEditGetter( getter, text ):
        """
        Adds an IEditGetter.  Optional text argument to describe the getter.
        """

class Editor( QtGui.QGroupBox ):
    implements( IEditor )

    editCreated = QtCore.pyqtSignal( Edit )

    def __init__( self, title, parent = None ):
        super( Editor, self ).__init__( title, parent )
        self.setLayout( QtGui.QVBoxLayout() )
        text = self.text = QtGui.QLabel()
        text.setWordWrap( True )
        text.setAlignment( QtCore.Qt.AlignCenter )

        buttonRow = self.buttonRow = QtGui.QHBoxLayout()
        buttonRow.addStretch()

        self.layout().addWidget( text, 1 )
        self.layout().addLayout( buttonRow )

    def setText( self, text ):
        self.text.setText( text )

    def getText( self ):
        return self.text.text()

    def addEditGetter( self, getter, text = None ):
        getter.editCreated.connect( self.editCreated.emit )
        if text:
            requestorButton = QtGui.QPushButton( text )
            requestorButton.clicked.connect( getter.getEdit )
            self.buttonRow.addWidget( requestorButton )
            return requestorButton

class TextEditor( Editor ):
    def __init__( self, title, prompt = 'Enter text', parent = None, ):
        super( TextEditor, self ).__init__( title, parent )
        self.addEditGetter( TextGetter( prompt, self ), 'New' )

class ValueEditor( Editor ):
    def __init__( self, title, prompt = 'Enter YAML string', default = None, parent = None ):
        super( ValueEditor, self ).__init__( title, parent )
        yamlGetter = YamlGetter( prompt, self )
        yamlGetter.setDefault( default if default else '' )
        self.addEditGetter( yamlGetter, 'Yaml Value' )
        __builtin__.__name__ = 'Builtin Functions'
        self.addEditGetter( BuiltinFunctionGetter( self, *[BuiltinModuleItem( module ) for module in ( __builtin__, math, time )] ), 'Builtin' )

class FunctionEditor( Editor ):
    def __init__( self, title, parent ):
        super( FunctionEditor, self ).__init__( title, parent )
        modules = []
        try:
            from ..functions import standard
            modules.append( standard )
        except ImportError:
            pass
        try:
            from ..functions import custom
            modules.append( custom )
        except ImportError:
            pass
        self.addEditGetter( FunctionGetter( self, *modules ), 'New Function' )
        labradButton = self.addEditGetter( LabradSettingGetter( self ), 'LabRAD' )
        labradConnection = LRConnectionManager( self )
        labradButton.setEnabled( labradConnection.connected )
        labradButton.setToolTip( 'Must have LabRAD connection' )
        labradConnection.connectionChanged.connect( labradButton.setEnabled )

class FunctionEditorUpdater( FunctionEditor ):
    def __init__( self, component, title, parent ):
        super( FunctionEditorUpdater, self ).__init__( title, parent )

        self.setText( self.formatFunction( component.function ) )

        @updateModel
        def editFunction( function ):
            self.setText( self.formatFunction( function ) )
            component.function = function
        self.editCreated.connect( lambda edit: editFunction( edit.value ) )

    def formatFunction( self, function ):
        if function is None:
            return '<i>No function assigned</i>'
        if type( function ) is LabradSetting:
            return function.doc
        return '<i>Name:</i> <b>%s</b><br />%s' % ( function.__name__, getFormattedFunctionTypeInfo( function ) )
