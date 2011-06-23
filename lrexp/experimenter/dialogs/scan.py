'''
Created on Jun 5, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui
from . import UnitDialog, UnitSelectorWidget
from ..view import TreeView, TreeWidget
from ..delegate import BaseColorDelegate
from ..component import ComponentModel
from ...components import Input

class ScanDialog( UnitDialog ):
    def __init__( self, parent, component ):
        super( ScanDialog, self ).__init__( parent, component )

        treeTab = QtGui.QWidget()

        treeLayout = QtGui.QVBoxLayout( treeTab )

        unitSelector = UnitSelectorWidget()
        unitSelector.unitSelected.connect( self.setScanUnit )

        tree = self.tree = TreeView()
        tree.setModel( ComponentModel() )
        tree.doubleClicked.connect( lambda index: self.setScanInput( ComponentModel().itemFromIndex( index ).component ) )
        self.highlightScanInput = BaseColorDelegate()
        tree.setItemDelegate( self.highlightScanInput )
        treeWidget = self.treeWidget = TreeWidget( tree )
        self.scanInputCycler = treeWidget.addCycler( 'Scan input' )
        self.updateTree()

        treeLayout.addWidget( unitSelector )
        treeLayout.addWidget( treeWidget )

        self.tabWidget.insertTab( 0, treeTab, 'Scan Unit/Input' )
        self.tabWidget.setCurrentIndex( 0 )

    def setScanUnit( self, unit ):
        self.component.scanUnit = unit
        ComponentModel().update()
        self.updateTree()

    def setScanInput( self, input ):
        if type( input ) is not Input: return
        self.component.scanInput = input
        ComponentModel().update()
        self.updateTree()

    def updateTree( self ):
        rootItem = ComponentModel().getItemsFromComponent( self.component.scanUnit )[0]
        self.tree.setRootIndex( rootItem.index() )
        self.treeWidget.setTitle( 'Scan unit: %s (%s)' % ( repr( self.component.scanUnit ), type( self.component.scanUnit ).__name__ ) )
        self.highlightScanInput.clearMatches()
        self.highlightScanInput.addMatchColor( self.component.scanInput, 'red' )
        self.scanInputCycler.setIndexes( [item.index() for item in ComponentModel().getItemsFromComponent( self.component.scanInput, rootItem )] )
        self.scanInputCycler.next()

