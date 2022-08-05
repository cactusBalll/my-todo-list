from datetime import datetime, timedelta
from src.core.user import User
from typing import List
from src.core.storage import Storage
from src.ui.task_edit import TaskEdit
from PyQt5.QtCore import Qt, QSize, QMimeData, pyqtSignal
from PyQt5.QtGui import QIcon, QDrag, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QStackedWidget, QHBoxLayout, \
    QListWidgetItem, QLabel, QVBoxLayout, QMainWindow, QComboBox, QPushButton, QMenu, QAction, \
    QMessageBox, QDialog


class UserConfigPage(QWidget):
    """用户配置页面"""
    sig_user_change = pyqtSignal(User)

    def __init__(self, s: Storage, name: str,
                 *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        layout = QVBoxLayout()

        self.s = s
        self.current_user = s.get_user_by_name(name)
        self.name_label = QLabel(self.current_user.name, self)
        self.name_label.setStyleSheet("font: 42px")
        layout.addWidget(self.name_label)

        self.btn0 = QPushButton("切换用户", self)
        self.btn0.clicked.connect(self.user_changing)

        self.setLayout(layout)

    def user_changing(self):
        self.change_user_dialog = ChangeUserDialog(self.s.get_user_names(), self)
        self.change_user_dialog.user_changed.connect(self.user_changed)
        self.change_user_dialog.exec()

    def user_changed(self, user_name: str):
        self.sig_user_change.emit(self.s.get_user_by_name(user_name))


class ChangeUserDialog(QDialog):
    """切换用户对话框"""
    user_changed = pyqtSignal(str)

    def __init__(self, names: List[str], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.names = names
        layout = QVBoxLayout()

        self.combo_box = QComboBox(self)
        self.combo_box.addItems(names)
        self.combo_box.setCurrentIndex(0)
        layout.addWidget(self.combo_box)

        self.btn0 = QPushButton("确认", self)
        self.btn0.clicked.connect(self.confirm)
        self.btn1 = QPushButton("取消", self)
        self.btn1.clicked.connect(self.cancel)
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.btn0)
        hlayout.addWidget(self.btn1)

        layout.addLayout(hlayout)

        self.setLayout(layout)

    def confirm(self):
        user = self.combo_box.currentText()
        cond = QMessageBox.question(
            self, f"确认切换", "将切换用户为{user}", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if cond == QMessageBox.StandardButton.Yes:
            self.user_changed.emit(user)
            self.accept()

    def cancel(self):
        self.reject()
