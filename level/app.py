from PySide6 import QtCore
from PySide6 import QtWidgets

from pyrsistent import pmap
import qdarktheme

from framework.data import DataManager

from level.data import LevelData
from level.view import RootView


class LevelDesigner(object):
    def __init__(self):
        self._data_manager = DataManager(LevelData(objects=pmap({})))
        self._qt_app = QtWidgets.QApplication([])
        self._qt_app.setStyleSheet(qdarktheme.load_stylesheet())

        self._root_view = RootView(self._level_data_updated,
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

    def _level_data_updated(self, new_level_data, record_in_history=True):
        self._data_manager.push_data(new_level_data,
                                     record_in_history=record_in_history)
