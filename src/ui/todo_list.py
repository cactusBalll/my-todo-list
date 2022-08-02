from datetime import datetime
from PyQt5.QtCore import Qt, QSize, QMimeData
from PyQt5.QtGui import QIcon, QDrag, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QStackedWidget, QHBoxLayout, \
    QListWidgetItem, QLabel, QVBoxLayout, QMainWindow, QComboBox, QPushButton, QMenu, QAction

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

    def __init__(self, title: str, description: str, state: int, t: datetime, task: 'Task',
                 list_item: 'QListWidgetItem', *args, **kwargs) -> None:
        super(TodoItem, self).__init__(*args, **kwargs)
        self.list_item = list_item  # 与之绑定的list_item
        layout = QHBoxLayout()
        layout_left = QVBoxLayout()
        layout_right = QVBoxLayout()
        l = QLabel(title, parent=self)
        layout_left.addWidget(l)
        l = QLabel(description, parent=self)
        layout_left.addWidget(l)
        self.state = self.get_state_widget(state)
        layout_right.addWidget(self.state)
        l = QLabel("%d-%d-%d" % (t.year, t.month, t.day), parent=self)
        layout_right.addWidget(l)
        

        layout.addLayout(layout_left)
        layout.addLayout(layout_right)

        self.complete_button = QPushButton("已完成",self)
        layout.addWidget(self.complete_button)

        self.setLayout(layout)
        # 设置右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightClickMenu)

        self.task = task  # 保存对应任务的引用

    def rightClickMenu(self):
        """右键菜单"""
        self.rmenu = QMenu()

        self.action_edit = QAction("修改", self)
        self.action_edit.triggered.connect(self.rmenu_edit)

        self.action_important = QAction("设为重要", self)
        self.action_important.triggered.connect(self.rmenu_important)

        self.rmenu.addActions([self.action_edit, self.action_important])
        self.rmenu.popup(QCursor.pos())

    def rmenu_edit(self):
        pass

    def rmenu_important(self):
        pass

    def complete_buttpn_clicked(self):
        self.state.setText(TodoItem.str_table[TodoItem.COMPLETED])
        self.state.setStyleSheet("color: %s" %
                                 TodoItem.color_table[TodoItem.COMPLETED])
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
    def __init__(self,  *args, **kwargs) -> None:
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

    def view_changed(self, text: str):
        pass

    def create_new_task(self):
        pass


