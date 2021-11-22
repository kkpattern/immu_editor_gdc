from PySide6 import QtCore
from PySide6 import QtWidgets

from pyrsistent import pvector

from framework.data import DataManager

from todo.data import TodoAppData
from todo.view import RootView


class TodoApp(object):
    def __init__(self):
        self._data_manager = DataManager(TodoAppData(todo_list=pvector()))
        self._qt_app = QtWidgets.QApplication([])
        self._root_view = RootView(self._todo_data_updated,
                                   self._data_manager.undo,
                                   self._data_manager.redo)
        self._update_timer = QtCore.QTimer()
        self._update_timer.timeout.connect(self._update)

    def exec_(self):
        self._root_view.widget.show()
        self._update()
        self._update_timer.start(33)
        return self._qt_app.exec_()

    def _update(self):
        self._root_view.try_refresh(self._data_manager.get_data())

    def _todo_data_updated(self, new_todo_data, record_in_history=True):
        self._data_manager.push_data(new_todo_data,
                                     record_in_history=record_in_history)
