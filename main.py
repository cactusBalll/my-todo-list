from datetime import date, timedelta
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
            # 如果在凌晨12点启动，可能要重启应用以使得每日任务被加入
            today = date.today()
            if today > s.last_login_time:
                dt = today - s.last_login_time
                for i in range(1,dt.days+1):
                    d = s.last_login_time + timedelta(days=i)
                    for u in s.users:
                        for trig in u.triggers:
                            t = trig.generate_task(d)
                            if t:
                                u.add_task(t)
            s.last_login_time = today
            return s, s.users[0].name
    else:
        with open("err.txt", "w+", encoding='utf-8') as f:
            f.write("文件系统错误,创建文件失败")
        print("文件系统错误,创建文件失败")
        exit(1)

from freezegun import freeze_time
freezer = freeze_time("2022-8-9 17:51:00")
#freezer.start()
QtCore.QCoreApplication.setAttribute(
    QtCore.Qt.AA_EnableHighDpiScaling)  # 高分辨率兼容
app = QApplication(sys.argv)

apply_stylesheet(app, "light_blue.xml")

s, name = init_app()
#main_window = MainWindow(s, name)
login_dialog = LoginDialog(s)

r = app.exec_()
Storage.save()
#freezer.stop()
sys.exit(r)
