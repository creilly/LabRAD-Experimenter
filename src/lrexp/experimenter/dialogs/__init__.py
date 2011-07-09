"""
Contains base classes for components and units (Unit is a subclass of Component)
"""
from PyQt4 import QtGui, QtCore

from zope.interface import Interface, implements

from ..editor import Editor, TextEditor
from ..component import ComponentModel, updateModel, ColorComponentModel
from ..reorderlist import IReorderList
from ..view import BaseListView, TreeView, TreeWidget
from ..clipboard import ClipBoardBrowser
from ...components import Unit

class ComponentEditDialog( QtGui.QDialog ):
    """
    Every component edit dialog has a tab that shows the component's place(s) in the root tree
    """
    class Title( QtGui.QLabel ):
        """
        Edit dialog's title
        """
        def setTitle( self, title ):
            self.setText( '<big><b>%s</b></big>' % title )

    def __init__( self, parent, component, title ):
        super( ComponentEditDialog, self ).__init__( parent )
        self.component = component
        self.setLayout( QtGui.QVBoxLayout() )
        self.title = self.Title()
        self.title.setTitle( title )
        self.tabWidget = QtGui.QTabWidget()
        self.layout().addWidget( self.title )
        self.layout().addWidget( self.tabWidget, 1 )

        view = self.matchView = TreeView()
        model = self.matchModel = ColorComponentModel()

        model.setRoot( ComponentModel().rootComponent )

        view.setModel( model )

        treeWidget = self.matchTreeWidget = TreeWidget( view )

        model.addCycler( view, component, treeWidget.addButton( 'Next match' ) )
        model.addColorCondition( component, 'red', QtGui.QFont.Bold )

        self.tabWidget.addTab( treeWidget, 'View' )

        ComponentModel().endUpdate.connect( self.updateModel )

    def updateModel( self ):
        self.matchModel.update()


class UnitDialog( ComponentEditDialog ):
    """
    Every unit in addition to a match view tab gets a name edit tab and a execution mode selection tab
    """
    def __init__( self, parent, component ):
        super( UnitDialog, self ).__init__( parent, component, 'Edit %s: <i>%s</i>' % ( type( component ).__name__, component.name ) )

        nameEdit = self.nameEdit = TextEditor( 'Edit name', 'Enter new unit name' )
        nameEdit.editCreated.connect( lambda edit: self.newUnitName( edit.value ) )
        nameEdit.setText( component.name )

        modeSelector = QtGui.QButtonGroup( self )
        modeSelectorWidget = QtGui.QWidget()
        modeSelectorWidget.setLayout( QtGui.QVBoxLayout() )

        for name, id, toolTip in  ( ( 'Probe', Unit.PROBE, 'Make each step as small as possible.' ),
                                    ( 'Step', Unit.STEP, 'Make each step a full round.' ),
                                    ( 'All', Unit.ALL, 'Execute entire unit in one step.' ) ):
            radio = QtGui.QRadioButton( name )
            radio.setToolTip( toolTip )
            modeSelector.addButton( radio, id )
            modeSelectorWidget.layout().addWidget( radio )

        modeSelectorWidget.layout().addStretch()
        modeSelector.buttonClicked[int].connect( self.modeSelected )

        modeSelector.button( self.component.mode ).click()

        self.tabWidget.insertTab( 0, nameEdit, 'Name' )
        self.tabWidget.addTab( modeSelectorWidget, 'Execution Mode' )

        self.layout().addWidget( self.tabWidget, 1 )

    @updateModel
    def modeSelected( self, mode ):
        self.component.mode = mode

    def newUnitName( self, name ):
        self.component.name = name
        ComponentModel().update()
        self.nameEdit.setText( name )
        self.title.setTitle( 'Edit %s: <i>%s</i>' % ( type( self.component ).__name__, name ) )
