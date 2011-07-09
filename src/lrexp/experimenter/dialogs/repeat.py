from PyQt4 import QtGui
from . import UnitDialog
from unit import UnitSelectorWidget
from ..view import TreeView, TreeWidget
from ..component import updateModel, BaseComponentModel
class RepeatDialog( UnitDialog ):
    """
    Widgets to view and set the repeatUnit
    """
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
