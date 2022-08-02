from datetime import datetime, timedelta
from PyQt5.QtCore import Qt, QSize, QMimeData, pyqtSignal
from PyQt5.QtGui import QIcon, QDrag, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QStackedWidget, QHBoxLayout, \
    QListWidgetItem, QLabel, QVBoxLayout, QMainWindow, QComboBox, QPushButton, QMenu, QAction, \
    QMessageBox

from ..core.user import User

from ..core.task import Task


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

        self.action_delete = QAction("删除", self.rmenu_edit)
        self.action_delete.triggered.connect(self.rmenu_delete)

        self.rmenu.addActions([self.action_edit, self.action_important])
        self.rmenu.popup(QCursor.pos())

    def rmenu_edit(self):
        pass

    def rmenu_important(self):
        self.task.importance = 3
        self.title.setStyleSheet("color: red")

    def rmenu_delete(self):
        cond = QMessageBox.question(
            self, "确认删除", "删除后可以在历史任务中找到", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if cond == QMessageBox.StandardButton.Yes:
            self.task.deleted = True
            TodoItem.delete_me.emit(self.list_item)

    def complete_buttpn_clicked(self):
        self.state.setText(TodoItem.str_table[TodoItem.COMPLETED])
        self.state.setStyleSheet("color: %s" %
                                 TodoItem.color_table[TodoItem.COMPLETED])
        # 标记为已完成的项仍然会显示在界面上，切换时会清理掉
        self.task.set_completed()

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

        l = QLabel(TodoItem.str_table[state], parent=self)
        l.setStyleSheet("color: %s" % TodoItem.color_table[state])
        return l


class TodoListPage(QWidget):
    def __init__(self, user: 'User', *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        layout = QVBoxLayout()
        tool_bar_layout = QHBoxLayout()

        self.new_task_button = QPushButton(self)
        self.new_task_button.clicked.connect(self.create_new_task)
        tool_bar_layout.addWidget(self.new_task_button)

        self.select_view_combo = QComboBox(self)
        self.select_view_combo.addItems(["本日", "本周", "本月", "全部"])
        self.select_view_combo.activated[str].connect(self.view_changed)
        tool_bar_layout.addWidget(self.select_view_combo)

        self.todo_list = QListWidget(self)
        layout.addWidget(self.todo_list)

        layout.addLayout(tool_bar_layout)
        self.setLayout(layout)

        self.user = user

        self.show()

    def show_view(self, text: str):
        self.user.clear_completed()
        self.todo_list.clear()
        tasks = None
        if text == "本日":
            tasks = self.user.filter_task_day(datetime.now())
        if text == "本周":
            tasks = self.user.filter_task_week(datetime.now())
        if text == "本月":
            tasks = self.user.filter_task_month(datetime.now())
        if text == "全部":
            tasks = self.user.tasks

        for task in tasks:
            item = self.construct_list_item(task)
            self.todo_list.setItemWidget(item.list_item, item)

    def construct_list_item(self, task: 'Task') -> TodoItem:
        widget = QListWidgetItem(self.todo_list)
        ret = TodoItem(task.title, task.description, task.start_time,
                       datetime.now(), task, widget, parent=self.todo_list)
        ret.delete_me.connect(self.delete_item)
        return ret

    def delete_item(self, item: QListWidgetItem):
        """从视图中删除列表项"""
        # 根据item得到它对应的行数
        row = self.todo_list.indexFromItem(item).row()
        # 删除item
        item = self.todo_list.takeItem(row)
        # 删除widget
        self.todo_list.removeItemWidget(item)

    def view_changed(self, text: str):
        self.show_view(text)

    def create_new_task(self):
        pass
