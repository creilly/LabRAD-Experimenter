from labrad.types import parseTypeTag, LRCluster, LRNone

class LabradSetting( object ):
    """
    A persistent representation of a labRAD setting. Make sure the Client class possesses a labRAD connection before attempting to use.
    
    You can optionally initialize with one of the strings from the labRAD setting's 'accept' property.  In this case the parameters property is an ordered list of labRAD type strings for that particular overloaded version of the setting.
    
    This object can be called with arguments just like a regular labRAD setting.
    """
    def __init__( self, setting, overload ):
        self.serverName = setting._server.name
        self.settingName = setting.name
        self.doc = repr( setting ) + '\n' + 'OVERLOAD: %s' % overload
        self.parameters = self.parseOverload( overload )

    @staticmethod
    def parseOverload( overload ):
        parsed = parseTypeTag( overload )
        if type( parsed ) is LRNone:
            pars = []
        else:
            if type( parsed ) is not LRCluster:
                parsed = ( parsed, )
            pars = [str( par ) for par in parsed]
        return pars

    def setting( self ):
        return Client.connection.servers[self.serverName].settings[self.settingName]
    def __call__( self, *pars, **kwpars ):
        return Client.connection.servers[self.serverName].settings[self.settingName]( *pars, **kwpars )
    def __repr__( self ):
        return str( self.doc )

class Client( object ):
    """
    This packages looks to this class's connection attribute to provide a labRAD connection.
    
    Set this object with a labRAD connection before attempting to use labRAD specific features of the package.
    """
    connection = None
