import sys
import time
import json
import logging
import base64
import re
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QStackedWidget, QWidget, QPushButton, QProgressBar
from PyQt5.QtGui import QIcon, QPixmap, QFont, QMouseEvent
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt, QTimer, QDateTime
from pystream.pyrelay import PyRelay

from rpi_backlight import Backlight
from rpi_backlight.utils import FakeBacklightSysfs

from Xlib import X
from Xlib import display
import pyautogui

from pystream.webservice import WebSocketServer, Metric
from pystream.analoggaugewidget import AnalogGaugeWidget 
from pystream.rollinglabel import RollingLabel
from pystream.gradiant_progressbar import GradiantProgressBar
from pystream.event_message import EventMessage, Command, Action
from pystream.pytemp import PyTemp
from pystream.pysense import PySense

def main(rootPath):
    app = QApplication(sys.argv)
    global window 
    window = PyStream(rootPath)
    sys.exit(app.exec_())

class PyStream(QMainWindow):
    receive_signal = pyqtSignal(Metric)

    def __init__(self, rootPath):
        super().__init__()
        self.rootPath = rootPath
        self.__server = WebSocketServer(self)
        self.__server.start()
        self.__relay = PyRelay()
        self.__temp = PyTemp()
        self.__temp
        self.__temp.start()
        self.__stats_tab_index = 0
        self.__buttons_tab_index = 1
        self.__pysense = PySense()
        self.enable_gui_switch = True
        self.timer = QTimer()
        self.timer.timeout.connect(self.__timer_tick)
    
        try:
            self.backlight = Backlight()
        except:
            self.fakeBacklightSysfs = FakeBacklightSysfs()
            self.fakeBacklightSysfs.__enter__()
            self.backlight = Backlight(backlight_sysfs_path=self.fakeBacklightSysfs.path)
        
        self.initUI()
        self.enable_screensaver()

    def initUI(self):
        logging.info("[GUI] Init main frame")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setGeometry(0, 0, 800, 480)
        self.setWindowTitle("MediaDisplay-Server")
        self.setWindowIcon(QIcon("pystream/resource/pyalarm.png"))

        self.is_updating = False

        self.stack = QStackedWidget(self)
        self.stack.setGeometry(0, 0, 800, 480)
        self.panel_1 = QWidget()
        #self.panel_2 = QWidget()
        self.panel_3 = QWidget()
        self.stack.addWidget(self.panel_1)
        #self.stack.addWidget(self.panel_2)
        self.stack.addWidget(self.panel_3)

        #####################
        ##### Panel 1
        background_1 = QLabel(self.panel_1)
        background_1.setGeometry(0, 0, 800, 480)
        background_1.setStyleSheet("background-image: url(pystream/resource/page_1.jpg);")

        self.gauge_cpu_1 = self.__create_gauge(self.panel_1, 95, 67)
        self.gauge_cpu_2 = self.__create_gauge(self.panel_1, 335, 67)
        self.gauge_cpu_3 = self.__create_gauge(self.panel_1, 580, 67)
        self.gauge_cpu_4 = self.__create_gauge(self.panel_1, 95, 230)
        self.gauge_cpu_5 = self.__create_gauge(self.panel_1, 335, 230)
        self.gauge_cpu_6 = self.__create_gauge(self.panel_1, 580, 230)

        self.label_cpu_1 = self.__create_label(self.panel_1, 135, 164, text="-- °C")
        self.label_cpu_2 = self.__create_label(self.panel_1, 380, 164, text="-- °C")
        self.label_cpu_3 = self.__create_label(self.panel_1, 620, 164, text="-- °C")
        self.label_cpu_4 = self.__create_label(self.panel_1, 135, 333, text="-- °C")
        self.label_cpu_5 = self.__create_label(self.panel_1, 380, 333, text="-- °C")
        self.label_cpu_6 = self.__create_label(self.panel_1, 620, 333, text="-- °C")

        self.__create_label(self.panel_1, 35, 384, text="GPU", font_size=20, color="#FFFFFF")
        self.label_gpu_temp = self.__create_label(self.panel_1, 37, 419, text="--°C", font_size=15, color="#FFFFFF")
        self.progress_gpu_load = self.__create_progressbar(self.panel_1, 95, 390, 174, 20)
        self.progress_gpu_mem_load = self.__create_progressbar(self.panel_1, 95, 420, 174, 20)

        self.__create_label(self.panel_1, 330, 395, text="Down", font_size=15, color="#FFFFFF")
        self.__create_label(self.panel_1, 330, 419, text="Up", font_size=15, color="#FFFFFF")
        self.label_net_down = self.__create_label(self.panel_1, 430, 395, width=100, height=25, text="0", font_size=15, color="#FFFFFF")
        self.label_net_down.setAlignment(Qt.AlignRight)
        self.label_net_up = self.__create_label(self.panel_1, 430, 419, width=100, height=25, text="0", font_size=15, color="#FFFFFF")
        self.label_net_up.setAlignment(Qt.AlignRight)

        self.__create_label(self.panel_1, 546, 379, text="Memory", font_size=18, color="#FFFFFF")
        self.progress_mem_load = self.__create_progressbar(self.panel_1, 551, 407, 203, 34)
        
        self.__create_button(self.panel_1, 774, 227, 26, 26, "arrow_right.png", lambda:self.__change_page("Forward"))

        #####################
        ##### Panel 3
        background_3 = QLabel(self.panel_3)
        background_3.setGeometry(0, 0, 800, 480)
        background_3.setStyleSheet("background-image: url(pystream/resource/page_2.jpg);")

        self.__create_button(self.panel_3, 125, 180, 100, 120, "desk_lamp.png", lambda:self.__relay.toggle_relay(PyRelay.BIG_2), checkable=True)
        self.__create_button(self.panel_3, 350, 180, 100, 120, "keyboard.png", press=lambda:self.__relay.activate_relay(PyRelay.SMALL_1), release=lambda:self.__relay.deactivate_relay(PyRelay.SMALL_1))
        self.label_active_usb = self.__create_label(self.panel_3, 350, 280, width=100, height=25, text="1", color="#FFFFFF")
        self.label_active_usb.setAlignment(Qt.AlignCenter)
        self.__create_button(self.panel_3, 575, 180, 100, 120, "laptop.png", lambda:self.__relay.toggle_relay(PyRelay.BIG_1), checkable=True)
        
        self.__create_button(self.panel_3, 0, 227, 26, 26, "arrow_left.png", lambda:self.__change_page("Backward"))

        
        self.label_room_temp = self.__create_label(self, 110, 0, text="--°C", color="#FFFFFF")
        self.label_time = self.__create_label(self, 590, 0, text="00:00", font_size=15, color="#FFFFFF")

        self.restore_gui()
        self.setCursor(QtCore.Qt.BlankCursor)
        logging.info("[GUI] Init done")
        self.timer.start(1000)
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

    def __create_label(self, parent, x, y, width=None, height=None, text="", font_size=15, color="#00FFFF"):
        label = QLabel(parent)
        label.setText(text)
        font = QFont("Decorative", font_size)
        font.setBold(True)
        label.setFont(font)
        label.setStyleSheet("color: %s;" % color);
        if width is None or height is None:
            label.move(x, y)
        else:
            label.setGeometry(x, y, width, height)
        return label

    def __create_progressbar(self, parent, x, y, width, height):
        progress = GradiantProgressBar(parent)
        progress.setFormat("")
        progress.setValue(50)
        progress.setMaximum(100)
        progress.setGeometry(x, y, width, height)
        return progress

    def __create_button(self, parent, x, y, width, height, image, click=None, press=None, release=None, checkable=False):
        button = QPushButton(parent)
        button.setCheckable(checkable)
        if checkable:
            pressed_image = image.replace(".", "_pressed.")
            stre = "QPushButton {border-image: url(pystream/resource/" + image + ");} " \
                 + "QPushButton:checked {border-image: url(pystream/resource/" + pressed_image + ");}"
            button.setStyleSheet(stre)
        else:
            button.setStyleSheet("border-image: url(pystream/resource/" + image + ");")
        
        if click is not None:
            button.clicked.connect(click)
        if press is not None:
            button.pressed.connect(press)
        if release is not None:
            button.released.connect(release)

        button.setGeometry(x, y, width, height)
        button.setFlat(True)
        return button

    def __timer_tick(self):
        time = QDateTime.currentDateTime()
        timeDisplay = time.toString('hh:mm')
        temp = self.__temp.temperature
        active_usb = "2" if self.__pysense.check_state(PySense.INPUT_1) else "1"

        self.label_time.setText(timeDisplay)
        self.label_room_temp.setText("%1.0f°C" % temp)
        self.label_active_usb.setText(active_usb)

    def __change_page(self, direction):
        self.enable_gui_switch = False
        if direction == "Forward":
            if self.stack.currentIndex() < self.stack.count() - 1: 
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

    def receive_gui(self, data:Metric):
        if data.reset is not None and data.reset:
            logging.info("[GUI] Restoring initial image")
            self.restore_gui()
            self.enable_screensaver()
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
            self.disable_screensaver()

    def receive(self, data:Metric):
        if data is None:
            data = Metric(reset = True)
        self.receive_signal.emit(data)

        if data.send_display_brightness == True:
            msgObj = EventMessage(Action.Brightness, self.backlight.brightness)
            msg = json.dumps(msgObj.__dict__)
            self.__server.broadcast(msg)
        if data.display_brightness is not None and data.display_brightness >= 0 and data.display_brightness <= 100:
            self.backlight.brightness = data.display_brightness

    def enable_gui(self):
        if self.enable_gui_switch == True and self.stack.currentIndex() == self.__buttons_tab_index:
                self.stack.setCurrentIndex(self.__stats_tab_index)

    def restore_gui(self):
        self.enable_gui_switch = True

        self.stack.setCurrentIndex(2)
        self.label_cpu_1.setText("-- °C")
        self.label_cpu_2.setText("-- °C")
        self.label_cpu_3.setText("-- °C")
        self.label_cpu_4.setText("-- °C")
        self.label_cpu_5.setText("-- °C")
        self.label_cpu_6.setText("-- °C")

        self.gauge_cpu_1.update_value(50)
        self.gauge_cpu_2.update_value(50)
        self.gauge_cpu_3.update_value(50)
        self.gauge_cpu_4.update_value(50)
        self.gauge_cpu_5.update_value(50)
        self.gauge_cpu_6.update_value(50)

        self.progress_mem_load.setValue(50)

        self.label_gpu_temp.setText("%1.0f°C" % 0)
        self.progress_gpu_load.setValue(50)
        self.progress_gpu_mem_load.setValue(50)  
        
        self.label_net_down.setText("0")
        self.label_net_up.setText("0")

        self.stack.setCurrentIndex(self.__buttons_tab_index)

    def update_app(self):
        GitUpdater.update(self.rootPath)
    
    def disable_screensaver(self):
        # disp = display.Display()
        # disp.set_screen_saver(0, 0, X.DontPreferBlanking, X.AllowExposures)
        # disp.sync()
        pyautogui.moveRel(0, 10)

    def enable_screensaver(self):
        disp = display.Display()
        screensaver = disp.get_screen_saver()
        if screensaver.timeout != 60:
            disp.set_screen_saver(60, 60, X.DefaultBlanking, X.AllowExposures)
            disp.sync()
