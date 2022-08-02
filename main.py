from PyQt5.QtWidgets import QApplication
import sys
from qt_material import apply_stylesheet

from src.ui.main import MainWindow

app = QApplication(sys.argv)
apply_stylesheet(app, "light_blue.xml")

main_window = MainWindow()
sys.exit(app.exec_())