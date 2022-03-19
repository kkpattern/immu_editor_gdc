import pickle
import time

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from pyrsistent import pmap
import qdarktheme

from framework.data import DataManager
from framework.debug import generate_view_data
from framework.view import DebugView

from level.data import LevelData
from level.data import TreeData
from level.data import HouseData
from level.data import MountainData
from level.view import RootView


class ActionPlayer(object):
    def __init__(self, data_manager, status_bar, get_open_file):
        self._data_manager = data_manager
        self._data_history = []
        self._index = -1
        self._time = 0
        self._status_widget = QtWidgets.QLabel("Playing")
        status_bar.addPermanentWidget(self._status_widget)
        self._status_widget.hide()
        self._get_open_file = get_open_file

    def play(self, filename=None):
        if filename is None:
            filename = self._get_open_file()
        if filename:
            with open(filename, "rb") as f:
                data_history = pickle.load(f)
            self._data_history = [
                (LevelData.create(d), t) for (d, t) in data_history]
            self._time = 0
            self._index = -1
            self._next()

    def _next(self):
        if self._index >= 0:
            data, timestamp = self._data_history[self._index]
            self._data_manager.push_data(data)
        next_action = self._index+1
        if next_action < len(self._data_history):
            data, timestamp = self._data_history[next_action]
            self._index += 1
            QtCore.QTimer.singleShot((timestamp-self._time)*1000, self._next)
            self._time = timestamp
            self._status_widget.show()
        else:
            self._index = -1
            self._time = 0
            self._status_widget.hide()


class ActionRecorder(object):
    def __init__(self, status_bar, get_save_file):
        self._start_at = None
        self._recording_data = None
        self._status_widget = QtWidgets.QLabel("Recording")
        status_bar.addPermanentWidget(self._status_widget)
        self._status_widget.hide()
        self._get_save_file = get_save_file

    @property
    def in_recording(self):
        return self._start_at is not None

    def data_updated(self, data, record_in_history=True):
        if self._start_at is not None:
            self._recording_data.append((data.serialize(),
                                         time.time()-self._start_at))

    def toggle(self):
        if self.in_recording:
            if self._recording_data:
                file_name = self._get_save_file()
                if file_name:
                    with open(file_name, "wb") as f:
                        pickle.dump(self._recording_data, f)
                self._recording_data = None
            self._start_at = None
            self._status_widget.hide()
        else:
            self._start_at = time.time()
            self._recording_data = []
            self._status_widget.show()


class LevelDesigner(object):
    def __init__(self, test_case=None):
        self._data_manager = DataManager(LevelData(objects=pmap({})))
        self._qt_app = QtWidgets.QApplication([])
        self._qt_app.setStyleSheet(qdarktheme.load_stylesheet())

        self._root_view = RootView(self._level_data_updated)

        status_bar = self._root_view.widget.statusBar()
        self._action_player = ActionPlayer(
            self._data_manager,
            status_bar,
            lambda: QtWidgets.QFileDialog.getOpenFileName(
                filter="*.record")[0])
        self._action_recorder = ActionRecorder(
            status_bar,
            lambda: QtWidgets.QFileDialog.getSaveFileName(
                filter="*.record")[0])

        self._setup_menu(self._root_view.widget.menuBar())

        self._update_timer = QtCore.QTimer()
        self._update_timer.timeout.connect(self._update)

        self._debug_data = None
        self._debug_view = DebugView()

        if test_case is not None:
            self._action_player.play(test_case)

    def _setup_menu(self, menubar):
        self._undo = QtGui.QAction("Undo")
        self._undo.setShortcut("ctrl+z")
        self._undo.triggered.connect(self._data_manager.undo)

        self._redo = QtGui.QAction("Redo")
        self._redo.setShortcut("ctrl+y")
        self._redo.triggered.connect(self._data_manager.redo)

        edit_menu = menubar.addMenu('&Edit')

        add_menu = QtWidgets.QMenu("Add")

        self._add_actions = {}

        for type_ in ["Tree", "House", "Mountain"]:
            self._add_actions[type_] = self._create_add_action(add_menu, type_)

        edit_menu.addMenu(add_menu)
        edit_menu.addAction(self._undo)
        edit_menu.addAction(self._redo)

        debug_menu = menubar.addMenu('&Debug')

        self._view_tree = QtGui.QAction("View tree")
        self._view_tree.triggered.connect(self._show_view_tree)
        debug_menu.addAction(self._view_tree)

        self._record_action_toggle = QtGui.QAction("Record action")
        self._record_action_toggle.triggered.connect(
            self._toggle_record_action)
        debug_menu.addAction(self._record_action_toggle)

        self._play = QtGui.QAction("Play action")
        self._play.triggered.connect(self._action_player.play)
        debug_menu.addAction(self._play)

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

    def _level_data_updated(self, new_level_data, record_in_history=True):
        self._data_manager.push_data(new_level_data,
                                     record_in_history=record_in_history)
        self._action_recorder.data_updated(new_level_data)

    def _create_add_action(self, menu, type_):
        action = QtGui.QAction(type_)
        action.triggered.connect(
            lambda: self._add_object_callback(type_))
        menu.addAction(action)
        return action

    def _add_object_callback(self, type_):
        level_data = self._data_manager.get_data()
        objects = level_data.objects
        if objects:
            new_id = max(objects.iterkeys())+1
        else:
            new_id = 1
        factory = {
            "Tree": TreeData,
            "House": HouseData,
            "Mountain": MountainData}[type_]
        new_objects = objects.set(new_id, factory(id_=new_id))
        new_level_data = level_data.set("objects", new_objects)
        self._level_data_updated(new_level_data)

    def _show_view_tree(self):
        self._debug_view.widget.show()

    def _toggle_record_action(self):
        self._action_recorder.toggle()
        if self._action_recorder:
            self._record_action_toggle.setText("Stop recording")
        else:
            self._record_action_toggle.setText("Record action")
