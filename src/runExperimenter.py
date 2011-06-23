'''
Created on Jun 2, 2011

@author: christopherreilly
'''
def run():
    import sys
    from PyQt4 import QtGui
    a = QtGui.QApplication( [] )
    from lrexp.experimenter.mainwindow import MainWindow
    MainWindow().show()
    sys.exit( a.exec_() )

if __name__ == '__main__':
    run()
