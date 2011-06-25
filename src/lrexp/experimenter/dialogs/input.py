'''
Created on Apr 27, 2011

@author: christopherreilly
'''
import yaml, types

from PyQt4 import QtGui
from . import ComponentEditDialog
from ..editor import TextEditor, ValueEditor, FunctionEditorUpdater
from ..view import TreeView, TreeWidget
from ..component import ComponentModel, updateModel, ColorComponentModel
from ..globals import GlobalsModel

class BaseInputDialog( ComponentEditDialog ):
    def __init__( self, parent, component ):
        super( BaseInputDialog, self ).__init__( parent, component, 'Edit %s' % component.__class__.__name__ )

        inputView = self.inputView = TreeView()
        model = self.model = ColorComponentModel()

        model.setRoot( ComponentModel().rootComponent )

        inputView.setModel( model )

        treeWidget = self.treeWidget = TreeWidget( inputView )

        model.addCycler( inputView, component, treeWidget.addButton( 'Next match' ) )
        model.addColorCondition( component, 'red', QtGui.QFont.Bold )

        descriptionEditor = TextEditor( 'Description', 'Enter new description' )
        descriptionEditor.setText( component.description )
        @updateModel
        def editDescription( description ):
            descriptionEditor.setText( description )
            component.description = description

        descriptionEditor.editCreated.connect( lambda edit: editDescription( edit.value ) )

        self.tabWidget.addTab( descriptionEditor, 'Description' )
        self.tabWidget.addTab( treeWidget, 'View' )

        ComponentModel().endUpdate.connect( model.update )

class ResultDialog( BaseInputDialog ):
    def __init__( self, parent, component ):
        super( ResultDialog, self ).__init__( parent, component )
        self.model.addCycler( self.inputView, component.parentAction, self.treeWidget.addButton( 'Result Action' ) )

class InputDialog( BaseInputDialog ):
    def __init__( self, parent, component ):
        super( InputDialog, self ).__init__( parent, component )
        try:
            default = yaml.dump( component.value )
        except:
            default = ''
        valueEditor = ValueEditor( 'Value', default = default )
        valueEditor.setText( repr( component.value ) )
        @updateModel
        def editValue( value ):
            valueText = repr( value )
            if callable( value ):
                valueText += ' (callable)'
            valueEditor.setText( valueText )
            component.value = value
        valueEditor.editCreated.connect( lambda edit: editValue( edit.value ) )
        self.tabWidget.insertTab( 0, valueEditor, 'Value' )
        self.tabWidget.setCurrentIndex( 0 )

class GlobalDialog( InputDialog ):

    def __init__( self, parent, component ):
        super( GlobalDialog, self ).__init__( parent, component )
        nameEditor = TextEditor( 'Name', 'Enter new Global name' )
        nameEditor.setText( repr( component.name ) )
        @updateModel
        def editName( name ):
            nameEditor.setText( name )
            component.name = name
        nameEditor.editCreated.connect( lambda edit: editName( edit.value ) )
        self.tabWidget.insertTab( 1, nameEditor, 'Name' )

    def modelUpdated( self ):
        super( GlobalDialog, self ).modelUpdated()
        GlobalsModel().updateGlobal( self.component )

class MapDialog( BaseInputDialog ):
    def __init__( self, parent, component ):
        super( MapDialog, self ).__init__( parent, component )
        self.tabWidget.insertTab( 0, FunctionEditorUpdater( component, 'Mapping function', self ), 'Map' )
        self.tabWidget.setCurrentIndex( 0 )
