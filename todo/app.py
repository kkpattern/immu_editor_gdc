from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from pyrsistent import pvector
import qdarktheme

from framework.data import DataManager
from framework.debug import generate_view_data
from framework.view import DebugView

from todo.data import TodoAppData
from todo.debug import ColorHistoryView
from todo.view import RootView


class TodoApp(object):
    def __init__(self):
        self._debug_data = None
        self._data_manager = DataManager(TodoAppData(todo_list=pvector()))

        self._qt_app = QtWidgets.QApplication([])
        self._qt_app.setStyleSheet(qdarktheme.load_stylesheet())
        self._root_view = RootView(self._todo_data_updated)

        self._debug_view = DebugView()
        self._color_history_view = ColorHistoryView()

        self._setup_menu(self._root_view.widget.menuBar())

        self._update_timer = QtCore.QTimer()
        self._update_timer.timeout.connect(self._update)

    def _setup_menu(self, menubar):
        self._undo = QtGui.QAction("Undo")
        self._undo.setShortcut("ctrl+z")
        self._undo.triggered.connect(self._data_manager.undo)

        self._redo = QtGui.QAction("Redo")
        self._redo.setShortcut("ctrl+y")
        self._redo.triggered.connect(self._data_manager.redo)

        edit_menu = menubar.addMenu('&Edit')
        edit_menu.addAction(self._undo)
        edit_menu.addAction(self._redo)

        self._view_tree = QtGui.QAction("View tree")
        self._view_tree.triggered.connect(self._show_view_tree)

        self._color_history = QtGui.QAction("Color history")
        self._color_history.triggered.connect(self._show_color_history)

        debug_menu = menubar.addMenu('&Debug')
        debug_menu.addAction(self._view_tree)
        debug_menu.addAction(self._color_history)

    def _show_view_tree(self):
        self._debug_view.widget.show()

    def _show_color_history(self):
        self._color_history_view.widget.show()

    def exec_(self):
        self._root_view.widget.show()
        self._update()
        self._update_timer.start(33)
        return self._qt_app.exec_()

    def _update(self):
        self._root_view.try_refresh(self._data_manager.get_data())
        self._debug_data = generate_view_data(self._root_view,
                                              self._debug_data)
        self._debug_view.try_refresh(self._debug_data)
        color_history = []
        for record in reversed(self._data_manager.history):
            if record.todo_list:
                color_history.append(record.todo_list[0].color)
        self._color_history_view.try_refresh(color_history)

    def _todo_data_updated(self, new_todo_data, record_in_history=True):
        self._data_manager.push_data(new_todo_data,
                                     record_in_history=record_in_history)
