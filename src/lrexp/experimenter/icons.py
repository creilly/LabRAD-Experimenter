'''
Loads the programs icons into memory.

Abstracts the need for modules that use icons to worry about their file location/type/etc.
'''
from PyQt4 import QtGui
from ..components import Action, Scan, Sequence, Repeat, Conditional, Input, Global, Map, Label, ArgumentList, Arguments, Result, ScanRange, NullUnit
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
                   Map:'map',
                   ScanRange:'scanrange',
                   ArgumentList:'argumentlist',
                   Arguments:'arguments',
                   Result:'result',
                   NullUnit:'nullunit'}.items():


    compIcons[unit] = QtGui.QIcon( os.path.join( iconFileBase, '%s.svg' % name ) )

arrowIcons = {}
for arrow in ( 'up', 'down', 'plus', 'minus' ):
    arrowIcons[arrow] = QtGui.QIcon( os.path.join( iconFileBase, '%s.svg' % arrow ) )

editIcon = QtGui.QIcon( os.path.join( iconFileBase, 'edit.svg' ) )
