'''
UnitDialog with a function select tab
'''
from . import UnitDialog

from ..editor import FunctionEditorUpdater

class ActionDialog( UnitDialog ):
    def __init__( self, parent, component ):
        super( ActionDialog, self ).__init__( parent, component )
        self.tabWidget.insertTab( 0, FunctionEditorUpdater( component, 'Function', self ), 'Function' )
        self.tabWidget.setCurrentIndex( 0 )

