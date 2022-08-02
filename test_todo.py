


from datetime import datetime
import sys

from PyQt5.QtCore import Qt, QSize, QMimeData
from PyQt5.QtGui import QIcon, QDrag
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QStackedWidget, QHBoxLayout, \
    QListWidgetItem, QLabel, QVBoxLayout, QMainWindow, QComboBox, QPushButton, QMenu, QAction
from src.core.task import Task, TaskBuilder

from src.ui.todo_list import TodoItem
import unittest

from qt_material import apply_stylesheet
class Test(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # self.statusBar().showMessage('Ready')
        vbox = QVBoxLayout()
        t1 = TodoItem("StarCraft", "play",
                      TodoItem.NEAR_START, datetime.now(), TaskBuilder.get_empty_task(), QListWidgetItem(), self,)
        t2 = TodoItem("DogCraft", "play",
                      TodoItem.IN_PROGRESS, datetime.now(),  TaskBuilder.get_empty_task(), QListWidgetItem(), self,)
        t3 = TodoItem("StarCraft", "dog",
                      TodoItem.EXPIRED, datetime.now(), TaskBuilder.get_empty_task(), QListWidgetItem(), self,)
        vbox.addWidget(t1)
        vbox.addWidget(t2)
        vbox.addWidget(t3)
        self.setLayout(vbox)
        self.setGeometry(300, 300, 250, 150)
        # self.setWindowTitle('Statusbar')
        self.show()


class TestItem(unittest.TestCase):
    def test_item(self):

        app = QApplication(sys.argv)
        apply_stylesheet(app, "dark_blue.xml")

        test = Test()
        sys.exit(app.exec_())


'''class Test233(unittest.TestCase):
    def test_fk(self):
        print('fk')

class TestTask(unittest.TestCase):
    def test_creation(self):
        task = TaskBuilder.get_simple_task('233', '233', None, None)
        print(task)
'''

if __name__ == "__main__":
    unittest.main()
