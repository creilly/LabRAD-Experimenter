from PyQt4 import QtGui
from . import UnitDialog
from unit import UnitSelectorWidget
from ..view import TreeView, TreeWidget
from ..component import ColorComponentModel, updateModel, DontUpdate
from ...components import Input

class ScanDialog( UnitDialog ):
    """
    Widgets to view and set both the scanInput and scanUnit
    """
    def __init__( self, parent, component ):
        super( ScanDialog, self ).__init__( parent, component )

        treeTab = QtGui.QWidget()

        treeLayout = QtGui.QVBoxLayout( treeTab )

        unitSelector = UnitSelectorWidget( component )
        unitSelector.unitSelected.connect( self.setScanUnit )

        tree = self.tree = TreeView()
        tree.setModel( ColorComponentModel() )
        tree.model().setRoot( component.scanUnit )
        self.colorCondition = tree.model().addColorCondition( component.scanInput, 'red', QtGui.QFont.Bold )
        tree.doubleClicked.connect( lambda index: self.setScanInput( tree.model().itemFromIndex( index ).component ) )
        treeWidget = self.treeWidget = TreeWidget( tree )
        self.cycler = tree.model().addCycler( tree, component.scanInput, treeWidget.addButton( 'Scan Input' ) )
        self.cycler.button.setToolTip( 'Double click or press Enter on another Input to change' )

        treeLayout.addWidget( unitSelector )
        treeLayout.addWidget( treeWidget )

        self.tabWidget.insertTab( 0, treeTab, 'Scan Unit/Input' )
        self.tabWidget.setCurrentIndex( 0 )

    @updateModel
    def setScanUnit( self, unit ):
        self.component.scanUnit = unit
        model = self.tree.model()
        model.clear()
        model.setRoot( unit )
        self.treeWidget.setTitle( 'Scan Unit: <i>%s</i>' % repr( unit ) )
        self.setScanInput( Input( None ) )

    @updateModel
    def setScanInput( self, input ):
        if type( input ) is not Input: raise DontUpdate
        self.component.scanInput = input
        self.cycler.setCondition( input )
        self.colorCondition.setCondition( input )
        self.cycler.next()
