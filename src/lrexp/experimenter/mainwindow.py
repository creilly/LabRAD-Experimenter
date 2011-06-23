'''
Created on Apr 26, 2011

@author: christopherreilly
'''

import os

from PyQt4 import QtGui, QtCore

from component import ComponentModel, updateModel
from globals import GlobalsEditWidget
from menu import menubar, recentUnits, fileMenu, askToSave, _saveUnitAs
from view import TreeView, TreeWidget
from delegate import BaseColorDelegate
from dialogs import input, sequence, parameter, componentgroup, scan, action, execute
from labradconnection import LRConnectionManager
from clipboard import ClipBoardReorderWidget

from ..components import IUnit, Input, Global, Map, Result, Action, Sequence, Parameter, ScanRange, ArgumentList, Scan
from ..util import loadUnit

class TitleLabel( QtGui.QLabel ):
    base = '<big><b>Experimenter:</b> '
    def __init__( self ):
        super( TitleLabel, self ).__init__( '%s<i>load a unit</i></big>' % self.base )
    def newFile( self, filename ):
        self.setText( '%s%s' % ( self.base, os.path.basename( str( filename ) ) if str( filename ) else '<i>untitled</i>' ) )
        self.setToolTip( filename )

class MainWindow( QtGui.QMainWindow ):

    dialogDict = {
        Input:input.InputDialog,
        Global:input.GlobalDialog,
        Map:input.MapDialog,
        Result:input.ResultDialog,
        Parameter:parameter.ParameterDialog,
        ArgumentList:componentgroup.ArgumentListDialog,
        ScanRange:componentgroup.ScanRangeDialog,
        Action:action.ActionDialog,
        Scan:scan.ScanDialog,
        Sequence:sequence.SequenceDialog
        }

    def __init__( self ):
        super( MainWindow, self ).__init__()

        self.setMenuBar( menubar )
        executeRoot = menubar.addMenu( 'Execute' ).addAction( 'Execute Root' )
        executeRoot.setShortcut( QtGui.QKeySequence( 'Ctrl+E', QtGui.QKeySequence.NativeText ) )
        executeRoot.setEnabled( False )
        executeRoot.triggered.connect( lambda: self.executeUnit( ComponentModel().rootComponent ) )
        ComponentModel().endUpdate.connect( lambda: executeRoot.setEnabled( ComponentModel().rootConfigured ) )

        centralWidget = QtGui.QWidget()
        centralWidget.setLayout( QtGui.QVBoxLayout() )

        titleLabel = TitleLabel()

        recentUnits.currentFileChanged.connect( titleLabel.newFile )

        centralWidget.layout().addWidget( titleLabel )

        widgets = QtGui.QHBoxLayout()

        rootView = self.rootView = TreeView()
        rootView.setDragEnabled( True )
        rootView.pressed.connect( self.mouseEvent )
        rootView.setModel( ComponentModel() )
        delegate = RootColorDelegate()
        rootView.setItemDelegate( delegate )
        rootView.doubleClicked.connect( lambda index: self.editComponent( rootView.model().itemFromIndex( index ).component ) )
        ComponentModel().beginUpdate.connect( self.modelToUpdate )
        ComponentModel().endUpdate.connect( self.modelUpdated )

        treeWidget = TreeWidget( rootView, 'Root tree' )
        widgets.addWidget( treeWidget, 3 )

        globalsEditWidget = GlobalsEditWidget()

        clipBoardWidget = TreeWidget( ClipBoardReorderWidget() )

        right, left = QtCore.Qt.RightDockWidgetArea, QtCore.Qt.LeftDockWidgetArea

        dockGlobals = QtGui.QDockWidget( 'Globals' )
        dockGlobals.setWidget( globalsEditWidget )
        dockGlobals.setAllowedAreas( right | left )

        dockClipBoard = QtGui.QDockWidget( 'Clip board' )
        dockClipBoard.setWidget( clipBoardWidget )
        dockClipBoard.setAllowedAreas( right | left )
        self.addDockWidget( left, dockGlobals )
        self.addDockWidget( right, dockClipBoard )

        viewMenu = menubar.addMenu( 'View' )
        viewTree = viewMenu.addAction( 'Root tree' )
        viewTree.setShortcut( QtGui.QKeySequence( 'Ctrl+Shift+T', QtGui.QKeySequence.NativeText ) )
        viewTree.setCheckable( True )
        viewTree.toggled.connect( treeWidget.setVisible )
        viewTree.trigger()
        viewMenu.addAction( dockGlobals.toggleViewAction() )
        dockGlobals.toggleViewAction().setShortcut( QtGui.QKeySequence( 'Ctrl+Shift+G', QtGui.QKeySequence.NativeText ) )
        viewMenu.addAction( dockClipBoard.toggleViewAction() )
        dockClipBoard.toggleViewAction().setShortcut( QtGui.QKeySequence( 'Ctrl+Shift+C', QtGui.QKeySequence.NativeText ) )

        viewMenu.addSeparator().setText( 'Tree item size' )

        sizeOptions = QtGui.QActionGroup( viewMenu )
        for size in ( 'Small', 'Medium', 'Big' ):
            action = sizeOptions.addAction( size )
            action.setCheckable( True )
            viewMenu.addAction( action )
        def triggered( action ):
            BaseColorDelegate.setSize( getattr( BaseColorDelegate, str( action.text() ).upper() ) )
        sizeOptions.triggered.connect( triggered )
        sizeOptions.actions()[0].trigger()

        centralWidget.layout().addLayout( widgets )

        self.setCentralWidget( centralWidget )

        labradConnection = LRConnectionManager( self )
        connectLabrad = menubar.addMenu( 'LabRAD' ).addAction( 'Connect' )
        connectLabrad.setShortcut( QtGui.QKeySequence( 'Ctrl+L', QtGui.QKeySequence.NativeText ) )
        connectLabrad.triggered.connect( labradConnection.connect )

        labradConnection.connectionChanged.connect( lambda connected: connectLabrad.setEnabled( not connected ) )
        labradConnection.connectionChanged.connect( lambda connected: status.setText( 'Connected to LabRAD' if connected else 'No LabRAD connection.' ) )
        labradConnection.connectionChanged.connect( lambda connected: self.connectionLost() if not connected else None )

        labradConnection.connectionFailed.connect( self.connectionLost )

        statusBar = self.statusBar()
        status = QtGui.QLabel( 'No LabRAD connection' )
        statusBar.addWidget( status )

        labradConnection.connect()

        quit = fileMenu.addAction( 'Quit' )
        quit.setShortcut( QtGui.QKeySequence( 'Ctrl+Q', QtGui.QKeySequence.NativeText ) )
        quit.triggered.connect( self.quitApplication )

    def connectionLost( self ):
        if QtGui.QMessageBox.warning( self.parent(),
                                      'No LabRAD connection',
                                      'You have no LabRAD connection, try to reconnect?',
                                      QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                      QtGui.QMessageBox.Ok ) == QtGui.QMessageBox.Ok:
            LRConnectionManager().connect()

    def editComponent( self, component ):
        d = self.dialogDict.get( type( component ) )
        if d:
            d = d( self, component )
            d.setAttribute( QtCore.Qt.WA_DeleteOnClose )
            d.exec_()

    def executeUnit( self, unit ):
        if ( not LRConnectionManager().connected and
             QtGui.QMessageBox.warning( self,
                                        'No connection',
                                        'No LabRAD connection, continue?',
                                        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                        defaultButton = QtGui.QMessageBox.Cancel ) == QtGui.QMessageBox.Cancel ): return
        self.setEnabled( False )
        menubar.setEnabled( False )
        d = execute.ExecuteDialog( self, unit )
        d.setAttribute( QtCore.Qt.WA_DeleteOnClose )
        d.show()
        d.finished.connect( lambda result: self.setEnabled( True ) or menubar.setEnabled( True ) or unit.initialize() or ComponentModel().update() )

    def modelToUpdate( self ):
        currentIndex = self.rootView.currentIndex()
        self.path = []
        while True:
            if not currentIndex.isValid(): break
            self.path.append( currentIndex.row() )
            currentIndex = currentIndex.parent()

    def modelUpdated( self ):
        currentIndex = QtCore.QModelIndex()
        while self.path:
            currentIndex = ComponentModel().index( self.path.pop(), 0, currentIndex )
            if not currentIndex.isValid(): return
        if currentIndex.isValid():
            self.rootView.expandTo( currentIndex )
            self.rootView.expand( currentIndex )
            self.rootView.setCurrentIndex( currentIndex )

    def mouseEvent( self, index ):
        EDIT, SAVE, EXECUTE = 'Edit', 'Save', 'Execute'
        if QtGui.QApplication.mouseButtons() == QtCore.Qt.RightButton:
            menu = QtGui.QMenu( self )
            component = ComponentModel().itemFromIndex( index ).component
            if self.dialogDict.get( type( component ) ):
                menu.addAction( EDIT )
            if IUnit.providedBy( component ):
                menu.addAction( SAVE )
                if component.configured:
                    menu.addAction( EXECUTE )
            action = menu.exec_( QtGui.QCursor.pos() )
            if action:
                { EDIT:self.editComponent, SAVE:_saveUnitAs, EXECUTE:self.executeUnit }[str( action.text() )]( component )

    @askToSave
    def quitApplication( self ):
        cxnMan = LRConnectionManager()
        if LRConnectionManager().connected:
            cxnMan.connectionChanged.disconnect( self.connectionLost )
            cxnMan.connection.disconnect()
        self.close()

class RootColorDelegate( BaseColorDelegate ):

    def __init__( self ):
        super( RootColorDelegate, self ).__init__()
        self.conditions.append( ( lambda component: IUnit.providedBy( component ) and not component.configured, 'red' ) )
        self.conditions.append( ( lambda component: type( component ) is Global, 'purple' ) )
        self.conditions.append( ( lambda component: type( component ) is Map, 'green' ) )
        self.conditions.append( ( lambda component: type( component ) is Result, 'blue' ) )




