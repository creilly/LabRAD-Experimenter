'''
Created on Jun 8, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui, QtCore
from ..component import BaseComponentModel, updateModel
from ..view import TreeView, TreeWidget
from ...components import Action, Scan, Sequence, Repeat, Conditional
from ..labradconnection import LRConnectionManager
class ExecuteDialog( QtGui.QDialog ):
    def __init__( self, parent, rootComponent ):
        super( ExecuteDialog, self ).__init__( parent )
        self.rootComponent = rootComponent
        self.generator = rootComponent.__iter__()
        cxnMan = LRConnectionManager()
        cxnMan.connectionMade.connect( lambda: self.connectionChanged( True ) )
        cxnMan.connectionLost.connect( lambda: self.connectionChanged( False ) )
        timer = self.timer = QtCore.QTimer( self )
        timer.setInterval( 0 )
        timer.timeout.connect( self.next )
        model = self.model = BaseComponentModel()
        model.setRoot( rootComponent )
        view = self.view = TreeView()
        view.setModel( model )
        treeWidget = TreeWidget( view, 'Execute Unit' )
        next = treeWidget.addButton( 'Next' )
        run = treeWidget.addButton( 'Run' )
        pause = self.pause = treeWidget.addButton( 'Pause' )
        pause.setEnabled( False )
        next.clicked.connect( self.next )
        run.clicked.connect( lambda: run.setText( 'Running...' ) or run.setEnabled( False ) or next.setEnabled( False ) or pause.setEnabled( True ) or timer.start() )
        pause.clicked.connect( lambda: run.setText( 'Run' ) or run.setEnabled( True ) or next.setEnabled( True ) or pause.setEnabled( False ) or timer.stop() )
        layout = QtGui.QVBoxLayout( self )
        layout.addWidget( treeWidget )
    def next( self ):
        try:
            chain = self.generator.next()
        except StopIteration:
            self.unitFinished()
            return
        item = self.model.invisibleRootItem()
        row = [0]
        while chain:
            while row:
                item = item.child( row.pop() )
            cls, state = chain.pop()
            unitText = repr( item.component )
            if cls is Action:
                item.setText( '%s -> %s' % ( unitText, str( state ) ) )
                continue
            if cls in ( Sequence, Scan, Repeat ):
                if state is not None:
                    item.setText( '%s -> ( %d of %d )' % ( unitText, state[0], state[1] ) )
                    row = [ state[0] - 1 ] if cls is Sequence else [0]
                    continue
                else:
                    item.setText( unitText )
                    break
            if cls is Conditional:
                if state is not None:
                    item.setText( '%s -> %s' % ( unitText, str( state ) ) )
                    row = [0, int( not state )]
                    continue
                else:
                    item.setText( unitText )
                    break

        self.view.collapseAll()
        index = item.index()
        self.view.setCurrentIndex( index )
        self.view.expandTo( index )
        self.view.expand( index )

    def unitFinished( self ):
        QtGui.QMessageBox.information( self, 'Unit completed', 'Unit has finished execution.' )
        self.reset()

    @updateModel
    def reset( self ):
        self.pause.click()
        self.rootComponent.initialize()
        self.model.setRoot( self.rootComponent )
        self.generator = self.rootComponent.__iter__()

    def closeEvent( self, event ):
        self.timer.stop()
        self.timer.deleteLater()
        super( ExecuteDialog, self ).closeEvent( event )

    def connectionChanged( self, connected ):
        if QtGui.QMessageBox.information( self,
                                          'LabRAD connection status changed',
                                          'Connection with LabRAD %s.  Reset unit execution?' % ( 'made' if connected else 'lost' ),
                                          QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                          defaultButton = QtGui.QMessageBox.Ok ) == QtGui.QMessageBox.Ok:
            self.reset()
