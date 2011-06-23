from PyQt4.QtCore import pyqtSlot

def lambdaSlot( qObject, types, lambdaFunction ):
    if not hasattr( qObject, '_lambdaSlots' ):
        qObject._lambdaSlots = []
    slot = pyqtSlot( *types )( lambdaFunction )
    qObject._lambdaSlots.append( slot )
    return slot

