from PyQt4 import QtGui, QtCore

from component import ComponentModel, updateModel

class BaseColorDelegate( QtGui.QStyledItemDelegate ):
    """
    Conditions are checked if component is not in match dictionary.
    First true condition returns color.
    """
    BIG = 1.4
    MEDIUM = 1.2
    SMALL = 1
    _size = SMALL
    def __init__( self ):
        super( BaseColorDelegate, self ).__init__()
        self.matchDict = {}
        self.conditions = []
    def initStyleOption( self, option, index ):
        option.font.setPointSize( int( option.font.pointSize() * self.size ) )
        fm = QtGui.QFontMetrics( option.font )
        option.decorationSize = QtCore.QSize( 1.5 * fm.height(), fm.height() )
        super( BaseColorDelegate, self ).initStyleOption( option, index )
        item = ComponentModel().itemFromIndex( index )
        if item is None: return
        color = self.getIndexColor( item.component )
        if color is None: return
        option.palette.setBrush( QtGui.QPalette.Text, QtGui.QBrush( QtGui.QColor( color ) ) )
    def addMatchColor( self, match, color ):
        self.matchDict[match] = color
    def addConditionColor( self, condition, color, index = None ):
        if index is None:
            self.conditions.append( ( condition, color ) )
            return
        self.conditions.insert( index, ( condition, color ) )
    def getIndexColor( self, component ):
        color = self.matchDict.get( component )
        if color: return color
        for condition, col in self.conditions:
            if condition( component ):
                return col
    def clearMatches( self ):
        self.matchDict.clear()
        while self.conditions: self.conditions.pop()

    @property
    def size( self ):
        return self._size

    @classmethod
    @updateModel
    def setSize( cls, size ):
        cls._size = size

