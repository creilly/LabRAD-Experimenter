'''
Created on Jun 15, 2011

@author: christopherreilly
'''
import copy

from PyQt4 import QtGui, QtCore

from component import ComponentModel, ComponentItem, BaseComponentModel
from reorderlist import IReorderList, ReorderWidget
from zope.interface import implements
from twisted.python import components
from view import TreeView, ITree, TreeWidget

from ..components import IComponent

instance = None

class ClipBoardModel( BaseComponentModel ):

    def __new__( cls ):
        global instance
        if instance is not None:
            return instance
        instance = super( ClipBoardModel, cls ).__new__( cls )
        super( ClipBoardModel, cls ).__init__( instance )
        ComponentModel().endUpdate.connect( instance.update )
        return instance

    def __init__( self ):
        pass

    def mimeTypes( self ):
        return ['lrexp/component', 'lrexp/source']

    def dropMimeData( self, mimeData, action, row, column, parent ):
        rows = [int( row ) for row in str( mimeData.data( 'lrexp/component' ) ).split( ',' )]
        item = ( self if mimeData.data( 'lrexp/source' ) == 'Clip board' else ComponentModel() ).invisibleRootItem()
        while rows:
            item = item.child( rows.pop() )
        self.appendRow( item.component )
        return True

    def appendRow( self, item ):
        """
        Append any QStandardItem or Component
        """
        if IComponent.providedBy( item ):
            item = ComponentItem( item )
        super( ClipBoardModel, self ).appendRow( item )

    def mimeData( self, indexes ):
        mimeData = super( ClipBoardModel, self ).mimeData( indexes )
        if mimeData is None: return
        mimeData.setData( 'lrexp/source', 'Clip board' )
        return mimeData

    def appendCopy( self, component, deep = False ):
        copiedComponent = copy.copy( component )
        item = ComponentItem( copiedComponent )
        item.setText( item.text() + ' (copy)*' )
        item.setToolTip( 'Recently created component copy.  "(copy)" text may disappear.' )
        self.appendRow( item )

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
        self.tree = reorderList.widget

    def currentChanged( self, current, previous ):
        if not current.isValid():
            isFrontLevel = False
        else:
            isFrontLevel = current.parent() == QtCore.QModelIndex()
        self.raiseEnabled = self.lowerEnabled = self.removeEnabled = isFrontLevel

class ClipBoardSelectDialog( QtGui.QDialog ):
    def __init__( self, parent, condition = None, delegate = None ):
        super( ClipBoardSelectDialog, self ).__init__( parent )
        tree = TreeView()
        tree.setModel( ClipBoardModel() )
        if delegate: tree.setItemDelegate( delegate )

        condition = condition( self ) if condition else lambda component: True

        def doubleClicked( index ):
            if not index.isValid(): return
            component = tree.model().itemFromIndex( index ).component
            if condition( component ):
                self.result = component
                self.accept()

        tree.doubleClicked.connect( doubleClicked )

        layout = QtGui.QVBoxLayout( self )
        layout.addWidget( TreeWidget( tree, 'Get from Clip board' ) )
        self.condition = condition

    def show( self ):
        self.result = None
        super( ClipBoardSelectDialog, self ).show()

class ClipBoardBrowser( QtGui.QDialog ):
    def __init__( self, condition = lambda component: True ):
        super( ClipBoardBrowser, self ).__init__()
        tree = TreeView()
        tree.setModel( ClipBoardModel() )
        layout = QtGui.QVBoxLayout( self )
        layout.addWidget( TreeWidget( tree ) )
        tree.doubleClicked.connect( lambda index: self.componentSelected( tree.model().itemFromIndex( index ).component ) )
        self.condition = condition

    def componentSelected( self, component ):
        if self.condition( component ):
            self.component = component
            self.accept()

    def getComponent( self ):
        if self.exec_():
            return self.component

    def isLoopFree( self, child, parent ):
        def recursiveIDCheck( a, b ):
            if a is b:
                return b
            for child in b.children:
                result = recursiveIDCheck( a, child )
                if result:
                    return result
            return False
        for model in ( ComponentModel(), ClipBoardModel() ):
            for item in model.getItemsFromComponent( parent ):
                while item:
                    loopingComponent = recursiveIDCheck( item.component, child )
                    if loopingComponent:
                        if QtGui.QMessageBox.information( self,
                                                          'Loop detected',
                                                          'Selection rejected because <i><b>%s</b></i> would contain itself.  Create a copy?' % repr( loopingComponent ),
                                                          QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                          defaultButton = QtGui.QMessageBox.No ) == QtGui.QMessageBox.Yes:
                            ClipBoardModel().appendCopy( loopingComponent )
                        return False
                    item = item.parent()
        return True
