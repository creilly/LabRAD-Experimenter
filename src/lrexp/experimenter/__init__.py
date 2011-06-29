from PyQt4 import QtGui

class Shortcut( QtGui.QKeySequence ):
    def __init__( self, shortcut ):
        super( Shortcut, self ).__init__( shortcut )

