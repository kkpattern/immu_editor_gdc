from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from framework.view import ViewBase
from framework.view import ListViewBase
from framework.view import FormEditViewBase

from level.data import Vector2


LABEL_BUTTON = """
QPushButton:pressed {{
    background-color: {color};
}}
QPushButton {{
    background-color: {color}; border: 1px solid black;
    border-radius: 1px;
}}
QPushButton:disabled {{
    background-color: {color};
}}
"""


class RootView(ViewBase):
    def _create_child_view(self):
        self._scene_view = SceneView(self._on_objects_changed)
        self.bind_child_view(self._scene_view,
                             lambda level_data: level_data.objects)
        self._object_list_view = ObjectListView(self._on_objects_changed)
        self.bind_child_view(self._object_list_view,
                             lambda level_data: level_data.objects)
        self._attr_edit_view = AttrEditView(self._on_object_attr_changed)
        self.bind_child_view(self._attr_edit_view, self._get_selected_object)

    def _get_selected_object(self, level_data):
        object_ = None
        for each in level_data.objects.itervalues():
            if each.is_selected:
                object_ = each
                break
        return object_

    def _create_widget(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)
        widget.setLayout(layout)
        widget.setFocusPolicy(QtCore.Qt.ClickFocus)
        # Add widgets of child view into layout.
        self._object_list_view.widget.setMaximumWidth(160)
        layout.addWidget(self._object_list_view.widget)
        self._scene_view.widget.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding)
        layout.addWidget(self._scene_view.widget)
        self._attr_edit_view.widget.setMinimumWidth(250)
        layout.addWidget(self._attr_edit_view.widget)

        main_window = QtWidgets.QMainWindow()
        main_window.setWindowTitle("Level Designer")
        main_window.setCentralWidget(widget)
        return main_window

    def _on_objects_changed(self, new_objects, record_in_history=True):
        new_level_data = self.get_current_data().set("objects", new_objects)
        self.submit_data(new_level_data, record_in_history=record_in_history)

    def _on_object_attr_changed(self, new_object, record_in_history=True):
        level_data = self.get_current_data()
        new_objects = level_data.objects.set(new_object.id_, new_object)
        new_level_data = level_data.set("objects", new_objects)
        self.submit_data(new_level_data, record_in_history=record_in_history)


class ObjectListItemView(ViewBase):
    def _create_widget(self):
        self._label = QtWidgets.QListWidgetItem()
        return self._label

    def refresh(self, data):
        self._label.setText("{0} {1}".format(data.type_, data.id_))


class ObjectListView(ListViewBase):
    def __init__(self, submit_data_callback=None):
        super().__init__(lambda: ObjectListItemView(),
                         submit_data_callback)

    def _create_widget(self):
        widget = super()._create_widget()
        widget.setSelectionMode(
            QtWidgets.QListWidget.SelectionMode.ExtendedSelection)
        widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        widget.customContextMenuRequested.connect(self._context_menu)
        return widget

    def _context_menu(self, pos):
        self._menu = QtWidgets.QMenu(self.widget)
        remove_action = QtGui.QAction(u"remove")
        remove_action.triggered.connect(self._remove_selected)
        self._menu.addAction(remove_action)
        self._menu.exec_(QtGui.QCursor.pos())

    def _remove_selected(self):
        new_objects = None
        objects = self.get_current_data()
        for key, value in objects.iteritems():
            if value.is_selected:
                new_objects = objects.remove(key)
                break
        if new_objects is not None:
            self.submit_data(new_objects)

    def _generate_key_list(self, data):
        if data is self.UNINTIALIZED:
            result = []
        else:
            result = sorted(data.iterkeys())
        return result

    def _get_data_at(self, index, key, data_collection):
        return data_collection[key]

    def _on_selection_changed(self, index):
        items = self.widget.selectedItems()
        selected_rows = [self.widget.row(i) for i in items]
        selected_ids = [self._current_key_list[i] for i in selected_rows]
        dirty_object = {}
        data = self.get_current_data()
        for id_, object_ in data.iteritems():
            if object_.is_selected and id_ not in selected_ids:
                dirty_object[id_] = object_.set("is_selected", False)
            elif id_ in selected_ids and not object_.is_selected:
                dirty_object[id_] = object_.set("is_selected", True)
        if dirty_object:
            evolver = data.evolver()
            for key, value in dirty_object.items():
                evolver.set(key, value)
            self.submit_data(evolver.persistent())

    def refresh(self, data):
        super().refresh(data)
        current_selection = None
        for i, key in enumerate(self._current_key_list):
            object_ = self._get_data_at(i, key, data)
            if object_.is_selected:
                current_selection = i
                break
        if current_selection is not None:
            if current_selection != self.widget.currentRow():
                self.widget.setCurrentRow(current_selection)
        else:
            self.widget.clearSelection()


class ObjectItem(QtWidgets.QGraphicsItem):
    BORDER_SIZE = 2

    def __init__(self, pixmap_path, select_callback, pos_changed_callback):
        super().__init__()
        self._pixmap = QtGui.QPixmap(pixmap_path)
        self._width = self._pixmap.width()
        self._height = self._pixmap.height()
        self._enable_border = False
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self._select_callback = select_callback
        self._pos_changed_callback = pos_changed_callback
        self._pos_value = None

    def setEnableBorder(self, flag):
        if self._enable_border != flag:
            self._enable_border = flag
            self.update()

    def boundingRect(self):
        return QtCore.QRectF(-self._width/2-self.BORDER_SIZE,
                             -self._height/2-self.BORDER_SIZE,
                             self._width+self.BORDER_SIZE*2,
                             self._height+self.BORDER_SIZE*2)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawPixmap(-self._width/2, -self._height/2, self._pixmap)
        if self._enable_border:
            painter.setPen(
                QtGui.QPen(QtGui.QBrush(QtGui.QColor("yellow"),
                                        QtCore.Qt.SolidPattern),
                           self.BORDER_SIZE))
            painter.drawRoundedRect(-self._width/2,
                                    -self._height/2,
                                    self._width,
                                    self._height,
                                    5,
                                    5)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
            self._pos_value = value
            self._pos_changed_callback(value, record_in_history=False)
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        self._select_callback()
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self._pos_value is not None:
            value, self._pos_value = self._pos_value, None
            self._pos_changed_callback(value, record_in_history=True)
        return super().mouseReleaseEvent(event)


class SceneObjectView(ViewBase):
    TEXTURE = {
        "Tree": "res/treePine_large.png",
        "House": "res/house.png",
        "Mountain": "res/rockGrey_large.png",
    }

    SIMULATED_LOADING_TIME = {
        "Tree": 10,
        "House": 100,
        "Mountain": 10000,
    }

    def __init__(self,
                 scene,
                 data,
                 load_finish_callback,
                 submit_data_callback):
        super().__init__(submit_data_callback)
        self._scene = scene
        self.set_current_data(data)
        loading_pixmap = QtGui.QPixmap("res/timer_CW_75.png")
        loading_icon = self._scene.addPixmap(loading_pixmap)
        loading_icon.setPos(data.pos.x-loading_pixmap.width()/2,
                            data.pos.y-loading_pixmap.height()/2)

        def _on_object_loaded():
            object_ = ObjectItem(
                self.TEXTURE[data.type_],
                self._on_selected,
                self._on_object_pos_changed)
            self._scene.addItem(object_)
            self._scene.removeItem(loading_icon)
            object_.setPos(data.pos.x, data.pos.y)
            self._widget = object_
            load_finish_callback(data, self._widget)
        # Simulate an async loading.
        QtCore.QTimer.singleShot(self.SIMULATED_LOADING_TIME[data.type_],
                                 _on_object_loaded)

    def _create_widget(self):
        pass

    def refresh(self, new_data):
        self._widget.setPos(new_data.pos.x, new_data.pos.y)
        self._widget.setEnableBorder(new_data.is_selected)

    def _on_selected(self):
        if not self._in_refresh:
            object_data = self.get_current_data()
            if not object_data.is_selected:
                new_object_data = object_data.set("is_selected", True)
                self.submit_data(new_object_data)

    def _on_object_pos_changed(self, pos, record_in_history):
        if not self._in_refresh:
            object_data = self.get_current_data()
            new_object_data = object_data.set("pos",
                                              Vector2(x=pos.x(), y=pos.y()))
            self.submit_data(new_object_data,
                             record_in_history=record_in_history)


class SceneView(ViewBase):
    SCENE_WIDTH = 640
    SCENE_HEIGHT = 640

    def __init__(self, submit_data_callback=None):
        super(SceneView, self).__init__(submit_data_callback)
        self._id_to_view = {}
        self._loading = False

    def _create_widget(self):
        self._scene = QtWidgets.QGraphicsScene()
        brush = QtGui.QBrush(QtGui.QColor("darkgrey"),
                             QtCore.Qt.SolidPattern)
        self._scene.setBackgroundBrush(brush)
        self._scene.setSceneRect(-self.SCENE_WIDTH/2,
                                 -self.SCENE_HEIGHT/2,
                                 self.SCENE_WIDTH,
                                 self.SCENE_HEIGHT)
        self._view = QtWidgets.QGraphicsView(self._scene)
        self._view.setMinimumSize(500, 500)
        return self._view

    def should_refresh(self, new_data, current_data):
        if not self._loading:
            result = super().should_refresh(new_data, current_data)
        else:
            result = False
        return result

    def should_refresh_children(self):
        if not self._loading:
            result = super().should_refresh_children()
        else:
            result = False
        return result

    def refresh(self, data):
        self._loading = True
        old_data = self.get_old_data()
        if old_data is self.UNINTIALIZED:
            old_data = {}
        for id_ in old_data:
            if id_ not in data:
                object_view = self._id_to_view.pop(id_)
                self._scene.removeItem(object_view.widget)
                self.unbind_child_view(object_view)
        new_objects = []
        for id_ in data:
            if id_ not in old_data:
                new_objects.append(id_)
        if new_objects:
            loading_ids = set(new_objects)
            for id_ in new_objects:
                object_view = SceneObjectView(
                    self._scene,
                    data[id_],
                    lambda object_data, object_: self._on_object_loaded(
                        object_data, object_, loading_ids),
                    self._on_object_data_changed)
                self.bind_child_view(object_view,
                                     lambda data, id_=id_: data[id_])
                self._id_to_view[id_] = object_view
        else:
            self._finish_refresh()

    def _on_object_loaded(self, object_data, object_, loading_ids):
        loading_ids.remove(object_data.id_)
        if not loading_ids:
            self._finish_refresh()

    def _finish_refresh(self):
        self._loading = False

    def _on_object_data_changed(self, new_object_data, record_in_history=True):
        old_objects = self.get_current_data()
        old_object_data = old_objects[new_object_data.id_]
        dirty_object = {new_object_data.id_: new_object_data}
        if new_object_data.is_selected and not old_object_data.is_selected:
            data = self.get_current_data()
            for id_, object_ in data.iteritems():
                if object_.is_selected and id_ != new_object_data.id_:
                    dirty_object[id_] = object_.set("is_selected", False)
        evolver = old_objects.evolver()
        for key, value in dirty_object.items():
            evolver.set(key, value)
        self.submit_data(evolver.persistent(),
                         record_in_history=record_in_history)

    def submit_data(self, new_data, record_in_history=True):
        if not self._in_refresh and not self._loading:
            self.set_current_data(new_data)
            self.refresh(new_data)
            super().submit_data(new_data, record_in_history=record_in_history)


class Vector2EditView(ViewBase):
    def _create_widget(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        widget.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        self._x_input = QtWidgets.QSpinBox()
        self._x_input.setMinimum(-640)
        self._x_input.setMaximum(640)
        layout.addWidget(self._x_input)
        self._x_input.valueChanged.connect(lambda i: self._set_value("x", i))

        self._y_input = QtWidgets.QSpinBox()
        self._y_input.setMinimum(-640)
        self._y_input.setMaximum(640)
        layout.addWidget(self._y_input)
        self._y_input.valueChanged.connect(lambda i: self._set_value("y", i))
        return widget

    def refresh(self, data):
        self._x_input.setValue(data.x)
        self._y_input.setValue(data.y)

    def _set_value(self, attr, value):
        current_data = self.get_current_data()
        if current_data.get(attr) != value:
            new_data = current_data.set(attr, value)
            self.submit_data(new_data)


class AttrEditView(ViewBase):
    def _create_child_view(self):
        self._inner_view = AttrEditInnerView(self.submit_data)
        self.bind_child_view(self._inner_view, lambda data: data)

    def _create_widget(self):
        widget = QtWidgets.QGroupBox("Attribute")
        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.addWidget(self._inner_view.widget)
        return widget


class AttrEditInnerView(FormEditViewBase):
    def init_item_edit(self):
        self.append_item_edit("Position:", "pos", Vector2EditView)

    def try_refresh(self, data):
        if data is not self.get_current_data() and data is None:
            self.widget.setVisible(False)
        else:
            self.widget.setVisible(True)
            super().try_refresh(data)
