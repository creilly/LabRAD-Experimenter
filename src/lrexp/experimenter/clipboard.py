'''
The clip board functions as a workspace while creating the root unit tree.

Drag units from the tree into the clipboard, where they can be temporarily stored or made more easily accessible.

Scans, for instance, can select from the clipboard when assigning its scanUnit.

The clipboard has methods in place to detect units looping in on themselves and prevent their insertion into the tree structure.
'''
import copy

from PyQt4 import QtGui, QtCore

from component import ComponentModel, ComponentItem, BaseComponentModel
from reorderlist import IReorderList, ReorderWidget
from zope.interface import implements
from twisted.python import components
from view import TreeView, ITree, TreeWidget

from ..components import IComponent, IUnit

instance = None

class ClipBoardModel( BaseComponentModel ):
    duplicateDetected = QtCore.pyqtSignal( QtCore.QModelIndex )
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
            for row in range( self.rowCount() ):
                if self.item( row ).component is item:
                    self.duplicateDetected.emit( self.item( row ).index() )
                    return
            item = ComponentItem( item )
        super( ClipBoardModel, self ).appendRow( item )

    def mimeData( self, indexes ):
        mimeData = super( ClipBoardModel, self ).mimeData( indexes )
        if mimeData is None: return
        mimeData.setData( 'lrexp/source', 'Clip board' )
        return mimeData

    def appendCopy( self, component, deep = False ):
        copiedComponent = copy.deepcopy( component )
        item = ComponentItem( copiedComponent )
        def renameRecursively( item ):
            item.setText( item.text() + ' (copy)*' )
            item.setToolTip( 'Recently created component copy.  "(copy)" text may disappear.' )
            if IUnit.providedBy( item.component ):
                item.component.name += ' (copy)'
            for row in range( item.rowCount() ):
                renameRecursively( item.child( row ) )
        renameRecursively( item )
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
        tree.setDropIndicatorShown( False )
        model.duplicateDetected.connect( self.duplicateDetected )
        self.raiseItem = lambda: self.changeRows( self.UP )
        self.lowerItem = lambda: self.changeRows( self.DOWN )
        self.removeItem = lambda: self.changeRows( self.REMOVE )
        self.model = model
    def duplicateDetected( self, index ):
        self.tree.setCurrentIndex( index )
        QtGui.QMessageBox.information( self.tree, 'Already in clipboard', 'Component already a top level entry in clipboard' )

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
                                                          'Selection rejected because <i><b>%s</b></i> would contain itself.  Create a copy of %s?' % ( repr( loopingComponent ), repr( child ) ),
                                                          QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                          defaultButton = QtGui.QMessageBox.No ) == QtGui.QMessageBox.Yes:
                            ClipBoardModel().appendCopy( child )
                        return False
                    item = item.parent()
        return True
