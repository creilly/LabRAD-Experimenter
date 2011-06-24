'''
Created on Apr 26, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui, QtCore

from ..components import Global, Input
from icons import compIcons
from globals import GlobalsModel

class BaseComponentItem( QtGui.QStandardItem ):

    def __init__( self, component ):
        super( BaseComponentItem, self ).__init__()
        self.setEditable( False )
        self._component = component
        icon = compIcons.get( type( component ) )
        if icon: self.setIcon( icon )
        self.update()

    def update( self ):
        self.setText( repr( self.component ) )
        for child in [self.child( row ) for row in range( self.rowCount() )]:
            self.removeRow( child.row() )
        for child in self.component.children:
            self.appendRow( type( self )( child ) )

    @property
    def component( self ):
        return self._component

    def mimeData( self ):
        mimeData = QtCore.QMimeData()
        rows = []
        item = self
        while item:
            rows.append( str( item.row() ) )
            item = item.parent()
        mimeData.setData( 'lrexp/component', ','.join( rows ) )
        return mimeData

class ComponentItem( BaseComponentItem ):
    def __init__( self, component ):
        super( ComponentItem, self ).__init__( component )
        self.setDragEnabled( True )
        if type( component ) is Global:
            gModel = GlobalsModel()
            if component not in gModel.globals:
                gModel.addGlobal( component )

class BaseComponentModel( QtGui.QStandardItemModel ):
    Item = BaseComponentItem

    def setRoot( self, rootComponent ):
        if self.rowCount():
            self.removeRow( 0 )
        self.appendRow( self.Item( rootComponent ) )
        for item in self.items():
            print item

    def update( self ):
        def updateRecursively( item ):
            item.update()
            for row in range( item.rowCount() ):
                updateRecursively( item.child( row ) )
        for row in range( self.rowCount() ):
            updateRecursively( self.item( row ) )

    def getItemsFromComponent( self, target, startItem = None ):
        return self.getItemsFromFunction( lambda component: component is target, startItem )

    def getItemsFromFunction( self, function, startItem = None ):
        matches = []
        def searchRecursively( item ):
            if function( item.component ): matches.append( item )
            for row in range( item.rowCount() ):
                searchRecursively( item.child( row ) )
        searchRecursively( startItem if startItem else self.item( 0 ) )
        return matches

    def mimeData( self, indexes ):
        if len( indexes ) is not 1: return
        return self.itemFromIndex( indexes[0] ).mimeData()

    #returns generator that iterates over every item
    def items( self ):
        def crawl( item ):
            for row in range( item.rowCount() ):
                child = item.child( row )
                component = child.component
                yield child, child.component
                for grandChild in crawl( child ):
                    yield grandChild
        return crawl( self.invisibleRootItem() )

def wrapUpdateSignals( function ):
    def f( self, *args, **kwargs ):
        self.beginUpdate.emit()
        function( self, *args, **kwargs )
        self.endUpdate.emit()
    return f

instance = None
class ComponentModel( BaseComponentModel ):
    beginUpdate = QtCore.pyqtSignal()
    endUpdate = QtCore.pyqtSignal()

    Item = ComponentItem

    def __new__( cls ):
        global instance
        if instance is not None:
            return instance
        instance = super( ComponentModel, cls ).__new__( cls )
        super( ComponentModel, cls ).__init__( instance )
        return cls._init( instance )

    def __init__( self ):
        pass

    @staticmethod
    def _init( self ):
        gm = GlobalsModel()
        gm.globalRemoved.connect( self.globalRemoved )
        gm.globalsEdited.connect( self.update )
        self.rootComponent = None
        return self

    def globalRemoved( self, globalInput ):
        globalInput.__class__ = Input
        self.update()

    def mimeData( self, indexes ):
        mimeData = super( ComponentModel, self ).mimeData( indexes )
        if mimeData is None: return
        mimeData.setData( 'lrexp/source', 'Component model' )
        return mimeData

    @wrapUpdateSignals
    def update( self ):
        super( ComponentModel, self ).update()

    @wrapUpdateSignals
    def setRoot( self, rootComponent ):
        GlobalsModel().newRoot()
        super( ComponentModel, self ).setRoot( rootComponent )
        self.rootComponent = rootComponent

    @property
    def rootConfigured( self ):
        return bool( self.rootComponent ) and self.rootComponent.configured

def updateModel( f ):
    def execAndUpdate( *args, **kwargs ):
        try:
            f( *args, **kwargs )
            ComponentModel().update()
        except DontUpdate: pass
    return execAndUpdate

class DontUpdate( Exception ):
    pass
