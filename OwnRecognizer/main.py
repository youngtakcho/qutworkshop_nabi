import os
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from Recognizer import Recognizer
import sys

sys.path.insert(1, '/usr/local/lib/python3.5/site-packages/')

from camera import CameraDevice

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.recognizer = Recognizer();
        self.recognizer.learn()
        self.ui = loadUi(os.path.join(THIS_DIR, 'mainwindow.ui'), self)
        self.thread = QThread()
        try:
            self.camera = CameraDevice()
        except ValueError:
            self.ui.video.setText("Device not found!\n\nIs FFMPEG available?")
        else:
            self.camera.frame_ready.connect(self.update_video_label)
            self.ui.video.setMinimumSize(640 * 2, 480)
            self.camera.moveToThread(self.thread)

        self.ui.t_max.setValue(0)
        self.ui.t_min.setValue(255)
        self.ui.s_max.setValue(200)
        self.ui.s_min.setValue(3)
        self.update_values()

    @pyqtSlot()
    def start_recog(self):
        if self.recognizer is not None:
            self.camera.set_recog(self.recognizer)
        else:
            print("plz do load recogi")

    @pyqtSlot()
    def stop_recog(self):
        self.camera.remove_recog()

    @pyqtSlot()
    def make_data(self):
        print("Not supported.")

    @pyqtSlot(int)
    def t_max_changed(self, val):
        if val < self.ui.t_min.value():
            self.ui.t_min.setValue(val)
        self.update_values()

    @pyqtSlot(int)
    def t_min_changed(self, val):
        if val > self.ui.t_max.value():
            self.ui.t_max.setValue(val)
        self.update_values()

    @pyqtSlot(int)
    def s_max_changed(self, val):
        if val < self.ui.s_min.value():
            self.ui.s_min.setValue(val)
        self.update_values()

    @pyqtSlot(int)
    def s_min_changed(self, val):
        if val > self.ui.s_max.value():
            self.ui.s_max.setValue(val)
        self.update_values()

    @pyqtSlot(QImage)
    def update_video_label(self, image):
        pixmap = QPixmap.fromImage(image)
        self.ui.video.setPixmap(pixmap)
        self.ui.video.update()

    def update_values(self):
        self.camera.set_values(self.ui.t_max.value(), self.ui.t_min.value(), self.ui.s_max.value(),
                               self.ui.s_min.value())


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


main()
