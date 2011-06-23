'''
Created on Jun 15, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui, QtCore

from component import ComponentModel, ComponentItem, BaseComponentModel
from reorderlist import IReorderList, ReorderWidget
from zope.interface import implements
from twisted.python import components
from view import TreeView, TreeWidget, ITree

instance = None

class ClipBoardModel( BaseComponentModel ):

    def __new__( cls ):
        global instance
        if instance is not None:
            return instance
        instance = super( ClipBoardModel, cls ).__new__( cls )
        super( ClipBoardModel, cls ).__init__( instance )
        return instance

    def __init__( self ):
        pass

    def mimeTypes( self ):
        return ['lrexp/component', 'lrexp/source', 'public/html']

    def dropMimeData( self, mimeData, action, row, column, parent ):
        rows = [int( row ) for row in str( mimeData.data( 'lrexp/component' ) ).split( ',' )]
        item = ( self if mimeData.data( 'lrexp/source' ) == 'Clip board' else ComponentModel() ).invisibleRootItem()
        while rows:
            item = item.child( rows.pop() )
        self.appendRow( ComponentItem( item.component ) )
        return True

    def mimeData( self, indexes ):
        mimeData = super( ClipBoardModel, self ).mimeData( indexes )
        if mimeData is None: return
        mimeData.setData( 'lrexp/source', 'Clip board' )
        return mimeData

class ClipBoardReorderModel( object ):
    implements( IReorderList )
    UP = -1
    DOWN = 1
    REMOVE = None

    def __init__( self, model ):
        tree = self.widget = self.tree = TreeView()
        tree.setSelectionMode( tree.SingleSelection )
        tree.setModel( model )
        tree.setDragDropMode( tree.DragDrop )
        self.raiseItem = lambda: self.changeRows( self.UP )
        self.lowerItem = lambda: self.changeRows( self.DOWN )
        self.removeItem = lambda: self.changeRows( self.REMOVE )
        self.model = model

    def getRow( self ):
        index = self.tree.currentIndex()
        if not index.isValid(): return None
        item = self.model.itemFromIndex( index )
        return item.row() if not item.parent() else None
    def changeRows( self, mode ):
        row = self.getRow()
        if row is None: return
        model = self.model
        if mode is self.REMOVE:
            model.removeRow( row )
            newRow = min( ( row, model.rowCount() - 1 ) )
        else:
            newRow = max( ( 0, min( ( model.rowCount() - 1, row + mode ) ) ) )
            model.insertRow( newRow, model.takeRow( row ) )
        toSelect = model.item( newRow )
        if toSelect:
            self.tree.setCurrentIndex( toSelect.index() )
    def addItem( self ):
        pass

components.registerAdapter( ClipBoardReorderModel, ClipBoardModel, IReorderList )

class ClipBoardReorderWidget( ReorderWidget ):
    implements( ITree )
    def __init__( self ):
        reorderList = IReorderList( ClipBoardModel() )
        super( ClipBoardReorderWidget, self ).__init__( reorderList, 'C' )
        self.addEnabled = False
        reorderList.widget.selectionModel().currentChanged.connect( self.currentChanged )
        for attr in ITree.names():
            setattr( self, attr, getattr( reorderList.widget, attr ) )

    def currentChanged( self, current, previous ):
        if not current.isValid():
            isFrontLevel = False
        else:
            isFrontLevel = current.parent() == QtCore.QModelIndex()
        self.raiseEnabled = self.lowerEnabled = self.removeEnabled = isFrontLevel
