'''
Created on Jul 8, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui, QtCore

from component import updateModel
from view import BaseListView
from reorderlist import IReorderList
from zope.interface import implements

class ComponentReorderList( QtCore.QAbstractListModel ):
    """
    Takes in a python list and a Qt view.  View must implement currentIndex().
    
    Implementation of IReorderList for lists of lrexp components.
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
