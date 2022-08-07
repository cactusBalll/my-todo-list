from src.core.user import User
from typing import Tuple
from src.core.storage import Storage
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
import sys
from qt_material import apply_stylesheet
from src.ui.login_dialog import LoginDialog

from src.ui.main import MainWindow


def init_app() -> Tuple[Storage, str]:
    s, created, ok = Storage.try_load()
    if ok:
        if created:
            s.users.append(User("default"))
            return s, "default"
        else:
            return s, s.users[0].name
    else:
        with open("err.txt", "w+", encoding='utf-8') as f:
            f.write("文件系统错误,创建文件失败")
        print("文件系统错误,创建文件失败")
        exit(1)


QtCore.QCoreApplication.setAttribute(
    QtCore.Qt.AA_EnableHighDpiScaling)  # 高分辨率兼容
app = QApplication(sys.argv)

apply_stylesheet(app, "light_blue.xml")

s, name = init_app()
#main_window = MainWindow(s, name)
login_dialog = LoginDialog(s)

r = app.exec_()
Storage.save()
sys.exit(r)
