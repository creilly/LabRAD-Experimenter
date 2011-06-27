'''
Created on May 25, 2011

@author: christopherreilly
'''
from __future__ import with_statement
from PyQt4 import QtGui, QtCore

from . import UnitDialog, getUnit, ComponentReorderList
from ..reorderlist import ReorderWidget, IReorderList
from ..view import BaseListView
from ..component import ComponentModel, updateModel
from ..icons import compIcons

from ...components import Sequence

from twisted.python import components

class SequenceReorder( ComponentReorderList ):
    def __init__( self, sequenceUnit ):
        super( SequenceReorder, self ).__init__( sequenceUnit.sequence )
        self.sequenceUnit = sequenceUnit

    @updateModel
    def addItem( self ):
        unit = getUnit( self.sequenceUnit )
        if not unit: return
        self.beginInsertRows( QtCore.QModelIndex(), len( self.pyList ), len( self.pyList ) )
        self.pyList.append( unit )
        self.endInsertRows()

    def data( self, index, role ):
        if index.isValid() and role == QtCore.Qt.DecorationRole:
            return compIcons[type( self.pyList[index.row()] )]
        return super( SequenceReorder, self ).data( index, role )

components.registerAdapter( SequenceReorder, Sequence, IReorderList )

class SequenceDialog( UnitDialog ):
    def __init__( self, parent, component ):
        super( SequenceDialog, self ).__init__( parent, component )

        self.tabWidget.insertTab( 0, ReorderWidget( component ), 'Sequence' )
        self.tabWidget.setCurrentIndex( 0 )
