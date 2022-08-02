#QListView使用
from re import S
from PyQt5.QtWidgets import   QMessageBox,QListView, QStatusBar,  QMenuBar,QMenu,QAction,QLineEdit,QStyle,QFormLayout,   QVBoxLayout,QWidget,QApplication ,QHBoxLayout, QPushButton,QMainWindow,QGridLayout,QLabel
from PyQt5.QtGui import QIcon,QPixmap,QStandardItem,QStandardItemModel
from PyQt5.QtCore import QStringListModel,QAbstractListModel,QModelIndex,QSize
from qt_material import apply_stylesheet
import sys

class WindowClass(QMainWindow):
    def __init__(self,parent=None):
        super(WindowClass, self).__init__(parent)
        self.layout=QVBoxLayout()
        self.resize(200,300)
        listModel=QStringListModel()
        listView=QListView()
        items=["张三","李四","小明","JONES"]

        listModel.setStringList(items)
        listView.setModel(listModel)

        listView.clicked.connect(self.checkItem)

        self.layout.addWidget(listView)
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        
    def  checkItem(self,index):
         QMessageBox.information(self,"ListView","选择项是：%d"%(index.row()))

if __name__=="__main__":
    app=QApplication(sys.argv)
    apply_stylesheet(app, theme='light_blue.xml')
    win=WindowClass()
    win.show()
    sys.exit(app.exec_())