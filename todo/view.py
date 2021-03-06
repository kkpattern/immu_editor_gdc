from PySide6 import QtCore
from PySide6 import QtWidgets

from framework.view import ViewBase
from framework.view import ListViewBase

from todo.data import TodoItemData


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
    def __init__(self, submit_data_callback):
        super(RootView, self).__init__(submit_data_callback)

    def _create_child_view(self):
        self._input_view = TodoInputView(self._todo_list_updated)
        self.bind_child_view(self._input_view,
                             lambda todo_app_data: todo_app_data.todo_list)

        self._counter_view = TodoCounterView()
        self.bind_child_view(self._counter_view,
                             lambda todo_app_data: todo_app_data.todo_list)

        self._list_view = TodoListView(self._todo_list_updated)
        self.bind_child_view(self._list_view,
                             lambda todo_app_data: todo_app_data.todo_list)

    def _create_widget(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        widget.setLayout(layout)
        widget.setFocusPolicy(QtCore.Qt.ClickFocus)
        # Add widgets of child view into layout.
        layout.addWidget(self._input_view.widget)
        layout.addWidget(self._counter_view.widget)
        layout.addWidget(self._list_view.widget)
        main_window = QtWidgets.QMainWindow()
        main_window.setMinimumSize(330, 419)
        main_window.setWindowTitle("Todo")
        main_window.setCentralWidget(widget)

        return main_window

    def _todo_list_updated(self, new_todo_list, record_in_history=True):
        current_data = self.get_current_data()
        new_data = current_data.set("todo_list", new_todo_list)
        self.submit_data(new_data, record_in_history=record_in_history)


class TodoInputView(ViewBase):
    def _create_widget(self):
        input_widget = QtWidgets.QLineEdit()
        input_widget.editingFinished.connect(self._new_todo)
        return input_widget

    def _new_todo(self):
        current_data = self.get_current_data()
        if current_data is not self.UNINTIALIZED:
            content = self.widget.text()
            if content:
                new_item = TodoItemData(done=False,
                                        content=content,
                                        color="#FFFFFF")
                new_data = current_data.append(new_item)
                self.submit_data(new_data)
                self.widget.setText("")


class TodoCounterView(ViewBase):
    def _create_widget(self):
        return QtWidgets.QLabel()

    def refresh(self, todo_list):
        todo_count = len(todo_list)
        done_count = sum([1 if item.done else 0 for item in todo_list])
        self.widget.setText(f"{done_count}/{todo_count}")


class TodoItemView(ViewBase):
    def _create_widget(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignLeft)
        widget.setLayout(layout)
        self._done_checkbox = QtWidgets.QCheckBox()
        self._done_checkbox.toggled.connect(self._done_changed)
        layout.addWidget(self._done_checkbox)
        self._content_edit = QtWidgets.QLineEdit()
        self._content_edit.setReadOnly(True)
        layout.addWidget(self._content_edit)
        self._push_button = QtWidgets.QPushButton()
        self._push_button.setFlat(True)
        self._push_button.setFixedSize(10, 18)
        self._push_button.clicked.connect(self._pick_label_color)
        layout.addWidget(self._push_button)
        return widget

    def refresh(self, data):
        self._done_checkbox.setChecked(data.done)
        self._push_button.setStyleSheet(LABEL_BUTTON.format(color=data.color))
        self._content_edit.setText(data.content)

    def _done_changed(self, value):
        current_data = self.get_current_data()
        if current_data is not self.UNINTIALIZED and (
                current_data.done != value):
            new_data = current_data.set("done", value)
            self.submit_data(new_data)

    def _pick_label_color(self):
        dialog = QtWidgets.QColorDialog(self.widget)
        dialog.show()

        def current_color_changed(color):
            current_data = self.get_current_data()
            new_data = current_data.set("color", color.name())
            self.submit_data(new_data, False)
        dialog.currentColorChanged.connect(current_color_changed)

        def color_selected(color):
            current_data = self.get_current_data()
            new_data = current_data.set("color", color.name())
            self.submit_data(new_data, True)
        dialog.colorSelected.connect(color_selected)

        origin_color = self.get_current_data().color
        if not dialog.exec_():
            current_data = self.get_current_data()
            if current_data.color != origin_color:
                new_data = current_data.set("color", origin_color)
                self.submit_data(new_data)


class TodoListView(ListViewBase):
    def __init__(self, submit_data_callback=None):
        super(TodoListView, self).__init__(TodoItemView, submit_data_callback)

    def _create_widget(self):
        list_widget = QtWidgets.QWidget()
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setAlignment(QtCore.Qt.AlignTop)
        self._layout.setContentsMargins(0, 0, 0, 0)
        list_widget.setLayout(self._layout)
        return list_widget

    def _create_element_view(self):
        view = self._element_view_factory(
            lambda new_v, record_in_history=True: self._update_triggered(
                self._get_element_view_index(view), new_v, record_in_history))
        return view

    def _insert_item(self, index, item):
        self._layout.insertWidget(index, item)

    def _take_item(self, index):
        item = self._layout.takeAt(index)
        item.widget().deleteLater()

    def _update_triggered(self, index, new_value, record_in_history=True):
        current_data = self.get_current_data()
        if current_data is not self.UNINTIALIZED:
            new_data = current_data.set(index, new_value)
            self.submit_data(new_data, record_in_history=record_in_history)

    def _generate_key_list(self, data_list):
        return [item.id_ for item in data_list]

    def _get_data_at(self, index, key, data_collection):
        return data_collection[index]
