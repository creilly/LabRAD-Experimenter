'''
Created on Apr 26, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui, QtCore

from ..components import Global, Input, IUnit
from icons import unitIcons
from globals import GlobalsModel

class BaseComponentModel( QtGui.QStandardItemModel ):
    beginUpdate = QtCore.pyqtSignal()
    endUpdate = QtCore.pyqtSignal()
    def __init__( self ):
        super( BaseComponentModel, self ).__init__()
        gm = GlobalsModel()
        gm.globalRemoved.connect( self.globalRemoved )
        gm.globalsEdited.connect( self.update )
        self.rootComponent = None

    def globalRemoved( self, globalInput ):
        globalInput.__class__ = Input
        self.update()

    def setRoot( self, rootComponent ):
        self.beginUpdate.emit()
        if self.rowCount():
            self.removeRow( 0 )
        GlobalsModel().newRoot()
        self.appendRow( ComponentItem( rootComponent ) )
        self.rootComponent = rootComponent
        self.endUpdate.emit()

    def update( self ):
        self.beginUpdate.emit()
        def updateRecursively( item ):
            item.update()
            for row in range( item.rowCount() ):
                updateRecursively( item.child( row ) )
        updateRecursively( self.item( 0 ) )
        self.endUpdate.emit()

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

instance = None
class ComponentModel( BaseComponentModel ):

    def __new__( cls ):
        global instance
        if instance is not None:
            return instance
        instance = super( ComponentModel, cls ).__new__( cls )
        super( ComponentModel, cls ).__init__( instance )
        return instance
    def __init__( self ):
        pass

class ComponentItem( QtGui.QStandardItem ):

    def __init__( self, component ):
        super( ComponentItem, self ).__init__()
        self.setEditable( False )
        self._component = component
        if type( component ) is Global:
            gModel = GlobalsModel()
            if component not in gModel.globals:
                gModel.addGlobal( component )
        if IUnit.providedBy( component ):
            self.setIcon( unitIcons[ type( component ) ] )
        self.update()

    def update( self ):
        self.setText( repr( self.component ) )
        for child in [self.child( row ) for row in range( self.rowCount() )]:
            self.removeRow( child.row() )
        for child in self.component.children:
            self.appendRow( ComponentItem( child ) )

    @property
    def component( self ):
        return self._component

def updateModel( f ):
    def execAndUpdate( *args, **kwargs ):
        try:
            f( *args, **kwargs )
            ComponentModel().update()
        except DontUpdate: pass
    return execAndUpdate

class DontUpdate( Exception ):
    pass
