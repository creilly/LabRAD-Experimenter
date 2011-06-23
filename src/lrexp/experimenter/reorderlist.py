'''
Created on May 2, 2011

@author: christopherreilly
'''
import os

from PyQt4 import QtGui, QtCore

from icons import arrowIcons

from zope.interface import Interface, Attribute

class IReorderList( Interface ):
    """
    Classes that implement this interface can interact with the ReorderWidget
    """
    widget = Attribute( "Widget that is the central widget of the ReorderWidget.  Should be a representation of the list being reordered." )
    def raiseItem():
        """
        Raise the current item in the list.
        """

    def lowerItem():
        """
        Lower the current item in the list.
        """

    def addItem():
        """
        Add a new item to the list.
        """

    def removeItem():
        """
        Remove the current item from the list.
        """

class ReorderWidget( QtGui.QWidget ):
    RAISE = 'raise'
    LOWER = 'lower'
    ADD = 'add'
    REMOVE = 'remove'

    def __init__( self, reorderList, baseKey = 'L' ):
        super( ReorderWidget, self ).__init__()
        self.setLayout( QtGui.QHBoxLayout() )
        self.enabledDict = {}

        reorderList = IReorderList( reorderList )

        toolbar = self.toolbar = QtGui.QToolBar()
        toolbar.setFloatable( False )
        toolbar.setOrientation( QtCore.Qt.Vertical )
        toolbar.setIconSize( QtCore.QSize( 16, 16 ) )

        def modFunc( f, key ):
            return lambda * l: f()

        self.enabledDict = {}
        for icon, tip, function, shortcut, keyword in zip( ( 'up', 'down', 'plus', 'minus' ),
                                                       ( 'Raise item', 'Lower item', 'Add item', 'Remove item' ),
                                                       ( reorderList.raiseItem, reorderList.lowerItem, reorderList.addItem, reorderList.removeItem ),
                                                       ( 'U', 'D', 'A', 'R' ),
                                                       ( self.RAISE, self.LOWER, self.ADD, self.REMOVE ) ):
            action = QtGui.QAction( arrowIcons[icon], tip, toolbar )
            action.triggered.connect( modFunc( function, keyword ) )
            action.setShortcut( QtGui.QKeySequence( 'Ctrl+%c, Ctrl+%c' % ( baseKey, shortcut ), QtGui.QKeySequence.NativeText ) )
            self.enabledDict[keyword] = action
            toolbar.addAction( action )

        self.layout().addWidget( reorderList.widget, 1 )
        self.layout().addWidget( toolbar )

    def _getEnabled( self, key ):
        return self.enabledDict[key].isEnabled()
    def _setEnabled( self, key, value ):
        self.enabledDict[key].setEnabled( value )

#===============================================================================
# Create convenient properties to enable or disable raise, lower, add, or remove buttons
# 
# i.e:
# 
# == > self.raiseEnabled = False
# == > self.lowerEnabled = True
#===============================================================================
RW = ReorderWidget
for key in ( RW.RAISE, RW.LOWER, RW.ADD, RW.REMOVE ):
    def get( key ):
        return lambda self: self._getEnabled( key )
    def set( key ):
        return lambda self, enabled: self._setEnabled( key, enabled )
    prop = property( get( key ), set( key ) )
    setattr( RW, key + 'Enabled', prop )
del RW
