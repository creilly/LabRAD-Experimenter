import labrad
import twisted
from PyQt4 import QtGui, QtCore

from ..lr import Client

instance = None
class LRConnectionManager( QtCore.QObject ):
    """
    Checks connectivity whenever you try to access the connection.
    """
    connectionMade = QtCore.pyqtSignal()
    connectionLost = QtCore.pyqtSignal()
    connectionFailed = QtCore.pyqtSignal()
    _connection = None
    def __new__( cls, parent = None ):
        global instance
        if instance is not None:
            return instance
        instance = super( LRConnectionManager, cls ).__new__( cls )
        super( LRConnectionManager, cls ).__init__( instance, parent )
        return instance
    def __init__( self, parent = None ):
        pass
    @property
    def connection( self ):
        return Client.connection
    @property
    def connected( self ):
        return bool( Client.connection )
    def connect( self ):
        if self.connected: return
        try:
            Client.connection = labrad.connect()
            Client.connection._cxn.connectionLost = self._connectionLost
            self.connectionMade.emit()
        except:
            Client.connection = None
            self.connectionFailed.emit()

    def _connectionLost( self, *l, **kw ):
        Client.connection = None
        self.connectionLost.emit()

