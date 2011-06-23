'''
Created on Apr 27, 2011

@author: christopherreilly
'''
from PyQt4 import QtCore, QtGui
from ..components import Global
from reorderlist import ReorderWidget, IReorderList

from zope.interface import implements
from twisted.python import components

import yaml

instance = None
class GlobalsModel( QtCore.QAbstractTableModel ):

    instance = None
    globalsEdited = QtCore.pyqtSignal()
    globalRemoved = QtCore.pyqtSignal( Global )
    globals = []

    def __new__( cls ):
        global instance
        if instance is not None:
            return instance
        instance = super( GlobalsModel, cls ).__new__( cls )
        super( GlobalsModel, cls ).__init__( instance )
        return instance

    def __init__( self ):
        pass

    def rowCount( self, parent = None ):
        if not parent.isValid():
            return len( self.globals )
        return 0
    def columnCount( self, parent = None ):
        if not parent.isValid():
            return 3
        return 0
    def data( self, index, role ):
        if not index.isValid(): return QtCore.QVariant()
        row, column = index.row(), index.column()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            globalInput = self.globals[row]
            if column is 0:
                return globalInput.name
            if column is 1:
                value = globalInput.value
                return str( value ) if role == QtCore.Qt.DisplayRole else yaml.dump( value )
            if column is 2:
                return globalInput.description
        return QtCore.QVariant()
    def flags( self, index ):
        if index.isValid(): return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        return QtCore.Qt.NoItemFlags
    def setData( self, index, data, role ):
        if not index.isValid() or role != QtCore.Qt.EditRole: return False
        row, column = index.row(), index.column()
        globalInput = self.globals[row]
        data = str( data.toString() )
        if column is 0:
            globalInput.name = data
        if column is 1:
            try:
                globalInput.value = yaml.load( data )
            except:
                return False
        if column is 2:
            globalInput.description = data
        self.dataChanged.emit( index, index )
        self.globalsEdited.emit()
        return True
    def headerData( self, section, orientation, role ):
        nullValue = QtCore.QVariant()
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole: return ( 'Name', 'Value', 'Description' )[section]
            if role == QtCore.Qt.ToolTipRole: return ( nullValue, 'Yaml string', nullValue )[section]
        return nullValue
    def addGlobal( self, globalInput = None ):
        curLen = len( self.globals )
        self.beginInsertRows( QtCore.QModelIndex(), curLen, curLen )
        self.globals.append( globalInput if globalInput else Global( 'Unnamed' ) )
        self.endInsertRows()
    def newRoot( self ):
        self.beginRemoveRows( QtCore.QModelIndex(), 0, len( self.globals ) - 1 )
        self.globals = []
        self.endRemoveRows()
    def updateGlobal( self, globalInput ):
        row = self.globals.index( globalInput )
        self.dataChanged.emit( self.index( row, 0 ), self.index( row, 2 ) )

class GlobalsReorder( object ):
    implements( IReorderList )
    def __init__( self, globalsModel ):
        globalsTable = self.widget = QtGui.QTableView()
        self.model = globalsModel
        globalsTable.setModel( globalsModel )
        globalsTable.horizontalHeader().setStretchLastSection( True )
        globalsTable.verticalHeader().hide()
        globalsTable.setCornerButtonEnabled( False )

    def getRow( self ):
        index = self.widget.currentIndex()
        if not index.isValid(): return None
        return index.row()
    def raiseItem( self ):
        row = self.getRow()
        if row is None or row is 0: return
        model = self.model
        model.globals[row], model.globals[row - 1] = model.globals[row - 1], model.globals[row]
        model.dataChanged.emit( model.index( row - 1, 0 ), model.index( row, 1 ) )
        self.widget.setCurrentIndex( self.widget.setCurrentIndex( model.index( row - 1 ) ) )
    def lowerItem( self ):
        row = self.getRow()
        if row is None or row + 1 >= len( self.globals ): return
        model = self.model
        model.globals[row], model.globals[row + 1] = model.globals[row + 1], model.globals[row]
        model.dataChanged.emit( model.index( row + 1, 0 ), model.index( row, 1 ) )
        self.widget.setCurrentIndex( self.widget.setCurrentIndex( model.index( row + 1 ) ) )
    def removeItem( self ):
        row = self.getRow()
        if row is None: return
        model = self.model
        model.beginRemoveRows( QtCore.QModelIndex(), row, row )
        model.globalRemoved.emit( model.globals.pop( row ) )
        model.endRemoveRows()
    def addItem( self ):
        self.model.addGlobal()

components.registerAdapter( GlobalsReorder, GlobalsModel, IReorderList )

class GlobalsEditWidget( QtGui.QGroupBox ):

    def __init__( self ):
        super( GlobalsEditWidget, self ).__init__( 'Globals' )
        self.setLayout( QtGui.QVBoxLayout() )
        self.layout().addWidget( ReorderWidget( GlobalsModel(), 'G' ) )

class GlobalsListWidget( QtGui.QListWidget ):
    globalSelected = QtCore.pyqtSignal( Global )
    def __init__( self ):
        super( GlobalsListWidget, self ).__init__()

        for globalInput in GlobalsModel().globals:
            listItem = QtGui.QListWidgetItem( '%s -> %s' % ( globalInput.name, globalInput.value ) )
            listItem.setToolTip( globalInput.description if globalInput.description else 'No description' )
            self.addItem( listItem )

        self.itemDoubleClicked.connect( lambda item: self.checkRow() )

    def keyPressEvent( self, event ):
        key = event.key()
        if key == QtCore.Qt.Key_Enter or key == QtCore.Qt.Key_Return:
            self.checkRow()

    def checkRow( self ):
        row = self.currentRow()
        if row >= 0:
            self.globalSelected.emit( GlobalsModel().globals[row] )
