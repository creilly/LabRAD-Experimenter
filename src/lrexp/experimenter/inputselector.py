'''
Provides a way for components to access inputs from the root tree, clip board, or make new ones.
'''
from PyQt4 import QtGui, QtCore

from component import ComponentModel
from clipboard import ClipBoardBrowser
from view import TreeView, TreeWidget
from globals import GlobalsListWidget

from ..components import Input, Map
from lrexp.experimenter.component import ColorComponentModel

class InputSelector( QtGui.QDialog ):

    inputSelected = QtCore.pyqtSignal( Input )

    def __init__( self, parent, referenceComponent = None ):
        super( InputSelector, self ).__init__( parent )
        self.setLayout( QtGui.QHBoxLayout() )

        optionsView = QtGui.QComboBox()

        optionsModel = QtGui.QStandardItemModel()

        for name, selector in ( ( 'New Input', NewInput() ) ,
                                ( 'Old Input', OldInput( self, referenceComponent ) ),
                                ( 'Global', Global( self ) ),
                                ( 'Map', NewMap() ),
                                ( 'Clip board', ClipBoard( self, parent.component ) ) ):
            optionsModel.appendRow( OptionsItem( name, selector ) )
            selector.inputSelected.connect( self.inputSelected.emit )


        optionsView.setModel( optionsModel )

        optionsActivate = QtGui.QPushButton( 'Get' )
        optionsActivate.clicked.connect( lambda: optionsModel.item( optionsView.currentIndex() ).selector.getInput() if optionsView.currentIndex() >= 0 else None )

        self.inputSelected.connect( lambda input: self.accept() )

        self.layout().addWidget( optionsView, 1 )
        self.layout().addWidget( optionsActivate )

class OptionsItem( QtGui.QStandardItem ):
    def __init__( self, name, selector ):
        super( OptionsItem, self ).__init__()
        self.setData( name, QtCore.Qt.DisplayRole )
        self.selector = selector

class BaseInputSelector( QtCore.QObject ):
    inputSelected = QtCore.pyqtSignal( Input )
    def getInput( self ):
        pass

class NewInput( BaseInputSelector ):
    def getInput( self ):
        self.inputSelected.emit( Input( None ) )

class NewMap( BaseInputSelector ):
    def getInput( self ):
        self.inputSelected.emit( Map() )

class OldInput( BaseInputSelector ):
    def __init__( self, parent, referenceComponent = None ):
        super( OldInput, self ).__init__( parent )

        self.selectedInput = None

        dialog = self.dialog = QtGui.QDialog( self.parent() )
        dialog.setLayout( QtGui.QVBoxLayout() )

        tree = TreeView()
        treeWidget = TreeWidget( tree, 'Get existing input' )
        model = ColorComponentModel()
        model.setRoot( ComponentModel().rootComponent )

        isInput = lambda comp: isinstance( comp, Input )
        model.addColorCondition( isInput , 'red', QtGui.QFont.Bold )
        model.addCycler( tree, isInput, treeWidget.addButton( 'Next' ) )
        if referenceComponent:
            model.insertColorCondition( 0, referenceComponent, 'blue', QtGui.QFont.Bold )
            cycler = model.addCycler( tree, referenceComponent, treeWidget.addButton( 'Current input' ) )
            for i in range( len( cycler.items ) ):
                cycler.next()

        tree.setModel( model )

        def itemSelected( component ):
            if isinstance( component, Input ):
                self.selectedInput = component
                dialog.accept()

        tree.doubleClicked.connect( lambda index: itemSelected( model.itemFromIndex( index ).component ) )

        dialog.layout().addWidget( treeWidget )

    def getInput( self ):

        self.selectedInput = None

        self.dialog.exec_()

        if self.selectedInput:
            self.inputSelected.emit( self.selectedInput )

class Global( BaseInputSelector ):
    def __init__( self, parent ):
        super( Global, self ).__init__()
        dialog = self.dialog = QtGui.QDialog( parent )
        dialog.setLayout( QtGui.QVBoxLayout() )

        self.selectedGlobal = None

        def globalSelected( globalInput ):
            self.selectedGlobal = globalInput
            dialog.accept()

        widget = GlobalsListWidget()
        widget.globalSelected.connect( globalSelected )

        dialog.layout().addWidget( widget )

    def getInput( self ):
        self.selectedGlobal = None
        self.dialog.exec_()
        if self.selectedGlobal:
            self.inputSelected.emit( self.selectedGlobal )

class ClipBoard( BaseInputSelector ):
    def __init__( self, parent, component ):
        super( ClipBoard, self ).__init__( parent )
        self.component = component

    def getInput( self ):
        clipBoardBrowser = ClipBoardBrowser()
        clipBoardBrowser.condition = lambda component: isinstance( component, Input ) and clipBoardBrowser.isLoopFree( component, self.component )
        component = clipBoardBrowser.getComponent()
        if component:
            self.inputSelected.emit( component )


