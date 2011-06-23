'''
Created on Jun 11, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui
from ..components import Action, Scan, Sequence, Repeat, Conditional, Input, Global, Map
import os
iconFileBase = os.path.join( os.path.dirname( globals()['__file__'] ), 'icons/' )
compIcons = {}
for unit, name in {Action:'action',
                   Scan:'scan',
                   Sequence:'sequence',
                   Repeat:'repeat',
                   Conditional:'conditional',
                   Input:'input',
                   Global:'global',
                   Map:'map'}.items():


    compIcons[unit] = QtGui.QIcon( os.path.join( iconFileBase, '%s.svg' % name ) )

arrowIcons = {}
for arrow in ( 'up', 'down', 'plus', 'minus' ):
    arrowIcons[arrow] = QtGui.QIcon( os.path.join( iconFileBase, '%s.svg' % arrow ) )
