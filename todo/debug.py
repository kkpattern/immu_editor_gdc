from PySide6 import QtCore
from PySide6 import QtWidgets

from framework.view import ViewBase
from framework.view import ListViewBase


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


class ColorView(ViewBase):
    def _create_widget(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        widget.setLayout(layout)
        self._push_button = QtWidgets.QPushButton()
        self._push_button.setFlat(True)
        self._push_button.setFixedSize(50, 18)
        layout.addWidget(self._push_button)
        return widget

    def refresh(self, color):
        self._push_button.setStyleSheet(LABEL_BUTTON.format(color=color))


class ColorHistoryView(ListViewBase):
    def __init__(self, submit_data_callback=None):
        super(ColorHistoryView, self).__init__(ColorView, submit_data_callback)

    def _create_widget(self):
        list_widget = QtWidgets.QWidget()
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setAlignment(QtCore.Qt.AlignTop)
        self._layout.setContentsMargins(0, 0, 0, 0)
        list_widget.setLayout(self._layout)

        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Color History")
        layout = QtWidgets.QVBoxLayout()
        dialog.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QtWidgets.QScrollArea(dialog)
        scroll_area.setWidget(list_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        layout.addWidget(scroll_area)
        return dialog

    def _create_element_view(self):
        view = self._element_view_factory(
            lambda new_v, record_in_history=True: self._update_triggered(
                self._get_element_view_index(view), new_v, record_in_history))
        return view

    def _insert_item(self, index, item):
        self._layout.insertWidget(index, item)
        self._layout.invalidate()

    def _take_item(self, index):
        item = self._layout.takeAt(index)
        item.widget().setParent(None)

    def _update_triggered(self, index, new_value, record_in_history=True):
        pass

    def _generate_key_list(self, data_list):
        return data_list

    def _get_data_at(self, index, key, data_collection):
        return data_collection[index]
