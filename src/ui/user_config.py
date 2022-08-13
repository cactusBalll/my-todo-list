from datetime import datetime, timedelta
from src.core.user import User
from typing import List
from src.core.storage import Storage
from src.ui.task_edit import TaskEdit
from PyQt5.QtCore import Qt, QSize, QMimeData, pyqtSignal
from PyQt5.QtGui import QIcon, QDrag, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QStackedWidget, QHBoxLayout, \
    QListWidgetItem, QLabel, QVBoxLayout, QMainWindow, QComboBox, QPushButton, QMenu, QAction, \
    QMessageBox, QDialog, QInputDialog


class UserConfigPage(QWidget):
    """用户配置页面"""
    sig_user_change = pyqtSignal(User)
    sig_theme_change = pyqtSignal()

    def __init__(self, s: Storage, name: str,
                 *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        layout = QVBoxLayout()

        self.s = s
        self.current_user = s.get_user_by_name(name)
        self.name_label = QLabel(self.current_user.name, self)
        self.name_label.setStyleSheet("font: 42px; margin-bottom: 150px")
        layout.addWidget(self.name_label)

        t = (len(self.current_user.tasks) + len(self.current_user.history_tasks))
        all_task_num =  t if t > 0 else 1
        complete_ratio = len(list(filter(lambda t:t.completed, self.current_user.history_tasks))) / all_task_num
        self.cp_ratio_lb = QLabel(f"当前任务完成率:{complete_ratio*100:.2f}%")
        self.cp_ratio_lb.setStyleSheet("font: 36px;")
        layout.addWidget(self.cp_ratio_lb)

        self.rename_btn = QPushButton("修改用户名",self)
        self.rename_btn.clicked.connect(self.user_renaming)
        self.rename_btn.setStyleSheet("margin-right: 300px")
        layout.addWidget(self.rename_btn)

        self.btn0 = QPushButton("切换用户", self)
        self.btn0.clicked.connect(self.user_changing)
        self.btn0.setStyleSheet("margin-right: 300px")
        layout.addWidget(self.btn0)

        self.btn1 = QPushButton("创建新用户", self)
        self.btn1.clicked.connect(self.user_creating)
        self.btn1.setStyleSheet("margin-right: 300px")
        layout.addWidget(self.btn1)

        self.btn2 = QPushButton("切换暗色主题", self)
        self.btn2.clicked.connect(self.theme_changing)
        self.btn2.setStyleSheet("margin-right: 300px")
        layout.addWidget(self.btn2)


        self.setLayout(layout)

    def calcu_cp_ratio(self):
        t = (len(self.current_user.tasks) + len(self.current_user.history_tasks))
        all_task_num =  t if t > 0 else 1
        complete_ratio = len(list(filter(lambda t:t.completed, self.current_user.history_tasks))) / all_task_num
        return complete_ratio

    def user_changing(self):
        self.change_user_dialog = ChangeUserDialog(self.s.get_user_names(), self)
        self.change_user_dialog.user_changed.connect(self.user_changed)
        self.change_user_dialog.exec()

    def user_changed(self, user_name: str):
        self.sig_user_change.emit(self.s.get_user_by_name(user_name))
        self.name_label.setText(user_name)
        self.current_user = self.s.get_user_by_name(user_name)
        self.cp_ratio_lb.setText(f"当前任务完成率:{self.calcu_cp_ratio()*100:.2f}%")

    def user_renaming(self):
        text, ok = QInputDialog.getText(self,"输入名字","输入新用户名")
        if ok:
            self.current_user.name = text
            self.name_label.setText(text)

    def user_creating(self):
        text, ok = QInputDialog.getText(self,"创建并切换到新用户","输入新用户名")
        if ok:
            self.current_user = User(text)
            self.s.users.append(self.current_user)
            self.name_label.setText(text)
            self.sig_user_change.emit(self.current_user)
            self.s.save()

    def theme_changing(self):
        self.sig_theme_change.emit()

    def sync_task(self):
        self.cp_ratio_lb.setText(f"当前任务完成率:{self.calcu_cp_ratio()*100:.2f}%")

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
            self, "确认切换", f"将切换用户为{user}", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if cond == QMessageBox.StandardButton.Yes:
            self.user_changed.emit(user)
            self.accept()

    def cancel(self):
        self.reject()
