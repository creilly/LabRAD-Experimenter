'''
Edit dialogs for components that contain a group of other components
'''
from PyQt4 import QtGui, QtCore

from . import ComponentEditDialog
from ..componentreorder import ComponentReorderList
from ..inputselector import InputSelector
from ..reorderlist import ReorderWidget
from ..component import updateModel

from ...components import ScanRange, ArgumentList

class ComponentGroupModeDialog( ComponentEditDialog ):
    def __init__( self, parent, component, modes, title ):
        super( ComponentGroupModeDialog, self ).__init__( parent, component, title )

        modeSelector = QtGui.QButtonGroup( self )
        modeSelectorWidget = QtGui.QGroupBox( 'Mode select' )
        modeSelectorWidget.setLayout( QtGui.QHBoxLayout() )

        for name, id, toolTip in modes:
            radio = QtGui.QRadioButton( name )
            radio.setToolTip( toolTip )
            modeSelector.addButton( radio, id )
            modeSelectorWidget.layout().addWidget( radio )

        modeSelector.buttonClicked[int].connect( self.modeSelected )
        modeSelector.buttonClicked[int].connect( self.setToolbar )

        reorderModel = self.reorderModel = ComponentReorderList( component.components )
        reorderModel.addItem = self.addItem
        self.reorderWidget = ReorderWidget( reorderModel )

        self.setToolbar( component.mode )
        modeSelector.button( component.mode ).setChecked( True )

        widget = QtGui.QWidget()
        widget.setLayout( QtGui.QVBoxLayout() )

        widget.layout().addWidget( self.reorderWidget, 1 )
        widget.layout().addWidget( modeSelectorWidget )

        self.tabWidget.insertTab( 0, widget, 'Components' )
        self.tabWidget.setCurrentIndex( 0 )

    @updateModel
    def addItem( self ):
        inputSelector = InputSelector( self )
        inputSelector.inputSelected.connect( self.newInput )
        inputSelector.exec_()
        inputSelector.deleteLater()

    def newInput( self, input ): pass

    def modeSelected( self, id ): pass
    def setToolbar( self, id ): pass

class ArgumentListDialog( ComponentGroupModeDialog ):
    def __init__( self, parent, component ):
        super( ArgumentListDialog, self ).__init__( parent,
                                                    component,
                                                    ( ( 'MONO', ArgumentList.MONO, 'Single input whose value is a collection' ), ( 'POLY', ArgumentList.POLY, 'Collection of inputs' ) ),
                                                    'Argument List' )

    def setToolbar( self, id ):
        rw = self.reorderWidget
        rw.ADD = True
        rw.RAISE = rw.LOWER = rw.REMOVE = False if id is ArgumentList.MONO else True

    @updateModel
    def modeSelected( self, id ):
        rm = self.reorderModel
        nullIndex = QtCore.QModelIndex()
        l = len( rm.pyList )
        newL = 1 if id is ArgumentList.MONO else 0
        if l > newL:
            rm.beginRemoveRows( nullIndex, newL, l - 1 )
            self.component.setMode( id )
            rm.endRemoveRows()
        if l < newL:
            rm.beginInsertRows( nullIndex, l, newL - 1 )
            self.component.setMode( id )
            rm.endInsertRows()
        if l is newL:
            self.component.setMode( id )
        if newL:
            rm.dataChanged.emit( rm.index( 0 ), rm.index( newL - 1 ) )

    @updateModel
    def newInput( self, input ):
        rm = self.reorderModel
        if self.component.mode is ArgumentList.MONO:
            rm.pyList[0] = input
            rm.dataChanged.emit( rm.index( 0 ), rm.index( 0 ) )
        if self.component.mode is ArgumentList.POLY:
            rm.appendObject( input )



class ScanRangeDialog( ComponentGroupModeDialog ):
    def __init__( self, parent, component ):
        super( ScanRangeDialog, self ).__init__( parent,
                                                 component,
                                                 ( ( 'DELTA', ScanRange.DELTA, 'Specify start, end, and the size of the spacings' ),
                                                   ( 'STEPS', ScanRange.STEPS, 'Specify start, end, and number of steps in between' ),
                                                   ( 'COLLECTION', ScanRange.COLLECTION, 'Collection of inputs' ),
                                                   ( 'LIST' , ScanRange.LIST, 'Single input whose value is a collection' ) ),
                                                   'Scan Range' )

    def setToolbar( self, id ):
        rw = self.reorderWidget
        if id is not ScanRange.LIST:
            rw.raiseEnabled = rw.lowerEnabled = rw.removeEnabled = rw.addEnabled = True if id is ScanRange.COLLECTION else False
        else:
            rw.raiseEnabled = rw.lowerEnabled = rw.removeEnabled = False
            rw.addEnabled = True
    @updateModel
    def modeSelected( self, id ):
        rm = self.reorderModel
        nullIndex = QtCore.QModelIndex()
        l = len( rm.pyList )
        if id is ScanRange.COLLECTION:
            newL = 0
        if id is ScanRange.LIST:
            newL = 1
        else:
            newL = 3
        if l < newL:
            rm.beginInsertRows( nullIndex, l, newL - 1 )
            self.component.setMode( id )
            rm.endInsertRows()
        if l > newL:
            rm.beginRemoveRows( nullIndex, newL, l - 1 )
            self.component.setMode( id )
            rm.endRemoveRows()
        if l is newL:
            self.component.setMode( id )
        if newL:
            rm.dataChanged.emit( rm.index( 0, 0 ), rm.index( 0, newL - 1 ) )

    @updateModel
    def newInput( self, input ):
        rm = self.reorderModel
        if self.component.mode is ScanRange.COLLECTION:
            rm.appendObject( input )
        if self.component.mode is ScanRange.LIST:
            rm.pyList[0] = input
            rm.dataChanged.emit( rm.index( 0, 0 ), rm.index( 0, 0 ) )
