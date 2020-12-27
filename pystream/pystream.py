import sys
import time
import json
import logging
import base64
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QStackedWidget, QWidget, QPushButton, QProgressBar
from PyQt5.QtGui import QIcon, QPixmap, QFont, QMouseEvent
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt

from pystream.webservice import WebSocketServer, Metric
from pystream.analoggaugewidget import AnalogGaugeWidget 
from pystream.gradiant_progressbar import GradiantProgressBar
from pystream.event_message import EventMessage, Command, Action

def main():
    app = QApplication(sys.argv)
    global window 
    window = PyStream()
    sys.exit(app.exec_())

class PyStream(QMainWindow):
    receive_signal = pyqtSignal(Metric)

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
        self.setWindowIcon(QIcon("pystream/resource/pyalarm.png"))

        self.is_updating = False

        self.stack = QStackedWidget(self)
        self.stack.setGeometry(0, 0, 800, 480)
        self.panel_1 = QWidget()
        self.panel_2 = QWidget()
        self.panel_3 = QWidget()
        self.stack.addWidget(self.panel_1)
        self.stack.addWidget(self.panel_2)
        self.stack.addWidget(self.panel_3)

        #####################
        ##### Panel 1
        #self.panel_1.setStyleSheet("background-color: #000000")
        background_1 = QLabel(self.panel_1)
        background_1.setGeometry(0, 0, 800, 480)
        background_1.setStyleSheet("background-image: url(pystream/resource/page_1.jpg);")

        self.__create_button(self.panel_1, 774, 227, 26, 26, "arrow_right.png", lambda:self.__change_page("Forward"))

        self.gauge_cpu_1 = self.__create_gauge(self.panel_1, 95, 67)
        self.gauge_cpu_2 = self.__create_gauge(self.panel_1, 335, 67)
        self.gauge_cpu_3 = self.__create_gauge(self.panel_1, 580, 67)
        self.gauge_cpu_4 = self.__create_gauge(self.panel_1, 95, 230)
        self.gauge_cpu_5 = self.__create_gauge(self.panel_1, 335, 230)
        self.gauge_cpu_6 = self.__create_gauge(self.panel_1, 560, 230)

        self.label_cpu_1 = self.__create_label(self.panel_1, 135, 164, text="--°C")
        self.label_cpu_2 = self.__create_label(self.panel_1, 380, 164, text="--°C")
        self.label_cpu_3 = self.__create_label(self.panel_1, 620, 164, text="--°C")
        self.label_cpu_4 = self.__create_label(self.panel_1, 135, 333, text="--°C")
        self.label_cpu_5 = self.__create_label(self.panel_1, 380, 333, text="--°C")
        self.label_cpu_6 = self.__create_label(self.panel_1, 620, 333, text="--°C")

        self.__create_label(self.panel_1, 32, 384, text="GPU", font_size=20, color="#FFFFFF")
        self.label_gpu_temp = self.__create_label(self.panel_1, 29, 417, text="--°C", font_size=15, color="#FFFFFF")
        self.progress_gpu_load = self.__create_progressbar(self.panel_1, 95, 390, 174, 20)
        self.progress_gpu_mem_load = self.__create_progressbar(self.panel_1, 95, 420, 174, 20)

        self.__create_label(self.panel_1, 275, 384, text="Network", font_size=20, color="#FFFFFF")
        self.__create_label(self.panel_1, 365, 390, text="Down", font_size=15, color="#FFFFFF")
        self.__create_label(self.panel_1, 365, 414, text="Up", font_size=15, color="#FFFFFF")
        self.label_net_down = self.__create_label(self.panel_1, 430, 390, text="0", font_size=15, color="#FFFFFF")
        self.label_net_up = self.__create_label(self.panel_1, 430, 414, text="0", font_size=15, color="#FFFFFF")

        self.__create_label(self.panel_1, 546, 379, text="Memory", font_size=20, color="#FFFFFF")
        self.progress_mem_load = self.__create_progressbar(self.panel_1, 551, 407, 203, 34)

        #####################
        ##### Panel 2
        background_2 = QLabel(self.panel_2)
        background_2.setGeometry(0, 0, 800, 480)
        background_2.setStyleSheet("background-image: url(pystream/resource/page_2.jpg);")

        self.__create_button(self.panel_2, 0, 227, 26, 26, "arrow_left.png", lambda:self.__change_page("Backward"))

        self.label_media_image = self.__create_label(self.panel_2, 325, 10)
        self.label_media_image.resize(150, 150)
        self.label_media_image.setPixmap(QPixmap("pystream/resource/media.png"))
        self.label_media_status = self.__create_label(self.panel_2, 60, 50, text="-", color="#FFFFFF")
        self.label_media_status.setAlignment(Qt.AlignCenter)
        self.label_media_status.resize(150, 25)
        self.label_media_title = self.__create_label(self.panel_2, 0, 180, text="-", color="#FFFFFF")
        self.label_media_title.setAlignment(Qt.AlignCenter)
        self.label_media_title.resize(800, 25)
        self.label_media_artist = self.__create_label(self.panel_2, 0, 210, text="-", color="#FFFFFF")
        self.label_media_artist.setAlignment(Qt.AlignCenter)
        self.label_media_artist.resize(800, 25)
        
        self.__create_button(self.panel_2, 362, 280, 75, 75, "play_pause.png", lambda:self.__send_key(Command.PlayPause))
        self.__create_button(self.panel_2, 362, 365, 75, 75, "stop.png", lambda:self.__send_key(Command.Stop))
        self.__create_button(self.panel_2, 277, 318, 75, 75, "previous.png", lambda:self.__send_key(Command.Previous))
        self.__create_button(self.panel_2, 448, 318, 75, 75, "next.png", lambda:self.__send_key(Command.Next))
        self.__create_button(self.panel_2, 40, 280, 75, 75, "volume_up.png", lambda:self.__send_key(Command.VolumeUp))
        self.__create_button(self.panel_2, 40, 365, 75, 75, "volume_down.png", lambda:self.__send_key(Command.VolumeDown))

        #####################
        ##### Panel 3
        self.panel_3.setStyleSheet("background-image: url(pystream/resource/pyalarm.png);")

        self.label_room_temp = self.__create_label(self, 110, 0, text="--°C", color="#FFFFFF")
        self.label_time = self.__create_label(self, 590, 0, text="00:00", font_size=15, color="#FFFFFF")

        self.restore_gui()
        #self.setCursor(QtCore.Qt.BlankCursor)
        logging.info("[GUI] Init done")
        self.receive_signal.connect(self.receive_gui)
        self.show()

    def __create_gauge(self, parent, x ,y):
        gauge = AnalogGaugeWidget(parent)
        gauge.set_enable_fine_scaled_marker(False)
        gauge.set_enable_big_scaled_grid(False)
        gauge.set_enable_ScaleText(False)
        gauge.set_enable_CenterPoint(False)
        gauge.set_enable_Needle_Polygon(False)
        gauge.set_enable_barGraph(False)
        gauge.set_start_scale_angle(165)
        gauge.set_total_scale_angle_size(210)
        gauge.set_gauge_color_inner_radius_factor(600)
        gauge.set_MaxValue(100)
        gauge.setGeometry(x, y, 130, 130)
        gauge.update_value(50)
        gauge.set_DisplayValueColor(0, 255, 255)
        return gauge

    def __create_label(self, parent, x, y, text="", font_size=15, color="#00FFFF"):
        label = QLabel(parent)
        label.setText(text) #"--°C"
        font = QFont("Decorative", font_size)
        font.setBold(True)
        label.setFont(font)
        label.setStyleSheet("color: %s;" % color);
        label.move(x, y)
        return label

    def __create_progressbar(self, parent, x, y, width, height):
        progress = GradiantProgressBar(parent)
        progress.setFormat("")
        progress.setValue(50)
        progress.setMaximum(100)
        progress.setGeometry(x, y, width, height)
        return progress

    def __create_button(self, parent, x, y, width, height, image, click):
        button = QPushButton(parent)
        button.setStyleSheet("background-image: url(pystream/resource/" + image + ");")
        button.clicked.connect(click)
        button.setGeometry(x, y, width, height)
        button.setFlat(True)
        return button

    def __change_page(self, direction):
        if direction == "Forward":
            if self.stack.currentIndex() < self.stack.count() - 2: 
                self.stack.setCurrentIndex(self.stack.currentIndex() + 1)
        elif direction == "Backward":
            if self.stack.currentIndex() > 0: 
                self.stack.setCurrentIndex(self.stack.currentIndex() - 1)

    def __send_key(self, key):
        msgObj = EventMessage(Action.Click, key)
        msg = json.dumps(msgObj.__dict__)
        self.__server.broadcast(msg)

    def udpate_gui(self, data:Metric):
        self.gauge_cpu_1.update_value(data.cpus[0].load)
        self.label_cpu_1.setText("%1.0f°C" % data.cpus[0].temperature)
        self.gauge_cpu_2.update_value(data.cpus[1].load)
        self.label_cpu_2.setText("%1.0f°C" % data.cpus[1].temperature)
        self.gauge_cpu_3.update_value(data.cpus[2].load)
        self.label_cpu_3.setText("%1.0f°C" % data.cpus[2].temperature)
        self.gauge_cpu_4.update_value(data.cpus[3].load)
        self.label_cpu_4.setText("%1.0f°C" % data.cpus[3].temperature)
        self.gauge_cpu_5.update_value(data.cpus[4].load)
        self.label_cpu_5.setText("%1.0f°C" % data.cpus[4].temperature)
        self.gauge_cpu_6.update_value(data.cpus[5].load) 
        self.label_cpu_6.setText("%1.0f°C" % data.cpus[5].temperature) 
        
        self.progress_mem_load.setValue(data.memory_load)
        
        self.label_gpu_temp.setText("%1.0f°C" % data.gpu.temperature)
        self.progress_gpu_load.setValue(data.gpu.load)
        self.progress_gpu_mem_load.setValue(data.gpu.memory_load)  
        
        self.label_net_down.setText(data.network.down)
        self.label_net_up.setText(data.network.up)
        
        self.label_room_temp.setText("%1.0f°C" % data.room_temperature)
        self.label_time.setText(data.time)

        if data.playback_info is not None:
            if data.playback_info.title is not None:
                self.label_media_title.setText(data.playback_info.title)
            if data.playback_info.artist is not None:
                self.label_media_artist.setText(data.playback_info.artist)
            if data.playback_info.image is not None:
                self.label_media_image.pixmap().loadFromData(base64.b64decode(data.playback_info.image))
            else:
                self.label_media_image.pixmap().loadFromData("pystream/resource/media.png")
            if data.playback_info.status is not None:
                if data.playback_info.status == 0:
                   self.label_media_status.setText("Closed")
                if data.playback_info.status == 1:
                   self.label_media_status.setText("Opened")
                if data.playback_info.status == 2:
                   self.label_media_status.setText("Changing")
                if data.playback_info.status == 3:
                   self.label_media_status.setText("Stopped")
                if data.playback_info.status == 4:
                   self.label_media_status.setText("Playing")
                if data.playback_info.status == 5:
                   self.label_media_status.setText("Paused")

    def receive_gui(self, data:Metric):
        if data.reset is not None and data.reset:
            logging.info("[GUI] Restoring initial image")
            self.restore_gui()
        else:
            if self.is_updating == False:
                self.is_updating = True
                try:
                    self.udpate_gui(data)
                    self.enable_gui()
                except Exception as e:
                    print(e)
                finally:
                    self.is_updating = False
            else: 
                print("Gui is locked")

    def receive(self, data:Metric):
        if data is None:
            data = Metric(reset = True)
        self.receive_signal.emit(data)

    def enable_gui(self):
        if self.stack.currentIndex() == 2:
                self.stack.setCurrentIndex(0)

    def restore_gui(self):
        self.stack.setCurrentIndex(2)