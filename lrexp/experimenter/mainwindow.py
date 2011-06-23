'''
Created on Apr 26, 2011

@author: christopherreilly
'''

import os

from PyQt4 import QtGui, QtCore

from component import ComponentModel
from globals import GlobalsEditWidget
from menu import menubar, recentUnits, askToSave, _saveUnitAs
from view import TreeView, TreeWidget
from delegate import BaseColorDelegate
from dialogs import UnitDialog, input, sequence, parameter, componentgroup, scan, action, execute
from labradconnection import LRConnectionManager

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
        executeRoot.setEnabled( False )
        executeRoot.triggered.connect( lambda: self.executeUnit( ComponentModel().rootComponent ) )
        ComponentModel().endUpdate.connect( lambda: executeRoot.setEnabled( ComponentModel().rootComponent.configured ) )

        centralWidget = QtGui.QWidget()
        centralWidget.setLayout( QtGui.QVBoxLayout() )

        titleLabel = TitleLabel()

        recentUnits.currentFileChanged.connect( titleLabel.newFile )

        centralWidget.layout().addWidget( titleLabel )

        widgets = QtGui.QHBoxLayout()

        rootView = self.rootView = TreeView()
        rootView.pressed.connect( self.mouseEvent )
        rootView.setModel( ComponentModel() )
        rootView.setItemDelegate( RootColorDelegate() )
        rootView.doubleClicked.connect( lambda index: self.editComponent( rootView.model().itemFromIndex( index ).component ) )
        ComponentModel().beginUpdate.connect( self.modelToUpdate )
        ComponentModel().endUpdate.connect( self.modelUpdated )
        treeWidget = TreeWidget( rootView, 'Root tree' )
        widgets.addWidget( treeWidget, 3 )
        globalsEditWidget = GlobalsEditWidget()
        widgets.addWidget( globalsEditWidget , 2 )

        viewMenu = menubar.addMenu( 'View' )
        viewTree = viewMenu.addAction( 'Root tree' )
        viewTree.setCheckable( True )
        viewTree.toggled.connect( treeWidget.setVisible )
        viewGlobals = viewMenu.addAction( 'Globals' )
        viewGlobals.setCheckable( True )
        viewGlobals.toggled.connect( globalsEditWidget.setVisible )
        viewTree.setChecked( True )
        viewGlobals.setChecked( True )

        centralWidget.layout().addLayout( widgets )

        self.setCentralWidget( centralWidget )

        labradConnection = LRConnectionManager( self )
        connectLabrad = menubar.addMenu( 'LabRAD' ).addAction( 'Connect' )
        connectLabrad.triggered.connect( labradConnection.connect )
        labradConnection.connectionMade.connect( lambda: connectLabrad.setEnabled( False ) )

        labradConnection.connectionLost.connect( lambda: connectLabrad.setEnabled( True ) )

        labradConnection.connectionLost.connect( self.connectionLost )
        labradConnection.connectionFailed.connect( self.connectionLost )
        statusBar = self.statusBar()
        status = QtGui.QLabel( 'No LabRAD connection' )
        statusBar.addWidget( status )
        labradConnection.connectionMade.connect( lambda: status.setText( 'Connected to LabRAD' ) )
        labradConnection.connectionLost.connect( lambda: status.setText( 'No LabRAD connection' ) )
        labradConnection.connect()

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
            d( self, component ).exec_()

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
            if self.dialogDict.get( type( component ) ) is None: return
            menu.addAction( EDIT )
            if IUnit.providedBy( component ):
                menu.addAction( SAVE )
                if component.configured:
                    menu.addAction( EXECUTE )
            action = menu.exec_( QtGui.QCursor.pos() )
            if action:
                { EDIT:self.editComponent, SAVE:_saveUnitAs, EXECUTE:self.executeUnit }[str( action.text() )]( component )

class RootColorDelegate( BaseColorDelegate ):
    def __init__( self ):
        super( RootColorDelegate, self ).__init__()
        self.conditions.append( ( lambda component: IUnit.providedBy( component ) and not component.configured, 'red' ) )
        self.conditions.append( ( lambda component: type( component ) is Global, 'purple' ) )
        self.conditions.append( ( lambda component: type( component ) is Map, 'green' ) )
        self.conditions.append( ( lambda component: type( component ) is Result, 'blue' ) )

