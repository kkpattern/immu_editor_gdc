from PySide6 import QtWidgets


class DebugDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(DebugDialog, self).__init__(parent)
        self.setWindowTitle("Debug")
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

    def setTreeWidget(self, treeWidget):
        self.layout().addWidget(treeWidget)
