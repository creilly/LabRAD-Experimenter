from PyQt4 import QtGui

from component import ComponentModel

class BaseColorDelegate( QtGui.QStyledItemDelegate ):
    """
    Conditions are checked if component is not in match dictionary.
    First true condition returns color.
    """
    def __init__( self ):
        super( BaseColorDelegate, self ).__init__()
        self.matchDict = {}
        self.conditions = []
    def initStyleOption( self, option, index ):
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

