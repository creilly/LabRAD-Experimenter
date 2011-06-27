'''
Created on Apr 26, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui, QtCore

from ..components import Global, Input, IUnit, IComponent, NullUnit
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

    def setColor( self, color ):
        self.setForeground( QtGui.QBrush( QtGui.QColor( color ) ) )

    def setWeight( self, weight ):
        font = QtGui.QFont()
        font.setWeight( weight )
        self.setFont( font )

class ComponentItem( BaseComponentItem ):
    def __init__( self, component ):
        super( ComponentItem, self ).__init__( component )
        self.setDragEnabled( True )
        if type( component ) is Global:
            gModel = GlobalsModel()
            if component not in gModel.globals:
                gModel.addGlobal( component )

    def update( self ):
        component = self.component
        if IUnit.providedBy( component ):
            self.setColor( None if component.configured else 'red' )
        elif type( component ) is Global:
            self.setColor( 'purple' )
        super( ComponentItem, self ).update()

class BaseComponentModel( QtGui.QStandardItemModel ):
    Item = BaseComponentItem
    class Cycler( QtCore.QObject ):
        def __init__( self, model, view, condition, button = None ):
            super( BaseComponentModel.Cycler, self ).__init__( view )
            self.model, self.view, self.condition, self.button = model, view, condition, button
            if button:
                button.clicked.connect( self.next )
            self.update()
        def next( self ):
            self.i = self.i % len( self.items )
            index = self.items[self.i].index()
            self.view.expandTo( index )
            self.view.setCurrentIndex( index )
            self.i += 1
        def update( self ):
            self.items = []
            self.i = 0
            for item, component in self.model.items():
                if self.condition( component ):
                    self.items.append( item )
            if self.button:
                self.button.setEnabled( bool( self.items ) )
        def getCondition( self ):
            return self._condition
        def _setCondition( self, condition ):
            self._condition = self._condition = condition if not IComponent.providedBy( condition ) else lambda component: component is condition
        condition = property( getCondition, _setCondition )

        def setCondition( self, condition ):
            self.condition = condition
            self.update()

    def setRoot( self, rootComponent ):
        if self.rowCount():
            self.removeRow( 0 )
        self.appendRow( self.Item( rootComponent ) )

    def update( self ):
        def updateRecursively( item ):
            item.update()
            for row in range( item.rowCount() ):
                updateRecursively( item.child( row ) )
        for row in range( self.rowCount() ):
            updateRecursively( self.item( row ) )
        for cycler in self.cyclers:
            cycler.update()

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
                yield child, child.component
                for grandChild in crawl( child ):
                    yield grandChild
        return crawl( self.invisibleRootItem() )

    def addCycler( self, view, condition, button = None ):
        cycler = self.Cycler( self, view, condition, button )
        self.cyclers.append( cycler )
        return cycler

    @property
    def cyclers( self ):
        if not hasattr( self, '_cyclers' ):
            self._cyclers = []
        return self._cyclers

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
        self.rootComponent = NullUnit()
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

class ColorComponentItem( BaseComponentItem ):
    def update( self ):
        if self.model():
            for condition, color, weight in self.model().conditions:
                if condition( self.component ):
                    self.setColor( color )
                    self.setWeight( weight )
                    break #exits loop after a condition is satisfied 
        super( ColorComponentItem, self ).update()

class ColorComponentModel( BaseComponentModel ):

    Item = ColorComponentItem

    class ColorCondition( object ):
        def __init__( self, model, condition, color, weight ):
            self.condition, self.color, self.weight = condition, color, weight
            def getSetter( name ):
                def setAndUpdate( value ):
                    setattr( self, name, value )
                    model.update()
                return setAndUpdate
            for element in ( 'Condition', 'Color', 'Weight' ):
                setattr( self, 'set' + element, getSetter( element.lower() ) )
        def __iter__( self ):
            return ( self.condition, self.color, self.weight ).__iter__()
        def getCondition( self ):
            return self._condition
        def _setCondition( self, condition ):
            self._condition = condition if not IComponent.providedBy( condition ) else lambda component: component is condition
        condition = property( getCondition, _setCondition )

    def addColorCondition( self, condition, color, weight = None ):
        return self.insertColorCondition( len( self.conditions ), condition, color, weight )

    def insertColorCondition( self, index, condition, color, weight = None ):
        colorCondition = self.ColorCondition( self, condition, color, weight )
        self.conditions.insert( index, colorCondition )
        self.update()
        return colorCondition

    @property
    def conditions( self ):
        if not hasattr( self, '_conditions' ):
            self._conditions = []
        return self._conditions


