from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage
import cv2
import numpy as np
import math



class CameraDevice(QObject):
    frame_ready = pyqtSignal(QImage)

    def __init__(self, device_id=0):
        super(CameraDevice,self).__init__()
        self.train = None
        self.recog = None
        self.capture = cv2.VideoCapture(device_id)
        if (self.capture.isOpened() is True):
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.timer = QTimer()
        if not self.capture.isOpened():
            raise ValueError("Device not found")

        self.timer.timeout.connect(self.read_frame)
        self.timer.setInterval(1000 / (self.fps or 30))
        self.timer.start()
        self.t_max = 0
        self.t_min = 0
        self.s_max = 0
        self.s_min = 0

    def __del__(self):
        self.timer.stop()
        self.capture.release()

    @property
    def fps(self):
        return int(self.capture.get(cv2.CAP_PROP_FPS))

    @property
    def size(self):
        width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)

    def read_frame(self):
        success, frame = self.capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        im_gray = cv2.GaussianBlur(gray, (5, 5), 0)
        ret, gray = cv2.threshold(im_gray, self.t_min, self.t_max, cv2.THRESH_BINARY_INV)

        if self.recog is not None:
            frame, gray = self.recog.recogize(frame, gray, self.s_max, self.s_min)
            gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            vis = np.concatenate((frame, gray), axis=1)
            frame = vis
        else:
            gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            vis = np.concatenate((frame, gray), axis=1)
            frame = vis
        if success:

            img = _convert_array_to_qimage(frame)
            self.frame_ready.emit(img)
        else:
            raise ValueError("Failed to read frame")



    def set_train(self, train):
        if self.train is not None:
            print("still train wait...")
            return;
        self.train = train;
        print("train setted..")

    def set_recog(self, recognizer):
        self.recog = recognizer

    def stop_recog(self):
        if self.recog is not None:
            self.recog = None;

    def set_values(self, t_max, t_min, s_max, s_min):
        self.t_max = t_max
        self.t_min = t_min
        self.s_max = s_max
        self.s_min = s_min


def _convert_array_to_qimage(a):
    if (len(a.shape) < 3):
        a = cv2.cvtColor(a, cv2.COLOR_GRAY2RGB, a)
    else:
        a = cv2.cvtColor(a, cv2.COLOR_BGR2RGB, a)
    height, width, channels = a.shape
    bytes_per_line = channels * width
    return QImage(a.data, width, height, bytes_per_line, QImage.Format_RGB888)
