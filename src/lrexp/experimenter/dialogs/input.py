'''
Edit dialogs for Input and its subclasses
'''
import yaml

from PyQt4 import QtGui
from . import ComponentEditDialog
from ..editor import TextEditor, ValueEditor, FunctionEditorUpdater
from ..component import updateModel
from ..globals import GlobalsModel

def updateModelPlus( f ):
    """
    Enhancement to the updateModel decorator to allow custom clean up after ComponentModel update.
    
    The class' cleanUp method (no args) will be called after the ComponentModel updates.
    """
    def _updateModel( *args, **kwargs ):
        updateModel( f )( *args, **kwargs )
        type( args[0] ).cleanUp( args[0] )
    return _updateModel

class BaseInputDialog( ComponentEditDialog ):
    """
    Dialog initialized with a description editor
    """
    def __init__( self, parent, component ):
        super( BaseInputDialog, self ).__init__( parent, component, 'Edit %s' % component.__class__.__name__ )

        descriptionEditor = self.descriptionEditor = TextEditor( 'Description', 'Enter new description' )
        descriptionEditor.setText( component.description )
        descriptionEditor.editCreated.connect( lambda edit: self.editDescription( edit.value ) )

        self.tabWidget.addTab( descriptionEditor, 'Description' )

    @updateModelPlus
    def editDescription( self, description ):
        self.descriptionEditor.setText( description )
        self.component.description = description

    def cleanUp( self ): pass

class ResultDialog( BaseInputDialog ):
    """
    Add navigation to the result's parentAction
    """
    def __init__( self, parent, component ):
        super( ResultDialog, self ).__init__( parent, component )
        self.matchModel.addCycler( self.matchView, component.parentAction, self.matchTreeWidget.addButton( 'Result Action' ) )
        self.matchModel.addColorCondition( component.parentAction, 'blue', QtGui.QFont.Bold )

class NamedInputDialog( BaseInputDialog ):
    """
    inputs with editable name attributes (Input and Global) get name edit tabs
    """
    def __init__( self, parent, component ):
        super( NamedInputDialog, self ).__init__( parent, component )

        nameEditor = self.nameEditor = TextEditor( 'Name', 'Enter new name' )
        nameEditor.setText( str( component.name ) )
        nameEditor.editCreated.connect( lambda edit: self.editName( edit.value ) )
        self.tabWidget.insertTab( 0, nameEditor, 'Name' )

    @updateModelPlus
    def editName( self, name ):
        self.nameEditor.setText( name )
        self.component.name = name


class InputDialog( NamedInputDialog ):
    """
    Inputs also get value edit tabs
    """
    def __init__( self, parent, component ):
        super( InputDialog, self ).__init__( parent, component )
        try:
            default = yaml.dump( component.value )
        except:
            default = ''
        valueEditor = self.valueEditor = ValueEditor( 'Value', default = default )
        valueEditor.setText( str( component.value ) )
        valueEditor.editCreated.connect( lambda edit: self.editValue( edit.value ) )
        self.tabWidget.insertTab( 0, valueEditor, 'Value' )
        self.tabWidget.setCurrentIndex( 0 )

    @updateModelPlus
    def editValue( self, value ):
        valueText = str( value )
        if callable( value ):
            valueText += ' (callable)'
        self.valueEditor.setText( valueText )
        self.component.value = value

class GlobalDialog( InputDialog ):
    """
    Be sure to update the GlobalsModel singleton when we edit a global
    """
    def __init__( self, parent, component ):
        super( GlobalDialog, self ).__init__( parent, component )
    def cleanUp( self ):
        GlobalsModel().updateGlobal( self.component )

class MapDialog( NamedInputDialog ):
    def __init__( self, parent, component ):
        super( MapDialog, self ).__init__( parent, component )
        self.tabWidget.insertTab( 0, FunctionEditorUpdater( component, 'Mapping function', self ), 'Map' )
        self.tabWidget.setCurrentIndex( 0 )
