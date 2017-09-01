from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage
import cv2

class CameraDevice(QObject):

    frame_ready = pyqtSignal(QImage)

    def __init__(self, device_id=0):
        super(CameraDevice,self).__init__()
        self.train = None
        self.recog = None
        self.capture = cv2.VideoCapture(device_id)
        if(self.capture.isOpened() is True):
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.timer = QTimer()
        self.faceCascade = cv2.CascadeClassifier("./haarcascade_frontalface_default.xml")
        if not self.capture.isOpened():
            raise ValueError("Device not found")

        self.timer.timeout.connect(self.read_frame)
        self.timer.setInterval(1000 / (self.fps or 30))
        self.timer.start()

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

    def detect(self , img, cascade):
        rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),
                                         flags=cv2.CASCADE_SCALE_IMAGE)
        if len(rects) == 0:
            return []
        rects[:, 2:] += rects[:, :2]
        return rects

    def draw_rects(self , img, rects, color):
        for x1, y1, x2, y2 in rects:
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

    def read_frame(self):
        success, frame = self.capture.read()
        gray = cv2.cvtColor(frame , cv2.COLOR_BGR2GRAY)

        if self.train is not None and self.train.train(frame , self.faceCascade) is False:
            if self.recog is not None:
                self.recog = None
            print("training..." , self.train.count)
        else:
            self.train = None;

        if self.recog is not None:
            frame = self.recog.recogize(frame,gray, self.faceCascade)

        if success:
            img = _convert_array_to_qimage(frame)
            self.frame_ready.emit(img)
        else:
            raise ValueError("Failed to read frame")

    def set_train(self,train):
        if self.train is not None:
            print("still train wait...")
            return;
        self.train = train;
        print("train setted..")

    def set_recog(self , recognizer):
        self.recog = recognizer

    def stop_recog(self):
        if self.recog is not None:
            self.recog = None;

def _convert_array_to_qimage(a):
    cv2.cvtColor(a, cv2.COLOR_BGR2RGB, a)
    height, width, channels = a.shape
    bytes_per_line = channels * width
    return QImage(a.data, width, height, bytes_per_line, QImage.Format_RGB888)