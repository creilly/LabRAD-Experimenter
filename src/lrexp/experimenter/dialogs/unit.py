'''
Dialogs and functions to create new units, load old ones from file, and select existing units from the clip board.
'''
from PyQt4 import QtGui, QtCore

from filedialog import getFileDialog
from ..clipboard import ClipBoardBrowser
from ...components import Action, Scan, Sequence, Repeat, Conditional, NullUnit, IUnit, Unit
from ...util import loadUnit

class NewUnitDialog( QtGui.QDialog ):
    unitDict = {
                'Action':Action,
                'Scan':Scan,
                'Sequence':Sequence,
                'Repeat':Repeat,
                'Conditional':Conditional,
                'Null':NullUnit
                }
    def __init__( self ):
        super( NewUnitDialog, self ).__init__()

        nameEdit = self.nameEdit = QtGui.QLineEdit( 'untitled' )

        unitType = self.unitType = QtGui.QComboBox()

        for key in sorted( self.unitDict ):
            unitType.addItem( key )

        buttonLayout = QtGui.QHBoxLayout()

        cancel = QtGui.QPushButton( 'Cancel' )
        cancel.clicked.connect( self.reject )
        create = QtGui.QPushButton( 'Create' )
        create.clicked.connect( self.accept )
        create.setDefault( True )

        buttonLayout.addStretch()
        buttonLayout.addWidget( cancel )
        buttonLayout.addWidget( create )

        layout = QtGui.QFormLayout( self )
        layout.addRow( QtGui.QLabel( '<big><b>New Unit</b></big>' ) )
        layout.addRow( 'Unit name', nameEdit )
        layout.addRow( 'Unit type', unitType )
        layout.addRow( buttonLayout )

def getNewUnit():
    newUnitD = NewUnitDialog()
    return newUnitD.unitDict[str( newUnitD.unitType.currentText() )]( str( newUnitD.nameEdit.text() ) ) if newUnitD.exec_() else None

class UnitSelectorWidget( QtGui.QGroupBox ):
    unitSelected = QtCore.pyqtSignal( Unit )
    def __init__( self, referenceUnit = None ):
        super( UnitSelectorWidget, self ).__init__( 'Get Unit' )

        layout = QtGui.QHBoxLayout( self )

        new = QtGui.QPushButton( 'New' )
        new.clicked.connect( self.new )

        load = QtGui.QPushButton( 'Old' )
        load.clicked.connect( self.load )

        clipBoard = QtGui.QPushButton( 'Clip board' )
        clipBoard.clicked.connect( self.clipBoard )

        layout.addWidget( new )
        layout.addWidget( load )
        layout.addWidget( clipBoard )
        layout.addStretch()

        self.fileDialog = getFileDialog( self )
        self.fileDialog.setAcceptMode( QtGui.QFileDialog.AcceptOpen )
        self.referenceUnit = referenceUnit

    def new( self ):
        unit = getNewUnit()
        if unit is None: return
        self.unitSelected.emit( unit )

    def load( self ):
        fd = self.fileDialog
        fd.setAcceptMode = fd.AcceptOpen
        fd.setWindowTitle( 'Load root unit' )
        if fd.exec_():
            unit = loadUnit( str( fd.selectedFiles()[0] ) )
            self.unitSelected.emit( unit )

    def clipBoard( self ):
        clipBoardBrowser = ClipBoardBrowser()
        clipBoardBrowser.condition = lambda component: IUnit.providedBy( component ) and ( clipBoardBrowser.isLoopFree( component, self.referenceUnit ) if self.referenceUnit else True )
        result = clipBoardBrowser.getComponent()
        if result:
            self.unitSelected.emit( result )

def getUnit( referenceUnit = None ):
    d = QtGui.QDialog()
    d.unit = None
    d.setLayout( QtGui.QVBoxLayout() )
    unitSelector = UnitSelectorWidget( referenceUnit )

    def unitSelected( selectedUnit ):
        d.unit = selectedUnit
        d.accept()

    unitSelector.unitSelected.connect( unitSelected )

    d.layout().addWidget( unitSelector )
    if d.exec_() and d.unit:
        return d.unit
    return None
