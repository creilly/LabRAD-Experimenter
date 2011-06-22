'''
Created on Jun 11, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui
from ..components import Action, Scan, Sequence, Repeat, Conditional
import os
iconFileBase = os.path.join( os.path.dirname( globals()['__file__'] ), 'icons/' )
unitIcons = {}
for unit, name in {Action:'action', Scan:'scan', Sequence:'sequence', Repeat:'repeat', Conditional:'conditional'}.items():
    unitIcons[unit] = QtGui.QIcon( os.path.join( iconFileBase, '%s.svg' % name ) )
arrowIcons = {}
for arrow in ( 'up', 'down', 'plus', 'minus' ):
    arrowIcons[arrow] = QtGui.QIcon( os.path.join( iconFileBase, '%s.svg' % arrow ) )
