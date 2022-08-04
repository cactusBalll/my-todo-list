
from datetime import datetime, timedelta
from src.ui.task_edit import TaskEdit
from PyQt5.QtCore import Qt, QSize, QMimeData, pyqtSignal
from PyQt5.QtGui import QIcon, QDrag, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QStackedWidget, QHBoxLayout, \
    QListWidgetItem, QLabel, QVBoxLayout, QMainWindow, QComboBox, QPushButton, QMenu, QAction, \
    QMessageBox

from ..core.user import User

from ..core.task import Task, TaskBuilder


class HistoryTodoItem(QWidget):
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
    delete_me = pyqtSignal(QListWidgetItem, Task)  # 删除自己信号
    refresh_list = pyqtSignal()  # 请求刷新列表
    add_to_todo = pyqtSignal(Task)

    def __init__(self, title: str, description: str, t: datetime, now: datetime, task: 'Task',
                 list_item: 'QListWidgetItem', *args, **kwargs) -> None:
        super(HistoryTodoItem, self).__init__(*args, **kwargs)

        if task.completed:
            state = HistoryTodoItem.COMPLETED
        else:
            state = HistoryTodoItem.get_state(t, task.deadline, now)
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
                return HistoryTodoItem.NEAR_START
            else:
                return HistoryTodoItem.NOT_START
        elif start <= now and now < end:
            if end - now < timedelta(hours=6):
                return HistoryTodoItem.NEAR_DEADLINE
            else:
                return HistoryTodoItem.IN_PROGRESS
        else:
            return HistoryTodoItem.EXPIRED

    def rightClickMenu(self):
        """右键菜单"""
        self.rmenu = QMenu()

        self.action_edit = QAction("恢复任务", self)
        self.action_edit.triggered.connect(self.rmenu_edit)

        self.action_delete = QAction("删除", self)
        self.action_delete.triggered.connect(self.rmenu_delete)

        self.rmenu.addActions(
            [self.action_edit, self.action_delete])
        self.rmenu.popup(QCursor.pos())

    def rmenu_edit(self):
        # 对task的引用已经传递
        cond = QMessageBox.information(self, "恢复任务", "这将把此任务加回到任务列表中")
        #print(cond == QMessageBox.StandardButton.Ok)
        if cond == QMessageBox.StandardButton.Ok:
            te = TaskEdit("恢复任务", self.task)
            te.task_edited.connect(self.task_edited)
            te.exec()

    def task_edited(self, task: Task):
        task.deleted = False
        task.completed = False
        self.add_to_todo.emit(task)
        self.delete_me.emit(self.list_item, task)
        self.refresh_list.emit()

    def rmenu_delete(self):
        cond = QMessageBox.question(
            self, "确认删除", "这将彻底删除这项任务", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if cond == QMessageBox.StandardButton.Yes:
            self.task.deleted = True
            self.delete_me.emit(self.list_item, self.task)

    def mouseMoveEvent(self, e):
        # 用于拖拽
        # if e.buttons() != Qt.RightButton:
        #    return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())

        dropAction = drag.exec_(Qt.MoveAction)

    def get_state_widget(self, state: int) -> QLabel:

        l = QLabel(HistoryTodoItem.str_table[state], parent=self)
        l.setStyleSheet("color: %s" % HistoryTodoItem.color_table[state])
        return l


class HistoryTaskPage(QWidget):
    def __init__(self, user: 'User', *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        layout = QVBoxLayout()
        tool_bar_layout = QHBoxLayout()

        self.select_view_combo = QComboBox(self)

        self.select_view_combo.addItems(["本日", "本周", "本月", "全部"])
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

    def show_view(self, text: str):
        self.user.clear_completed()
        self.todo_list.clear()
        tasks = None
        if text == "本日":
            tasks = self.user.filter_task_day(datetime.now(), history=True)
        if text == "本周":
            tasks = self.user.filter_task_week(datetime.now(), history=True)
        if text == "本月":
            tasks = self.user.filter_task_month(datetime.now(), history=True)
        if text == "全部":
            tasks = self.user.history_tasks

        for task in tasks:
            item = self.construct_list_item(task)
            self.todo_list.setItemWidget(item.list_item, item)

    def construct_list_item(self, task: 'Task') -> HistoryTodoItem:
        widget = QListWidgetItem(self.todo_list)
        widget.setSizeHint(QSize(60, 100))
        ret = HistoryTodoItem(task.title, task.description, task.start_time,
                              datetime.now(), task, widget, parent=self.todo_list)
        ret.delete_me.connect(self.delete_item)
        ret.refresh_list.connect(self.refresh_view)
        ret.add_to_todo.connect(self.add_to_todo)
        return ret

    def refresh_view(self) -> None:
        self.show_view(self.select_view_combo.currentText())

    def delete_item(self, item: QListWidgetItem, task: 'Task'):
        """从视图中删除列表项"""
        # 根据item得到它对应的行数
        row = self.todo_list.indexFromItem(item).row()
        # 删除item
        item = self.todo_list.takeItem(row)
        # 删除widget
        self.todo_list.removeItemWidget(item)
        self.user.history_tasks.remove(task)

    def add_to_todo(self, task: Task):
        self.user.add_task(task)

    def view_changed(self, text: str):
        self.show_view(text)
