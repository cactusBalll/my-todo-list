from datetime import datetime, timedelta
import typing
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QStackedWidget, QHBoxLayout, \
    QListWidgetItem, QLabel, QMainWindow, QTabWidget,QPushButton
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
        #self.tab_widget.setGeometry(QRect(0, 0, 1366, 768))
        self.tab_widget.setLayoutDirection(Qt.LeftToRight)
        # 主窗口的布局方式和其他QWidget不同
        self.setCentralWidget(self.tab_widget)



        test_user = User("default")
        test_task = TaskBuilder.get_simple_task("DogCraft","game",datetime.now(),datetime.now()+timedelta(days=1))
        test_user.add_task(test_task)
        test_task = TaskBuilder.get_simple_task("WarCraft","game",datetime.now()+timedelta(days=1),datetime.now()+timedelta(days=2))
        test_user.add_task(test_task)

        self.todo_list = TodoListPage(test_user,) # TodoList
        self.tab_widget.addTab(self.todo_list, "TodoList")
        self.tab_widget.addTab(QLabel("f**k"),"233")
        
        self.setGeometry(300,300, 1366, 768)
        self.show()


