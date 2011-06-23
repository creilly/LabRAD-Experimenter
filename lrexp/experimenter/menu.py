'''
Created on Apr 26, 2011

@author: christopherreilly
'''
from __future__ import with_statement
import os, pickle, inspect
from PyQt4 import QtGui, QtCore
from component import ComponentModel
from dialogs import getNewUnit, filedialog
from labradconnection import LRConnectionManager
from ..util import loadUnit, saveUnit
from .. import LREXPHOME

compModel = ComponentModel()
menubar = QtGui.QMenuBar()
fileMenu = menubar.addMenu( 'File' )
fileDialog = filedialog.getFileDialog( menubar )

def askToSave( f ):
    def saveAndExec( *args, **kwargs ):
        if compModel.rootComponent:
            response = QtGui.QMessageBox.warning( menubar,
                                                  'New unit',
                                                  'You are about to lose your old unit, would you like to save?',
                                                  buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                  defaultButton = QtGui.QMessageBox.Yes )
            if response == QtGui.QMessageBox.Escape: return
            if response == QtGui.QMessageBox.Yes: _saveRoot()
        f( *args[0:len( inspect.getargspec( f )[0] )], **kwargs )
    return saveAndExec

class RecentUnitsMenu( QtGui.QMenu ):
    currentFileChanged = QtCore.pyqtSignal( str )
    maxUnits = 6
    recentUnits = []
    currentFile = None

    class RecentUnit( QtGui.QAction ):
        def __init__( self, filename, parent ):
            super( RecentUnitsMenu.RecentUnit, self ).__init__( os.path.basename( filename ), parent )
            self.setToolTip( filename )
            self.triggered.connect( self._triggered )
            self.filename = filename

        @askToSave
        def _triggered( self ):
            compModel.setRoot( loadUnit( self.filename ) )
            recentUnits.addRecentUnit( self.filename )
    def __init__( self ):
        super( RecentUnitsMenu, self ).__init__( 'Recent units...' )
        recentsFilepath = self.recentsFilepath = os.path.join( os.environ[LREXPHOME], 'experiments/.recent.ini' )
        try:
            with open( recentsFilepath ) as file:
                recentUnits = pickle.load( file )
        except:
            recentUnits = []
        for recentUnit in recentUnits:
            self.addRecentUnit( recentUnit )

    def addRecentUnit( self, filename ):
        recentUnits = self.recentUnits
        matches = [i for i, fn in enumerate( [recentUnit.filename for recentUnit in recentUnits ] ) if fn == filename ]
        if matches:
            recentUnit = recentUnits.pop( matches[0] )
            self.removeAction( recentUnit )
        else:
            recentUnit = self.RecentUnit( filename, self )
        if recentUnits:
            self.insertAction( recentUnits[0], recentUnit )
        else:
            self.addAction( recentUnit )
        recentUnits.insert( 0, recentUnit )
        if len( recentUnits ) > self.maxUnits:
            self.removeAction( recentUnits.pop() )
        with open( self.recentsFilepath, 'w' ) as file:
            l = [recentUnit.filename for recentUnit in recentUnits]
            l.reverse()
            pickle.dump( l, file )
        self.currentFile = filename
        self.currentFileChanged.emit( filename )

    def newFile( self ):
        self.currentFile = None
        self.currentFileChanged.emit( '' )

newRoot = fileMenu.addAction( 'New root' )
saveRoot = fileMenu.addAction( 'Save root' )
saveRootAs = fileMenu.addAction( 'Save root as...' )
loadRoot = fileMenu.addAction( 'Load root' )
recentUnits = RecentUnitsMenu()
fileMenu.addMenu( recentUnits )

@askToSave
def _newRoot():
    newUnit = getNewUnit()
    if not newUnit: return
    compModel.setRoot( newUnit )
    recentUnits.newFile()

def _saveUnitAs( unit ):
    fileDialog.setAcceptMode( fileDialog.AcceptSave )
    fileDialog.setWindowTitle( 'Save root unit' )
    if fileDialog.exec_():
        filename = str( fileDialog.selectedFiles()[0] )
        saveUnit( unit, filename )
        recentUnits.addRecentUnit( filename )

def _saveRoot():
    unit = compModel.rootComponent
    filename = recentUnits.currentFile
    if filename:
        saveUnit( unit, filename )
        return
    _saveRootAs()

def _saveRootAs():
    _saveUnitAs( compModel.rootComponent )

@askToSave
def _loadRoot():
    fileDialog.setAcceptMode( fileDialog.AcceptOpen )
    fileDialog.setWindowTitle( 'Load root unit' )
    if fileDialog.exec_():
        filename = str( fileDialog.selectedFiles()[0] )
        compModel.setRoot( loadUnit( filename ) )
        recentUnits.addRecentUnit( filename )

newRoot.triggered.connect( _newRoot )
saveRoot.triggered.connect( _saveRoot )
saveRoot.setEnabled( False )
compModel.endUpdate.connect( lambda: saveRoot.setEnabled( bool( compModel.rootComponent ) ) )
saveRootAs.triggered.connect( _saveRootAs )
saveRootAs.setEnabled( False )
compModel.endUpdate.connect( lambda: saveRootAs.setEnabled( bool( compModel.rootComponent ) ) )

loadRoot.triggered.connect( _loadRoot )
