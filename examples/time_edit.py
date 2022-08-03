import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDate, QTime, QDateTime
from PyQt5.QtWidgets import (QApplication, QWidget, QTimeEdit, 
                             QPlainTextEdit, QPushButton, QVBoxLayout)
 
class DemoTimeEdit(QWidget):
    def __init__(self, parent=None):
        super(DemoTimeEdit, self).__init__(parent)       
        
        # 设置窗口标题
        self.setWindowTitle('实战PyQt5: QTimeEdit Demo!')      
        # 设置窗口大小
        self.resize(400, 300)
        
        self.initUi()
        
    def initUi(self):
        
        #创建日期时间控件并设置显示格式
        self.dtEdit = QTimeEdit(self)
        self.dtEdit.setDisplayFormat('HH:mm:ss')
       
        #设置日期的最大与最小值，在当前日期上，前后大约偏移10年
        self.dtEdit.setMinimumDate(QDate.currentDate().addDays(-3652))
        self.dtEdit.setMaximumDate(QDate.currentDate().addDays(3652))
        
        self.dtEdit.setTime(QTime.currentTime())
       
        #时间改变时触发
        self.dtEdit.timeChanged.connect(self.onTimeChanged)
        
        #创建按钮，点击按钮，获取当前日期和时间
        self.btnDateTimeInfo = QPushButton('日期时间信息')
        self.btnDateTimeInfo.clicked.connect(self.onButtonDateTimeClicked)
        
        #创建信息显示区域
        self.textShower = QPlainTextEdit(self)
        self.textShower.setReadOnly(True)
        
        vLayout = QVBoxLayout(self)
        vLayout.setSpacing(10)
        vLayout.addWidget(self.dtEdit)
        vLayout.addWidget(self.btnDateTimeInfo)
        vLayout.addWidget(self.textShower)
        
        self.setLayout(vLayout)
    
    def onTimeChanged(self, time):
        self.showInfo(time.toString('hh:mm:ss'))
    
    def onButtonDateTimeClicked(self):
        #日期时间
        dateTime = self.dtEdit.dateTime()
        #最大日期
        maxDate = self.dtEdit.maximumDate()
        #最大日期时间
        maxDateTime = self.dtEdit.maximumDateTime()
        #最大时间
        maxTime = self.dtEdit.maximumTime()
        #最小日期
        minDate = self.dtEdit.minimumDate()
        #最小日期时间 
        minDateTime = self.dtEdit.minimumDateTime()
        #最小时间
        minTime = self.dtEdit.minimumTime()
        
        self.showInfo('日期和时间信息')
        self.showInfo('日期时间为: ' + dateTime.toString('yyyy:MM:dd [ddd] hh:mm:ss'))
        self.showInfo('最小日期为: ' + minDate.toString('yyyy:MM:dd [ddd]'))
        self.showInfo('最大日期为: ' + maxDate.toString('yyyy:MM:dd [ddd]'))
        self.showInfo('最小时间为: ' + minTime.toString('hh:mm:ss'))
        self.showInfo('最大时间为: ' + maxTime.toString('hh:mm:ss'))
        self.showInfo('最小日期时间为: ' + minDateTime.toString('yyyy:MM:dd [ddd] hh:mm:ss'))
        self.showInfo('最大日期时间为: ' + maxDateTime.toString('yyyy:MM:dd [ddd] hh:mm:ss'))
    
    def showInfo(self, strInfo:str):
        #print(strInfo)
        self.textShower.appendPlainText(strInfo)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DemoTimeEdit()
    window.show()
    sys.exit(app.exec()) 