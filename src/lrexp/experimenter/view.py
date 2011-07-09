from PyQt4 import QtGui, QtCore
from zope.interface import Interface, implements

class TreeWidget( QtGui.QGroupBox ):
    """
    Wraps a treeview with buttons to expand/collapse the treeview.
    
    Also supports adding additional buttons to extend functionality.
    """
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
    """
    Connects enter/return key presses to the doubleclicked signal
    """
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
    """
    If you want to throw something besides a TreeView (custom class) into a TreeWidget,
    just make sure it implements this interface.  See the Clip board for an example of how this is used.
    """
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
    """
    Added a couple methods to expand to a particular index.
    """
    implements( ITree )
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
