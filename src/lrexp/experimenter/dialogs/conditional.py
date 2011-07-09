from PyQt4 import QtGui
from . import UnitDialog
from unit import UnitSelectorWidget
from ..view import TreeView, TreeWidget
from ..component import updateModel, BaseComponentModel

class ConditionalDialog( UnitDialog ):
    TRUE = True
    FALSE = False
    def __init__( self, parent, component ):
        super( ConditionalDialog, self ).__init__( parent, component )

        def newUnitSetter( unit, model ):
            @updateModel
            def setNewUnit( newUnit ):
                unit.component = newUnit
                model.setRoot( newUnit )
            return setNewUnit

        for unitType in ( self.TRUE, self.FALSE ):
            label = component.trueUnit if unitType else component.falseUnit
            unit = label.component
            model = BaseComponentModel()
            model.setRoot( unit )
            unitSelector = UnitSelectorWidget( component )
            unitSelector.unitSelected.connect( newUnitSetter( label, model ) )
            view = TreeView()
            view.setModel( model )

            widget = QtGui.QWidget()
            layout = QtGui.QVBoxLayout( widget )
            layout.addWidget( unitSelector )
            name = '%s Unit' % repr( unitType )
            layout.addWidget( TreeWidget( view, name ) )
            self.tabWidget.insertTab( 0 if unitType else 1, widget, name )

        self.tabWidget.setCurrentIndex( 0 )
