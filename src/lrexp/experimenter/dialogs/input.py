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
from ..component import ComponentModel, updateModel
from ..globals import GlobalsModel

from ...components import Result, Global

class BaseInputDialog( ComponentEditDialog ):
    def __init__( self, parent, component ):
        super( BaseInputDialog, self ).__init__( parent, component, 'Edit %s' % component.__class__.__name__ )

        inputView = TreeView()
        inputView.setModel( ComponentModel() )
        colorDelegate = self.colorDelegate = BaseColorDelegate()
        colorDelegate.addMatchColor( component, 'red' )
        inputView.setItemDelegate( colorDelegate )
        treeWidget = self.treeWidget = TreeWidget( inputView )

        self.inputCycler = treeWidget.addCycler( 'Next match', [item.index() for item in ComponentModel().getItemsFromComponent( component )] )

        descriptionEditor = TextEditor( 'Description', 'Enter new description' )
        descriptionEditor.setText( component.description )
        @updateModel
        def editDescription( description ):
            descriptionEditor.setText( description )
            component.description = description
            self.updateModels()

        descriptionEditor.editCreated.connect( lambda edit: editDescription( edit.value ) )

        self.tabWidget.addTab( descriptionEditor, 'Description' )
        self.tabWidget.addTab( treeWidget, 'View' )

        ComponentModel().endUpdate.connect( self.modelUpdated )

    def modelUpdated( self ):
        self.inputCycler.setIndexes( [item.index() for item in ComponentModel().getItemsFromComponent( self.component )] )

class ResultDialog( BaseInputDialog ):
    def __init__( self, parent, component ):
        super( ResultDialog, self ).__init__( parent, component )
        self.resultCycler = self.treeWidget.addCycler( 'Goto Action', [item.index() for item in ComponentModel().getItemsFromComponent( self.component.parentAction )] )
        self.colorDelegate.addMatchColor( component.parentAction, 'blue' )
    def modelUpdated( self ):
        super( ResultDialog, self ).modelUpdated()
        self.resultCycler.setIndexes( [item.index() for item in ComponentModel().getItemsFromComponent( self.component.parentAction )] )
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
