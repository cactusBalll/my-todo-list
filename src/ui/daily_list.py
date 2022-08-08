import copy
from datetime import date, datetime, timedelta
from src.core.storage import Storage
from src.ui.task_edit import DailyTaskEdit, TaskEdit
from PyQt5.QtCore import Qt, QSize, QMimeData, pyqtSignal
from PyQt5.QtGui import QIcon, QDrag, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QStackedWidget, QHBoxLayout, \
    QListWidgetItem, QLabel, QVBoxLayout, QMainWindow, QComboBox, QPushButton, QMenu, QAction, \
    QMessageBox

from ..core.user import User

from ..core.task import Task, TaskBuilder, Trigger


class DailyItem(QWidget):
    
    delete_me = pyqtSignal(QListWidgetItem)  # 删除自己信号
    refresh_list = pyqtSignal()  # 请求刷新列表

    def __init__(self, trigger: 'Trigger',
                 list_item: 'QListWidgetItem', *args, **kwargs) -> None:
        super(DailyItem, self).__init__(*args, **kwargs)

        self.list_item = list_item  # 与之绑定的list_item
        self.trigger = trigger
        task = self.trigger.task
        self.task = task

        layout = QHBoxLayout()
        layout_left = QVBoxLayout()
        layout_right = QVBoxLayout()
        self.title = QLabel(trigger.task.title, parent=self)
        if task.importance >= 3:
            self.title.setStyleSheet("color: red")
        layout_left.addWidget(self.title)
        l = QLabel(task.description, parent=self)
        layout_left.addWidget(l)

        l = QLabel(self.trigger.get_trigger_description_str(), parent=self)
        layout_right.addWidget(l)

        layout.addLayout(layout_left)
        layout.addLayout(layout_right)


        self.setLayout(layout)
        # 设置右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightClickMenu)


        self.show()

    @staticmethod
    def get_state(start: datetime, end: datetime, now: datetime) -> int:
        if now < start:
            if start - now < timedelta(hours=6):
                return DailyItem.NEAR_START
            else:
                return DailyItem.NOT_START
        elif start <= now and now < end:
            if end - now < timedelta(hours=6):
                return DailyItem.NEAR_DEADLINE
            else:
                return DailyItem.IN_PROGRESS
        else:
            return DailyItem.EXPIRED

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
        te = DailyTaskEdit("编辑周期任务", self.trigger)
        te.task_edited.connect(self.task_edited)
        te.exec()

    def task_edited(self, trig: Trigger):
        self.refresh_list.emit()

    def rmenu_important(self):
        self.task.importance = 3
        self.title.setStyleSheet("color: red")
        Storage.save()

    def rmenu_delete(self):
        cond = QMessageBox.question(
            self, "确认删除", "删除后将不可恢复", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if cond == QMessageBox.StandardButton.Yes:
            self.delete_me.emit(self.list_item)
            Storage.save()



class DailyListPage(QWidget):
    sig_sync = pyqtSignal()
    def __init__(self, user: 'User', *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        layout = QVBoxLayout()
        tool_bar_layout = QHBoxLayout()

        self.new_task_button = QPushButton("新建周期任务", self)
        self.new_task_button.clicked.connect(self.create_new_task)
        tool_bar_layout.addWidget(self.new_task_button)


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
        self.show_view()

    def show_view(self):
        self.todo_list.clear()
        for trigger in self.user.triggers:
            item = self.construct_list_item(trigger)
            self.todo_list.setItemWidget(item.list_item, item)

    def construct_list_item(self, trigger: 'Trigger') -> DailyItem:
        widget = QListWidgetItem(self.todo_list)
        widget.setSizeHint(QSize(60, 100))
        ret = DailyItem(trigger, widget, parent=self.todo_list)
        ret.delete_me.connect(self.delete_item)
        ret.refresh_list.connect(self.refresh_view)
        return ret

    def refresh_view(self) -> None:
        self.show_view()
        self.sig_sync.emit()

    def delete_item(self, item: QListWidgetItem):
        """从视图中删除列表项"""
        # 根据item得到它对应的行数
        row = self.todo_list.indexFromItem(item).row()
        # 删除item
        trig = self.todo_list.itemWidget(item)
        item = self.todo_list.takeItem(row)
        
        # 删除widget
        self.todo_list.removeItemWidget(item)
        self.user.triggers.remove(trig.trigger)
        self.sig_sync.emit()

    def view_changed(self):
        self.show_view()

    def create_new_task(self):
        te = DailyTaskEdit("新建周期任务", TaskBuilder.get_empty_trigger())
        te.task_edited.connect(self.task_added)
        te.exec()

    def task_added(self, trigger: 'Trigger'):
        self.user.triggers.append(trigger)
        # 立即创建一次任务
        if trigger.task.start_time.date() == date.today():
            self.user.add_task(copy.deepcopy(trigger.task))
        self.show_view()
        Storage.save()
        self.sig_sync.emit()

    def change_user(self, user: 'User'):
        self.user = user
        self.show_view()

    def sync_task(self):
        self.show_view()