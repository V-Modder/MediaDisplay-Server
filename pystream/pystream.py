import sys
import time
import json
import logging
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QFont, QMouseEvent
from PyQt5 import QtGui
from PyQt5 import QtCore

from pystream.webservice import WebSocketServer

def main():
    app = QApplication(sys.argv)
    global window 
    window = PyStream()
    sys.exit(app.exec_())

class PyStream(QMainWindow):

    def __init__(self):
        super().__init__()
        self.__server = WebSocketServer(self)
        self.__server.start()
        self.initUI()

    def initUI(self):
        logging.info("[GUI] Init main frame")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setGeometry(0, 0, 800, 480)
        self.setWindowTitle("PyAlarm")
        self.setWindowIcon(QIcon("pystream/pyalarm.png"))
        self.mousePressEvent = self.__windowClicked

        self.background = QLabel(self)
        self.background.setGeometry(0, 0, 800, 480)
        self.restore_gui()
        self.setCursor(QtCore.Qt.BlankCursor)
        logging.info("[GUI] Init done")
        self.show()

    def __windowClicked(self, event: QMouseEvent):
        x = event.x()
        y = event.y()
        msgObj = {"action": "click", "x": x, "y": y}
        msg = json.dumps(msgObj)
        self.__server.broadcast(msg)

    def receive(self, image):
        if image is None:
            logging.info("[GUI] Restoring initial image")
            self.restore_gui()
        else:
            self.background.pixmap().loadFromData(image)
        self.background.update()

    def restore_gui(self):
        self.background.setPixmap(QPixmap("pystream/pyalarm.png"))