'''
Created on Apr 26, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui, QtCore

class TreeWidget( QtGui.QGroupBox ):
    class Cycler( QtGui.QPushButton ):
        def __init__( self, text, tree, indexes = [] ):
            super( TreeWidget.Cycler, self ).__init__( text )
            self.i = 0
            self.indexes = indexes
            self.tree = tree
            self.clicked.connect( self.next )
            self.setEnabled( bool( indexes ) )
        def setIndexes( self, indexes ):
            self.indexes = indexes
            self.setEnabled( bool( indexes ) )
            self.i = 0
        def next( self ):
            if not self.indexes: return
            index = self.indexes[self.i]
            self.tree.expandTo( index )
            self.tree.setCurrentIndex( index )
            self.i = ( self.i + 1 ) % len( self.indexes )

    def __init__( self, tree, title = '', parent = None ):
        super( TreeWidget, self ).__init__( title, parent )

        expand = QtGui.QPushButton( 'Expand all' )
        expand.clicked.connect( tree.expandAll )

        collapse = QtGui.QPushButton( 'Collapse all' )
        collapse.clicked.connect( tree.collapseAll )
        collapse.clicked.connect( lambda: tree.setCurrentIndex( QtCore.QModelIndex() ) )

        self.setLayout( QtGui.QVBoxLayout() )
        self.layout().addWidget( tree )
        expandRow = self.expandRow = QtGui.QHBoxLayout()
        expandRow.addWidget( expand )
        expandRow.addWidget( collapse )
        expandRow.addStretch()
        self.layout().addLayout( expandRow )

        self.tree = tree

    def addCycler( self, text, indexes = [] ):
        cycler = self.Cycler( text, self.tree, indexes )
        self.expandRow.addWidget( cycler )
        return cycler

    def addButton( self, text ):
        button = QtGui.QPushButton( text )
        self.expandRow.addWidget( button )
        return button

class BaseListView( QtGui.QListView ):
    def __init__( self, parent = None ):
        super( BaseListView, self ).__init__( parent )
        self.setAlternatingRowColors( True )

    def keyPressEvent( self, event ):
        key = event.key()
        if key == QtCore.Qt.Key_Enter or key == QtCore.Qt.Key_Return:
            self.doubleClicked.emit( self.currentIndex() )
            return
        super( BaseListView, self ).keyPressEvent( event )

class TreeView( QtGui.QTreeView ):
    def __init__( self, parent = None ):
        super( TreeView, self ).__init__( parent )
        self.setAlternatingRowColors( True )
        self.setHeaderHidden( True )
        self.setExpandsOnDoubleClick( False )

    def expandTo( self, index ):
        def expand( child ):
            self.expand( child )
            if child.parent().isValid(): expand( child.parent() )
        expand( index )

    def keyPressEvent( self, event ):
        key = event.key()
        if key == QtCore.Qt.Key_Enter or key == QtCore.Qt.Key_Return:
            self.doubleClicked.emit( self.currentIndex() )
            return
        super( TreeView, self ).keyPressEvent( event )
