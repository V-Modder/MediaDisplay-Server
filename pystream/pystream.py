import sys
import time
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QFont, QMouseEvent
from PyQt5 import QtGui
from PyQt5 import QtCore

#from pystream.input_buffer import InputBuffer
from pystream.webservice import send_message

def main():
    app = QApplication(sys.argv)
    global window 
    window = PyStream()
    sys.exit(app.exec_())

class PyStream(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        print("Init main frame")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setGeometry(0, 0, 800, 480)
        self.setWindowTitle("PyAlarm")
        self.setWindowIcon(QIcon("pystream/pyalarm.png"))
        self.mousePressEvent = self.__windowClicked

        self.background = QLabel(self)
        self.background.setGeometry(0, 0, 800, 480)
        self.restore_gui()

        print("Init done")
        self.show()

    def __windowClicked(self, event: QMouseEvent):
        x = event.x()
        y = event.y()
        msg = {"action": "click", "x": x, "y": y}
        send_message(msg)
        #self.__input_buffer.set_action("click", x, y)

    def update_gui(self, image):
        self.background.pixmap().loadFromData(image)
        self.background.update()
        #return self.__input_buffer.pop_action()

    def restore_gui(self):
        self.background.setPixmap(QPixmap("pystream/pyalarm.png"))