from datetime import datetime, timedelta
from src.core.util import QDateTime2Pydatetime
from src.core.task import Task, TaskBuilder
import typing
from PyQt5.QtCore import Qt, QSize, QMimeData, pyqtSignal, QDateTime
from PyQt5.QtGui import QIcon, QDrag, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QStackedWidget, QHBoxLayout, \
    QListWidgetItem, QLabel, QVBoxLayout, QMainWindow, QComboBox, QPushButton, QMenu, QAction, \
    QMessageBox, QFormLayout, QLineEdit, QDateTimeEdit, QDialog


class TaskEdit(QDialog):
    """任务编辑组件"""
    task_edited = pyqtSignal(Task)
    def __init__(self,wtitle: str, task: 'Task',
                 *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.task = task
        self.setWindowTitle(wtitle)

        vlayout = QVBoxLayout()
        layout = QFormLayout()
        hlayout = QHBoxLayout()
        vlayout.addLayout(layout)
        vlayout.addLayout(hlayout)
        self.setLayout(vlayout)

        self.title = QLineEdit(self)
        if task.title:
            self.title.setText(task.title)
        self.title.textChanged[str].connect(self.title_edit)
        layout.addRow(QLabel("主题", self), self.title)

        self.description = QLineEdit(self)
        if task.description:
            self.description.setText(task.description)
        self.description.textChanged[str].connect(self.description_edit)
        layout.addRow(QLabel("描述", self), self.description)

        self.start_time = QDateTimeEdit(self)
        if task.start_time:
            self.start_time.setDateTime(task.start_time)
        else:
            self.start_time.setDateTime(QDateTime.currentDateTime())
            task.start_time = datetime.now()
        self.start_time.dateTimeChanged.connect(self.start_time_edit)
        layout.addRow(QLabel("开始时间", self), self.start_time)

        self.deadline = QDateTimeEdit(self)
        if task.deadline:
            self.deadline.setDateTime(task.deadline)
        else:
            self.deadline.setDateTime(QDateTime.currentDateTime())
            task.deadline = datetime.now()
        self.deadline.dateTimeChanged.connect(self.deadline_edit)
        layout.addRow(QLabel("截止时间", self), self.deadline)

        self.timecost = QLineEdit(self)
        if task.timecost:
            self.timecost.setText(str(task.timecost))
        self.timecost.textChanged[str].connect(self.timecost_edit)
        layout.addRow(QLabel("预计花费时间(小时)", self), self.timecost)

        self.importance = QComboBox(self)
        if task.importance:
            self.importance.setCurrentIndex(task.importance)
        self.importance.addItems(["无", "不重要", "一般重要", "非常重要"])
        self.importance.activated[str].connect(self.importance_edit)
        layout.addRow(QLabel("重要性", self),self.importance)

        
        self.tags = QLineEdit(self)
        if task.category:
            self.tags.setText(','.join(task.category))
        self.tags.textChanged[str].connect(self.tags_edit)
        layout.addRow(QLabel("标签(逗号分隔)", self), self.tags)

        self.btn0 = QPushButton("确认", self)
        self.btn0.clicked.connect(self.confirm)
        hlayout.addWidget(self.btn0)
        self.btn1 = QPushButton("取消", self)
        self.btn1.clicked.connect(self.cancel)
        hlayout.addWidget(self.btn1)

    def confirm(self):
        print(self.task.__dict__)
        if self.checkForm():
            self.task_edited.emit(self.task)
            self.accept()
    def cancel(self):
        self.reject()

    def checkForm(self) -> bool:
        """检查表单合法性"""
        if not self.task.title:
            popup = QMessageBox.warning(self,"无效任务","任务标题不能为空")
            return False
        if not self.task.description:
            self.task.description = ""
        if not self.task.timecost:
            self.task.timecost = 0
        if not self.task.importance:
            self.task.importance = 0
        if not self.task.category:
            self.task.category = []
        return True
    def title_edit(self, text: str):
        self.task.title = text

    def description_edit(self, text: str):
        self.task.description = text

    def start_time_edit(self, time: QDateTime):
        print('edit')
        self.task.start_time = QDateTime2Pydatetime(time)

    def deadline_edit(self, time: QDateTime):
        print('edit')
        self.task.deadline = QDateTime2Pydatetime(time)

    def timecost_edit(self, text: str):
        try:
            t = int(text)
            self.task.timecost = t
        except:
            pass

    def importance_edit(self, text: str):
        t = None
        if text == "无":
            t = 0
        if text == "不重要":
            t = 1
        if text == "一般重要":
            t = 2
        if text == "非常重要":
            t = 3
        self.task.importance = t

    def tags_edit(self, text: str):
        if len(text) > 0:
            tags = text.strip().split(',')
            self.task.category = tags