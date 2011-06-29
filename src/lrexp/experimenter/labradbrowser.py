'''
Created on Jun 9, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui
from ..lr import LabradSetting
from labradconnection import LRConnectionManager
from functionbrowser import BaseFunctionModelItem, InfoWidget, Organizer

class LabradModel( QtGui.QStandardItemModel ):
    SERVER = 0
    SETTING = 1
    OVERLOAD = 2
    def __init__( self ):
        super( LabradModel, self ).__init__()
        cxnMan = LRConnectionManager( self )
        self.cxn = cxnMan.connection
        self.update() if self.cxn else self.noConnection()
        cxnMan.connectionMade.connect( self.update )
        cxnMan.connectionLost.connect( self.noConnection )

    def update( self ):
        self.clear()
        for serverName, server in self.cxn.servers.items():
            serverItem = LabradItem( serverName, repr( server ), self.SERVER )
            for settingName, setting in server.settings.items():
                settingItem = LabradItem( settingName, repr( setting ), self.SETTING )
                for overload in setting.accepts:
                    settingItem.appendRow( OverloadItem( overload, LabradSetting( setting, overload ) ) )
                serverItem.appendRow( settingItem )
            self.appendRow( serverItem )

    def noConnection( self ):
        self.clear()
        self.appendRow( Organizer( 'No LabRAD connection' ) )
class LabradItem( BaseFunctionModelItem ):
    def __init__( self, name, doc, type ):
        super( LabradItem, self ).__init__()
        self.name = name
        self.setText( name )
        self.getInfoWidget = lambda: InfoWidget( '%s (%s)' % ( name, 'Server' if type is LabradModel.SERVER else 'Setting' ), doc )
        self.type = type

class OverloadItem( BaseFunctionModelItem ):
    type = LabradModel.OVERLOAD
    def __init__( self, name, obj ):
        super( OverloadItem, self ).__init__()
        self.object = obj
        self.setText( name if name else 'No args' )

