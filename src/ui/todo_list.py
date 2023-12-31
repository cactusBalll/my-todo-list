from datetime import datetime, timedelta
from typing import List
from src.core.storage import Storage
from .daily_list import DailyItem
from src.ui.task_edit import TaskEdit
from PyQt5.QtCore import Qt, QSize, QMimeData, pyqtSignal
from PyQt5.QtGui import QIcon, QDrag, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QStackedWidget, QHBoxLayout, \
    QListWidgetItem, QLabel, QVBoxLayout, QMainWindow, QComboBox, QPushButton, QMenu, QAction, \
    QMessageBox, QDialog

from ..core.user import User

from ..core.task import Task, TaskBuilder


class TodoItem(QWidget):
    NOT_START = 0
    NEAR_START = 1
    IN_PROGRESS = 2
    NEAR_DEADLINE = 3
    EXPIRED = 4
    COMPLETED = 5
    color_table = {
        NOT_START: "blue",
        NEAR_START: "cyan",
        IN_PROGRESS: "orange",
        NEAR_DEADLINE: "red",
        EXPIRED: "yellow",
        COMPLETED: "green"
    }
    str_table = {
        NOT_START: "未开始",
        NEAR_START: "即将开始",
        IN_PROGRESS: "进行中",
        NEAR_DEADLINE: "即将截止",
        EXPIRED: "已截止",
        COMPLETED: "已完成"
    }
    delete_me = pyqtSignal(QListWidgetItem)  # 删除自己信号
    refresh_list = pyqtSignal()  # 请求刷新列表

    def __init__(self, title: str, description: str, t: datetime, now: datetime, task: 'Task',
                 list_item: 'QListWidgetItem', *args, **kwargs) -> None:
        super(TodoItem, self).__init__(*args, **kwargs)

        if task.completed:
            state = TodoItem.COMPLETED
        else:
            state = TodoItem.get_state(t, task.deadline, now)
        self.list_item = list_item  # 与之绑定的list_item
        layout = QHBoxLayout()
        layout_left = QVBoxLayout()
        layout_right = QVBoxLayout()
        self.title = QLabel(title, parent=self)
        if task.importance >= 3:
            self.title.setStyleSheet("color: red")
        layout_left.addWidget(self.title)
        l = QLabel(description, parent=self)
        layout_left.addWidget(l)
        self.state = self.get_state_widget(state)
        layout_right.addWidget(self.state)
        l = QLabel("%d-%d-%d" % (t.year, t.month, t.day), parent=self)
        layout_right.addWidget(l)

        layout.addLayout(layout_left)
        layout.addLayout(layout_right)

        self.complete_button = QPushButton("已完成", self)
        self.complete_button.clicked.connect(self.complete_button_clicked)
        layout.addWidget(self.complete_button)

        self.setLayout(layout)
        # 设置右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightClickMenu)

        self.task = task  # 保存对应任务的引用

        self.show()

    @staticmethod
    def get_state(start: datetime, end: datetime, now: datetime) -> int:
        if now < start:
            if start - now < timedelta(hours=6):
                return TodoItem.NEAR_START
            else:
                return TodoItem.NOT_START
        elif start <= now and now < end:
            if end - now < timedelta(hours=6):
                return TodoItem.NEAR_DEADLINE
            else:
                return TodoItem.IN_PROGRESS
        else:
            return TodoItem.EXPIRED

    def rightClickMenu(self):
        """右键菜单"""
        self.rmenu = QMenu()

        self.action_edit = QAction("修改", self)
        self.action_edit.triggered.connect(self.rmenu_edit)

        self.action_important = QAction("设为重要", self)
        self.action_important.triggered.connect(self.rmenu_important)

        self.action_delete = QAction("删除", self)
        self.action_delete.triggered.connect(self.rmenu_delete)

        self.rmenu.addActions(
            [self.action_edit, self.action_important, self.action_delete])
        self.rmenu.popup(QCursor.pos())

    def rmenu_edit(self):
        # 对task的引用已经传递
        te = TaskEdit("编辑任务", self.task)
        te.task_edited.connect(self.task_edited)
        te.exec()

    def task_edited(self, task: Task):
        self.refresh_list.emit()

    def rmenu_important(self):
        self.task.importance = 3
        self.title.setStyleSheet("color: red")
        Storage.save()

    def rmenu_delete(self):
        cond = QMessageBox.question(
            self, "确认删除", "删除后可以在历史任务中找到", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if cond == QMessageBox.StandardButton.Yes:
            self.task.deleted = True
            self.delete_me.emit(self.list_item)
            Storage.save()

    def complete_button_clicked(self):
        self.state.setText(TodoItem.str_table[TodoItem.COMPLETED])
        self.state.setStyleSheet("color: %s" %
                                 TodoItem.color_table[TodoItem.COMPLETED])
        # 标记为已完成的项仍然会显示在界面上，切换时会清理掉
        self.task.set_completed()
        Storage.save()

    '''def mouseMoveEvent(self, e):
        # 用于拖拽
        # if e.buttons() != Qt.RightButton:
        #    return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())

        dropAction = drag.exec_(Qt.MoveAction)'''

    def get_state_widget(self, state: int) -> QLabel:

        l = QLabel(TodoItem.str_table[state], parent=self)
        l.setStyleSheet("color: %s" % TodoItem.color_table[state])
        return l


class TodoListPage(QWidget):
    sig_sync = pyqtSignal()

    def __init__(self, user: 'User', *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        layout = QVBoxLayout()
        tool_bar_layout = QHBoxLayout()

        self.new_task_button = QPushButton("新建任务", self)
        self.new_task_button.clicked.connect(self.create_new_task)
        tool_bar_layout.addWidget(self.new_task_button)

        # add
        self.new_task_button_c = QPushButton("今日任务安排", self)
        self.new_task_button_c.clicked.connect(self.schedule_tasks_auto)
        tool_bar_layout.addWidget(self.new_task_button_c)

        self.select_view_combo = QComboBox(self)

        self.select_view_combo.addItems(["本日", "本周", "本月", "全部"])
        self.select_view_combo.addItems(user.get_tags())
        self.select_view_combo.activated[str].connect(self.view_changed)
        self.select_view_combo.setCurrentIndex(0)
        tool_bar_layout.addWidget(self.select_view_combo)

        self.todo_list = QListWidget(self)
        layout.addWidget(self.todo_list)

        layout.addLayout(tool_bar_layout)
        self.setLayout(layout)

        self.user = user

        '''self.setStyleSheet("""
            QListWidgetItem {
                min-height: 120px
            }
        """)'''
        self.show()
        self.show_view(self.select_view_combo.currentText())

    def show_view(self, text: str):
        self.user.clear_completed()
        self.todo_list.clear()
        tasks = None
        if text == "本日":
            tasks = self.user.filter_task_day(datetime.now())
        elif text == "本周":
            tasks = self.user.filter_task_week(datetime.now())
        elif text == "本月":
            tasks = self.user.filter_task_month(datetime.now())
        elif text == "全部":
            tasks = self.user.tasks
        else:
            tasks = self.user.filter_by_tag(text)
        # if text == "自动":
        #     tasks = self.user.auto_schedule_tasks(datetime.now())

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
        self.show_view(self.select_view_combo.currentText())
        self.sig_sync.emit()

    def delete_item(self, item: QListWidgetItem):
        """从视图中删除列表项"""
        # 根据item得到它对应的行数
        row = self.todo_list.indexFromItem(item).row()
        # 删除item
        item = self.todo_list.takeItem(row)
        # 删除widget
        self.todo_list.removeItemWidget(item)
        self.sig_sync.emit()

    def view_changed(self, text: str):
        self.show_view(text)

    def create_new_task(self):
        te = TaskEdit("新建任务", TaskBuilder.get_empty_task())
        te.task_edited.connect(self.task_added)
        te.exec()

    def task_added(self, task: Task):
        self.user.add_task(task)
        self.show_view(self.select_view_combo.currentText())
        Storage.save()
        self.sig_sync.emit()

    def change_user(self, user: 'User'):
        self.user = user
        self.show_view(self.select_view_combo.currentText())

    def sync_task(self):
        self.user.clear_completed()
        self.select_view_combo.clear()
        self.select_view_combo.addItems(["本日", "本周", "本月", "全部"])
        self.select_view_combo.addItems(self.user.get_tags())
        self.show_view("本日")

    def schedule_tasks_auto(self):
        tasks = self.user.auto_schedule_tasks(datetime.now())
        '''self.todo_list.clear()
        for task in tasks:
            item = self.construct_list_item(task)
            self.todo_list.setItemWidget(item.list_item, item)'''
        d = DailySchedule(tasks)
        d.exec()

class ScheduleItem(QWidget):
    def __init__(self, task: 'Task', *args, **kwargs) -> None:
        super(ScheduleItem, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        self.task = task
        self.name = QLabel(task.title,self)

        self.start_time = QLabel(f"开始时间:{task.running_start_time}", self)
        self.start_time.setStyleSheet("color: blue")

        self.end_time = QLabel(f"结束时间:{task.running_end_time}", self)
        self.end_time.setStyleSheet("color: red")

        layout.addWidget(self.name)
        layout.addWidget(self.start_time)
        layout.addWidget(self.end_time)
        self.setLayout(layout)

         # 设置右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightClickMenu)
        self.show()
    def rightClickMenu(self):
        self.rmenu = QMenu()

        self.action_edit = QAction("详情", self)
        self.action_edit.triggered.connect(self.rmenu_edit)

        self.rmenu.addActions(
            [self.action_edit])
        self.rmenu.popup(QCursor.pos())
    
    def rmenu_edit(self):
        te = TaskEdit("任务详情", self.task)
        te.exec()
    
class DailySchedule(QDialog):
    def __init__(self, tasks: List['Task'], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        layout = QVBoxLayout()

        self.l = QListWidget(self)
        layout.addWidget(self.l)

        for task in tasks:
            widget = QListWidgetItem(self.l)
            widget.setSizeHint(QSize(60, 100))
            self.l.setItemWidget(widget, ScheduleItem(task,self.l))

        self.setLayout(layout)
        self.setGeometry(300,300,720,405)
        self.show()