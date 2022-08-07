from asyncio import Task
from datetime import date, datetime, timedelta
from src.core.storage import Storage
from src.core.task import TaskBuilder
from src.core.user import User
from src.core.util import QDate2Pydatetime, QDateTime2Pydatetime
from src.ui.task_edit import TaskEdit
from PyQt5.QtCore import Qt, QSize, QMimeData, pyqtSignal, QDate, QDateTime
from PyQt5.QtGui import QIcon, QDrag, QCursor,QTextCharFormat, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QStackedWidget, QHBoxLayout, \
    QListWidgetItem, QLabel, QVBoxLayout, QMainWindow, QComboBox, QPushButton, QMenu, QAction, \
    QMessageBox, QCalendarWidget

from src.ui.todo_list import TodoItem


class TodoCalender(QWidget):

    sig_sync = pyqtSignal()
    def __init__(self, user: 'User', *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        layout = QVBoxLayout()

        self.canlender = QCalendarWidget(self)
        self.todo_list = QListWidget(self)

        layout.addWidget(self.canlender)
        layout.addWidget(self.todo_list)

        self.setLayout(layout)

        self.user = user

        '''self.setStyleSheet("""
            QListWidgetItem {
                min-height: 120px
            }
        """)'''

        self.canlender.clicked.connect(self.view_changed)
        self.canlender.currentPageChanged.connect(lambda _y,_m:self.calender_task_coloring())
        self.default_text_style = self.canlender.dateTextFormat(date.today())
        self.calender_task_coloring()
        self.show()
        self.show_view(datetime.now())
        self.canlender.setSelectedDate(date.today())

    def show_view(self, date: datetime):
        self.user.clear_completed()
        self.todo_list.clear()
        tasks = self.user.filter_task_day(date)

        for task in tasks:
            item = self.construct_list_item(task)
            self.todo_list.setItemWidget(item.list_item, item)

    def construct_list_item(self, task: 'Task') -> TodoItem:
        widget = QListWidgetItem(self.todo_list)
        widget.setSizeHint(QSize(60, 100))
        ret = TodoItem(task.title, task.description, task.start_time,
                       datetime.now(), task, widget, parent=self.todo_list)
        ret.delete_me.connect(self.delete_item)
        ret.refresh_list.connect(self.refresh_view)
        return ret

    def refresh_view(self) -> None:
        self.show_view(QDate2Pydatetime(self.canlender.selectedDate()))

    def delete_item(self, item: QListWidgetItem):
        """从视图中删除列表项"""
        # 根据item得到它对应的行数
        row = self.todo_list.indexFromItem(item).row()
        # 删除item
        item = self.todo_list.takeItem(row)
        # 删除widget
        self.todo_list.removeItemWidget(item)
        self.sig_sync.emit()

    def view_changed(self, date: QDate):
        self.show_view(QDate2Pydatetime(date))


    def change_user(self, user: 'User'):
        self.user = user
        self.show_view(datetime.now())
        self.canlender.setSelectedDate(date.today())

    def calender_task_coloring(self):
        """用不同颜色标记有任务开始或者截止的日期"""
        fmtGreen = QTextCharFormat()
        fmtGreen.setBackground(QBrush(Qt.green))

        fmtOrange = QTextCharFormat()
        fmtOrange.setBackground(QBrush(QColor(252, 140, 28)))

        self.user.clear_completed()
        # clear

        for d in self.canlender.dateTextFormat().keys():
            self.canlender.setDateTextFormat(d,self.default_text_style)
    
        for task in self.user.tasks:
            start_time = task.start_time
            deadline = task.deadline
            self.canlender.setDateTextFormat(QDate(start_time.year,start_time.month,start_time.day),fmtGreen)
            self.canlender.setDateTextFormat(QDate(deadline.year,deadline.month,deadline.day),fmtOrange)

    def sync_task(self):
        self.show_view(datetime.now())
        self.canlender.setSelectedDate(date.today())
        self.calender_task_coloring()