'''
Dialog that allows selection of functions from function/labrad setting browsers
'''
import types

from PyQt4 import QtGui, QtCore
from ..functionbrowser import FunctionBrowser, FunctionModel, IFunctionModelItem
from ..labradbrowser import LabradModel
from ..view import TreeWidget

from ...lr import LabradSetting

class BaseFunctionDialog( QtGui.QDialog ):
    def __init__( self, parent, model, title ):
        super( BaseFunctionDialog, self ).__init__( parent )
        layout = QtGui.QVBoxLayout( self )

        self.view = view = FunctionBrowser()
        self.model = model
        view.setModel( model )
        view.doubleClicked.connect( lambda index: self.itemSelected( model.itemFromIndex( index ) ) )
        treeWidget = TreeWidget( view, title )
        refresh = treeWidget.addButton( 'Refresh' )
        refresh.clicked.connect( model.refresh )
        showInfo = treeWidget.addButton( 'Show Info' )
        showInfo.setToolTip( 'Or press Space Bar on an item' )
        showInfo.clicked.connect( view.showInfo )
        layout.addWidget( treeWidget )

    def addFunctionModelItem( self, obj ):
        self.model.appendRow( IFunctionModelItem( obj ) )

    def itemSelected( self, item ): pass

class FunctionDialog( BaseFunctionDialog ):
    functionSelected = QtCore.pyqtSignal( types.FunctionType )
    builtinFunctionSelected = QtCore.pyqtSignal( types.BuiltinFunctionType )
    def __init__( self, parent, title = 'Function Browser' ):
        super( FunctionDialog, self ).__init__( parent, FunctionModel(), title )

    def itemSelected( self, item ):
        if item.type is FunctionModel.FUNCTION:
            self.functionSelected.emit( item.object )
        if item.type is FunctionModel.BUILTIN:
            self.builtinFunctionSelected.emit( item.object )

class LabradDialog( BaseFunctionDialog ):
    labradSettingSelected = QtCore.pyqtSignal( LabradSetting )
    def __init__( self, parent ):
        super( LabradDialog, self ).__init__( parent, LabradModel(), 'LabRAD Browser' )
    def itemSelected( self, item ):
        if item.type is LabradModel.OVERLOAD:
            self.labradSettingSelected.emit( item.object )
