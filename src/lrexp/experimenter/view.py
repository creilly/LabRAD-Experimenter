'''
Created on Apr 26, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui, QtCore
from zope.interface import Interface, implements
from delegate import BaseColorDelegate

class TreeWidget( QtGui.QGroupBox ):

    def __init__( self, tree, title = '', parent = None ):
        super( TreeWidget, self ).__init__( title, parent )

        tree = ITree( tree )

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

class ITree( Interface ):
    def expandTo( index ):
        """
        Expand all parent indexes of the specified indexes
        """
    def setCurrentIndex( index ):
        """
        Make specified index the active index
        """
    def expandAll():
        """
        Expand all indexes
        """
    def collapseAll():
        """
        Collapse all indexes
        """

class TreeView( QtGui.QTreeView ):
    implements( ITree )
    def __init__( self, parent = None ):
        super( TreeView, self ).__init__( parent )
        self.setAlternatingRowColors( True )
        self.setHeaderHidden( True )
        self.setExpandsOnDoubleClick( False )
        self.setItemDelegate( BaseColorDelegate() )

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
