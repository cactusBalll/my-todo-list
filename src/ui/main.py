from datetime import datetime, timedelta
from src.core.storage import Storage
from src.ui.calender import TodoCalender
from src.ui.user_config import UserConfigPage
from src.ui.history_task import HistoryTaskPage
import typing
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QStackedWidget, QHBoxLayout, \
    QListWidgetItem, QLabel, QMainWindow, QTabWidget, QPushButton
from qt_material import apply_stylesheet
import sys

from src.core.task import TaskBuilder
from src.core.user import User

from src.ui.todo_list import TodoListPage


class MainWindow(QMainWindow):
    """这是主窗口, app.exec_在这里,是程序入口"""

    def __init__(self, s: Storage, user_name: str) -> None:
        """传入user_name作为初始用户"""
        super().__init__()

        self.tab_widget = QTabWidget(self)  # 标签组件
        #self.tab_widget.setGeometry(QRect(0, 0, 1366, 768))
        self.tab_widget.setLayoutDirection(Qt.LeftToRight)
        # 主窗口的布局方式和其他QWidget不同
        self.setCentralWidget(self.tab_widget)

        #test_user = User("default")
        #test_task = TaskBuilder.get_simple_task("DogCraft","game",datetime.now(),datetime.now()+timedelta(days=1))
        # test_user.add_task(test_task)
        #test_task = TaskBuilder.get_simple_task("WarCraft","game",datetime.now()+timedelta(days=1),datetime.now()+timedelta(days=2))
        # test_user.add_task(test_task)

        self.todo_list = TodoListPage(
            s.get_user_by_name(user_name),)  # TodoList
        self.history_list = HistoryTaskPage(s.get_user_by_name(user_name),)
        self.user_config = UserConfigPage(s, user_name)
        self.user_config.sig_user_change.connect(self.change_user)

        self.calender = TodoCalender(s.get_user_by_name(user_name))

        self.todo_list.sig_sync.connect(self.sync_task)
        self.history_list.sig_sync.connect(self.sync_task)
        self.calender.sig_sync.connect(self.sync_task)

        
        self.tab_widget.addTab(self.todo_list, "TodoList")
        self.tab_widget.addTab(self.history_list, "历史任务")
        self.tab_widget.addTab(self.calender, "日历")
        self.tab_widget.addTab(self.user_config, "用户设置")

        self.setGeometry(300, 300, 1366, 768)
        self.show()

    def change_user(self, user: 'User'):
        self.todo_list.change_user(user)
        self.history_list.change_user(user)
        self.calender.change_user(user)

    def sync_task(self):
        """将task数据的变化和GUI同步"""
        self.todo_list.sync_task()
        self.history_list.sync_task()
        self.calender.sync_task()