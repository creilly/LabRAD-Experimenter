'''
Created on May 1, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui, QtCore

from . import ComponentEditDialog
from ..inputselector import InputSelector
from ..component import updateModel

class InputLabel( QtGui.QLabel ):
    def __init__( self ):
        super( InputLabel, self ).__init__()
    def setInput( self, input = None ):
        self.setText( '<b>input</b>: %s' % ( repr( input ) if input else '<i>uninitialized</i>' ) )

class ParameterDialog( ComponentEditDialog ):
    def __init__( self, parent, component ):
        super( ParameterDialog, self ).__init__( parent, component, 'Edit Parameter: <i>%s</i>' % component.name )

        inputTab = QtGui.QWidget()

        vLayout = QtGui.QVBoxLayout( inputTab )
        inputLabel = self.inputLabel = InputLabel()
        inputLabel.setInput( component.input )

        hLayout = QtGui.QHBoxLayout()

        link = self.link = QtGui.QPushButton( 'Change input' )

        self.inputSelector = None
        self.getNewInputSelector()

        hLayout.addStretch()
        hLayout.addWidget( link )

        vLayout.addWidget( inputLabel, 1 )
        vLayout.addLayout( hLayout )

        self.tabWidget.addTab( inputTab, 'input' )

    def getNewInputSelector( self ):
        if self.inputSelector:
            self.inputSelector.deleteLater()
            self.link.clicked.disconnect( self.inputSelector.exec_ )
        self.inputSelector = InputSelector( self, self.component.input )
        self.inputSelector.inputSelected.connect( self.changeInput )
        self.link.clicked.connect( self.inputSelector.exec_ )

    @updateModel
    def changeInput( self, input ):
        self.component.input = input
        self.inputLabel.setInput( input )
        self.getNewInputSelector()

