from datetime import datetime, timedelta
import typing
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QStackedWidget, QHBoxLayout, \
    QListWidgetItem, QLabel, QMainWindow, QTabWidget
from qt_material import apply_stylesheet
import sys

from src.core.task import TaskBuilder
from src.core.user import User

from src.ui.todo_list import TodoListPage


class MainWindow(QMainWindow):
    """这是主窗口, app.exec_在这里,是程序入口"""

    def __init__(self) -> None:
        super().__init__()
        self.tab_widget = QTabWidget(self)  # 标签组件

        test_user = User("default")
        test_task = TaskBuilder.get_simple_task("DogCraft","game",datetime.now(),datetime.now()+timedelta(days=1))
        test_user.add_task(test_task)

        self.todo_list = TodoListPage(test_user,parent=self) # TodoList
        self.tab_widget.addTab(self.todo_list, "TodoList")
        self.show()


