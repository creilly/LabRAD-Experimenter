'''
Created on Jun 5, 2011

@author: christopherreilly
'''
import os
from PyQt4 import QtGui
from ... import LREXPHOME
def getFileDialog( parent ):
    fileDialog = QtGui.QFileDialog( parent, 'LabRAD File Dialog', os.path.join( os.environ[LREXPHOME], 'experiments' ), 'labRAD experiments (*.lre)' )
    fileDialog.setOption( fileDialog.DontUseNativeDialog, True )
    fileDialog.setDefaultSuffix( 'lre' )
    return fileDialog
