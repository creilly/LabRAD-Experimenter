from __future__ import with_statement

from PyQt4 import QtGui, QtCore

from zope.interface import Interface, implements

from filedialog import getFileDialog
from ..editor import Editor, TextEditor
from ..component import ComponentModel, updateModel
from ..reorderlist import IReorderList
from ..view import BaseListView

from ...components import Action, Scan, Sequence, Repeat, Conditional, Unit
from ...util import loadUnit

class ComponentEditDialog( QtGui.QDialog ):

    class Title( QtGui.QLabel ):
        def setTitle( self, title ):
            self.setText( '<big><b>%s</b></big>' % title )

    def __init__( self, parent, component, title ):
        super( ComponentEditDialog, self ).__init__( parent )
        self.component = component
        self.setLayout( QtGui.QVBoxLayout() )
        self.title = self.Title()
        self.title.setTitle( title )
        self.tabWidget = QtGui.QTabWidget()
        self.layout().addWidget( self.title )
        self.layout().addWidget( self.tabWidget, 1 )


class UnitDialog( ComponentEditDialog ):
    def __init__( self, parent, component ):
        super( UnitDialog, self ).__init__( parent, component, 'Edit %s: <i>%s</i>' % ( type( component ).__name__, component.name ) )

        nameEdit = self.nameEdit = TextEditor( 'Edit name', 'Enter new unit name' )
        nameEdit.editCreated.connect( lambda edit: self.newUnitName( edit.value ) )
        nameEdit.setText( component.name )

        self.tabWidget.addTab( nameEdit, 'Name' )

        self.layout().addWidget( self.tabWidget, 1 )

    def newUnitName( self, name ):
        self.component.name = name
        ComponentModel().update()
        self.nameEdit.setText( name )
        self.title.setTitle( 'Edit %s: <i>%s</i>' % ( type( self.component ).__name__, name ) )


class NewUnitDialog( QtGui.QDialog ):
    unitDict = {
                'Action':Action,
                'Scan':Scan,
                'Sequence':Sequence,
                'Repeat':Repeat,
                'Conditional':Conditional
                }
    def __init__( self ):
        super( NewUnitDialog, self ).__init__()

        nameEdit = self.nameEdit = QtGui.QLineEdit( 'untitled' )

        unitType = self.unitType = QtGui.QComboBox()

        for key in self.unitDict:
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
        if not unit: return
        self.unitSelected.emit( unit )

    def load( self ):
        fd = self.fileDialog
        fd.setAcceptMode = fd.AcceptOpen
        fd.setWindowTitle( 'Load root unit' )
        if fd.exec_():
            unit = loadUnit( str( fd.selectedFiles()[0] ) )
            self.unitSelected.emit( unit )

    def clipBoard( self ):
        print 'accessing clipboard'

def getUnit():
    d = QtGui.QDialog()
    d.unit = None
    d.setLayout( QtGui.QVBoxLayout() )
    unitSelector = UnitSelectorWidget()

    def unitSelected( selectedUnit ):
        d.unit = selectedUnit
        d.accept()

    unitSelector.unitSelected.connect( unitSelected )

    d.layout().addWidget( unitSelector )
    if d.exec_() and d.unit:
        return d.unit
    return None


class ComponentReorderList( QtCore.QAbstractListModel ):
    """
    Takes in a python list and a Qt view.  View must implement currentIndex().
    """
    implements( IReorderList )
    def __init__( self, pyList ):
        super( ComponentReorderList, self ).__init__()
        self.pyList = pyList
        self.view = self.widget = BaseListView()
        self.view.setModel( self )
    def rowCount( self, parent = QtCore.QModelIndex() ):
        if not parent.isValid():
            return len( self.pyList )
        return 0
    def data( self, index, role ):
        if not index.isValid(): return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            return repr( self.pyList[index.row()] )
        return QtCore.QVariant()
    def getRow( self ):
        index = self.view.currentIndex()
        if not index.isValid(): return None
        return index.row()
    @updateModel
    def raiseItem( self ):
        row = self.getRow()
        if row is None or row is 0: return
        self.pyList[row], self.pyList[row - 1] = self.pyList[row - 1], self.pyList[row]
        self.dataChanged.emit( self.index( row - 1, 0 ), self.index( row, 0 ) )
        self.view.setCurrentIndex( self.index( row - 1 ) )
    @updateModel
    def lowerItem( self ):
        row = self.getRow()
        if row is None or row + 1 >= len( self.pyList ): return
        self.pyList[row], self.pyList[row + 1] = self.pyList[row + 1], self.pyList[row]
        self.dataChanged.emit( self.index( row, 0 ), self.index( row + 1, 0 ) )
        self.view.setCurrentIndex( self.index( row + 1 ) )
    @updateModel
    def removeItem( self ):
        row = self.getRow()
        if row is None: return
        self.beginRemoveRows( QtCore.QModelIndex(), row, row )
        self.pyList.pop( row )
        self.endRemoveRows()
    @updateModel
    def addItem( self ):
        pass

    @updateModel
    def removeAll( self ):
        self.beginRemoveRows( QtCore.QModelIndex(), 0, len( self.pyList ) - 1 )
        while self.pyList: self.pyList.pop()
        self.endRemoveRows()

    def appendObject( self, obj ):
        l = len( self.pyList )
        self.beginInsertRows( QtCore.QModelIndex(), l, l )
        self.pyList.append( obj )
        self.endInsertRows()


