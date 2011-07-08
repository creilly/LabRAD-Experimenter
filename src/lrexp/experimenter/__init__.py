from PyQt4 import QtGui

class Shortcut( QtGui.QKeySequence ):
    """
    Makes it simple to toggle between NativeText type shortcuts and normal shortcuts.
    """
    def __init__( self, shortcut ):
        super( Shortcut, self ).__init__( shortcut )

