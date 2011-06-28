'''
Created on Jun 27, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui
from . import UnitDialog, UnitSelectorWidget
from ..view import TreeView, TreeWidget
from ..component import updateModel, BaseComponentModel
class RepeatDialog( UnitDialog ):
    def __init__( self, parent, component ):
        super( RepeatDialog, self ).__init__( parent, component )

        model = BaseComponentModel()
        model.setRoot( component.repeatUnit )

        @updateModel
        def setNewUnit( unit ):
            component.repeatUnit = unit
            model.setRoot( unit )

        unitSelector = UnitSelectorWidget( component )
        unitSelector.unitSelected.connect( setNewUnit )

        view = TreeView()
        view.setModel( model )

        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout( widget )
        layout.addWidget( unitSelector )
        name = 'Repeat Unit'
        layout.addWidget( TreeWidget( view, name ) )
        self.tabWidget.insertTab( 0, widget, name )
        self.tabWidget.setCurrentIndex( 0 )
