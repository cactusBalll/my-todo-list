from random import randint


from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QStackedWidget, QHBoxLayout, \
    QListWidgetItem, QLabel



class LeftTabWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super(LeftTabWidget, self).__init__(*args, **kwargs)
        self.resize(800, 600)
        layout = QHBoxLayout(self, spacing=0)
        layout.setContentsMargins(0, 0, 0, 0)
        # 左侧列表
        self.listWidget = QListWidget(self)
        self.listWidget.setStyleSheet("""
                QListWidget {
                min-width: 120px;
                max-width: 120px;
            }""")
        layout.addWidget(self.listWidget)
        # 右侧层叠窗口
        self.stackedWidget = QStackedWidget(self)
        layout.addWidget(self.stackedWidget)
        self.initUi()

    def initUi(self):
        # 初始化界面
        # 通过QListWidget的当前item变化来切换QStackedWidget中的序号
        self.listWidget.currentRowChanged.connect(
            self.stackedWidget.setCurrentIndex)
        # 去掉边框
        #self.listWidget.setFrameShape(QListWidget.NoFrame)
        # 隐藏滚动条
        self.listWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 这里就用一般的文本配合图标模式了(也可以直接用Icon模式,setViewMode)
        for i in range(20):
            item = QListWidgetItem(
                QIcon('Data/0%d.ico' % randint(1, 8)), str('选 项 %s' % i), self.listWidget)
            # 设置item的默认宽高(这里只有高度比较有用)
            item.setSizeHint(QSize(16777215, 60))
            # 文字居中
            item.setTextAlignment(Qt.AlignCenter)

        # 再模拟20个右侧的页面(就不和上面一起循环放了)
        for i in range(20):
            label = QLabel('我是页面 %d' % i, self)
            label.setAlignment(Qt.AlignCenter)
            # 设置label的背景颜色(这里随机)
            # 这里加了一个margin边距(方便区分QStackedWidget和QLabel的颜色)
            label.setStyleSheet('background: rgb(%d, %d, %d);margin: 50px;' % (
                randint(0, 255), randint(0, 255), randint(0, 255)))
            self.stackedWidget.addWidget(label)


# 美化样式表
Stylesheet = """
/*去掉item虚线边框*/
QListWidget, QListView, QTreeWidget, QTreeView {
    outline: 0px;
}
/*设置左侧选项的最小最大宽度,文字颜色和背景颜色*/
QListWidget {
    min-width: 120px;
    max-width: 120px;
}
"""
from qt_material import apply_stylesheet

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    #app.setStyleSheet(Stylesheet)
    apply_stylesheet(app, "light_blue.xml")
    #t = app.styleSheet()
    #app.setStyleSheet(t + Stylesheet)
    w = LeftTabWidget()
    w.show()
    sys.exit(app.exec_())