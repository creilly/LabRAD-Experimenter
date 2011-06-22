'''
Created on Apr 27, 2011

@author: christopherreilly
'''
import yaml, types

from PyQt4 import QtGui
from . import ComponentEditDialog
from ..editor import TextEditor, ValueEditor, FunctionEditorUpdater
from ..view import TreeView, TreeWidget
from ..delegate import BaseColorDelegate
from ..component import ComponentModel
from ..globals import GlobalsModel

from ...components import Result, Global

class BaseInputDialog( ComponentEditDialog ):
    def __init__( self, parent, component ):
        super( BaseInputDialog, self ).__init__( parent, component, 'Edit %s' % component.__class__.__name__ )

        inputView = TreeView()
        inputView.setModel( ComponentModel() )
        colorDelegate = BaseColorDelegate()
        colorDelegate.addMatchColor( component, 'red' )
        inputView.setItemDelegate( colorDelegate )
        treeWidget = TreeWidget( inputView )

        treeWidget.addCycler( 'Next match', [item.index() for item in ComponentModel().getItemsFromComponent( component )] )

        if type( component ) is Result:
            treeWidget.addCycler( 'Goto Action', [item.index() for item in ComponentModel().getItemsFromComponent( component.parentAction )] )
            colorDelegate.addMatchColor( component.parentAction, 'blue' )

        descriptionEditor = TextEditor( 'Description', 'Enter new description' )
        descriptionEditor.setText( component.description )
        def editDescription( description ):
            descriptionEditor.setText( description )
            component.description = description
            self.updateModels()

        descriptionEditor.editCreated.connect( lambda edit: editDescription( edit.value ) )

        self.tabWidget.addTab( descriptionEditor, 'Description' )
        self.tabWidget.addTab( treeWidget, 'View' )

    def updateModels( self ):
        ComponentModel().update()
        if type( self.component ) is Global:
            GlobalsModel().updateGlobal( self.component )

class InputDialog( BaseInputDialog ):

    def __init__( self, parent, component ):
        super( InputDialog, self ).__init__( parent, component )
        try:
            default = yaml.dump( component.value )
        except:
            default = ''
        valueEditor = ValueEditor( 'Value', default = default )
        valueEditor.setText( repr( component.value ) )
        def editValue( value ):
            valueText = repr( value )
            if callable( value ):
                valueText += ' (callable)'
            valueEditor.setText( valueText )
            component.value = value
            self.updateModels()
        valueEditor.editCreated.connect( lambda edit: editValue( edit.value ) )
        self.tabWidget.insertTab( 0, valueEditor, 'Value' )
        self.tabWidget.setCurrentIndex( 0 )

class GlobalDialog( InputDialog ):

    def __init__( self, parent, component ):
        super( GlobalDialog, self ).__init__( parent, component )
        nameEditor = TextEditor( 'Name', 'Enter new Global name' )
        nameEditor.setText( repr( component.name ) )
        def editName( name ):
            nameEditor.setText( name )
            component.name = name
            self.updateModels()
        nameEditor.editCreated.connect( lambda edit: editName( edit.value ) )
        self.tabWidget.insertTab( 1, nameEditor, 'Name' )

class MapDialog( BaseInputDialog ):
    def __init__( self, parent, component ):
        super( MapDialog, self ).__init__( parent, component )
        self.tabWidget.insertTab( 0, FunctionEditorUpdater( component, 'Mapping function', self ), 'Map' )
        self.tabWidget.setCurrentIndex( 0 )

class ResultDialog( BaseInputDialog ): pass
