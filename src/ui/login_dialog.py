from datetime import datetime, timedelta
from src.core.user import User
from typing import List
from src.core.storage import Storage
from src.ui.main import MainWindow
from src.ui.task_edit import TaskEdit
from PyQt5.QtCore import Qt, QSize, QMimeData, pyqtSignal
from PyQt5.QtGui import QIcon, QDrag, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QStackedWidget, QHBoxLayout, \
    QListWidgetItem, QLabel, QVBoxLayout, QMainWindow, QComboBox, QPushButton, QMenu, QAction, \
    QMessageBox, QDialog, QInputDialog

class LoginDialog(QWidget):
    """登录对话框"""
    user_changed = pyqtSignal(str)

    def __init__(self, s: Storage, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.s = s
        names = s.get_user_names()
        self.names = names
        layout = QVBoxLayout()

        self.combo_box = QComboBox(self)
        self.combo_box.addItems(names)
        self.combo_box.setCurrentIndex(0)

        self.create_btn = QPushButton("创建新用户",self)
        self.create_btn.clicked.connect(self.creating_new_user)
        
        
        layout.addWidget(self.combo_box)
        layout.addWidget(self.create_btn)
        self.btn0 = QPushButton("确认", self)
        self.btn0.clicked.connect(self.confirm)
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.btn0)

        layout.addLayout(hlayout)

        self.setLayout(layout)
        self.setGeometry(300, 300, 360, 198)
        self.show()

    def confirm(self):
        user = self.combo_box.currentText()
        self.main_window = MainWindow(self.s, user)
        self.hide()
        self.main_window.show()

    def creating_new_user(self):
        text, ok = QInputDialog.getText(self,"创建新用户","输入新用户名")
        if ok:
            self.s.users.append(User(text))
            self.s.save()
            self.combo_box.addItem(text)