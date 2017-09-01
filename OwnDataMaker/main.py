import os
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage
import sys
import numpy
import cv2

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def _convert_array_to_qimage(a):
    cv2.cvtColor(a, cv2.COLOR_BGR2RGB, a)
    height, width, channels = a.shape
    bytes_per_line = channels * width
    return QImage(a.data, width, height, bytes_per_line, QImage.Format_RGB888)


class CameraDevice(QObject):
    frame_ready = pyqtSignal(QImage)

    def __init__(self, device_id=0):
        super(CameraDevice,self).__init__()
        self.train = None
        self.recog = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_frame)
        self.timer.setInterval(1000/30)
        self.timer.start()
        self.fn_dir = 'instruments'
        self.target = 0
        self.get_target_images()
        self.t_max = 0
        self.t_min = 0
        self.s_max = 0
        self.s_min = 0

    def set_values(self , t_max , t_min , s_max , s_min):
        self.t_max = t_max
        self.t_min = t_min
        self.s_max = s_max
        self.s_min = s_min

    @property
    def size(self):
        height, width = self.images[self.target].shape[:2]
        # width = self.images[self.target].cols
        # height = self.images[self.target].rows
        return (width, height)

    def read_frame(self):
        frame, gray, rects = self.find_instuments_in_target(self.images[self.target].copy())
        gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        for rect in rects:
            cv2.rectangle(frame, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (0, 255, 0), 3)
            cv2.rectangle(gray, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (0, 255, 0), 3)

        vis = numpy.concatenate((frame, gray), axis=1)
        vis = _convert_array_to_qimage(vis)
        self.frame_ready.emit(vis)

    def get_target_images(self):
        self.max_target = 0
        (images, lables) = ([], [])
        self.names = {}
        self.id = 0
        for (subdirs, dirs, files) in os.walk(self.fn_dir):
            for subdir in dirs:
                self.names[self.id] = subdir
                subjectpath = os.path.join(self.fn_dir, subdir)
                for filename in os.listdir(subjectpath):
                    f_name, f_extension = os.path.splitext(filename)
                    if (f_extension.lower() not in
                            ['.png', '.jpg', '.jpeg', '.gif', '.pgm']):
                        print("Skipping " + filename + ", wrong file type")
                        continue
                    path = subjectpath + '/' + filename
                    lable = self.id
                    image = cv2.imread(path)
                    height, width = image.shape[:2]
                    if height > 480 or width > 640 :
                        if height < width:
                            image = cv2.resize(image, (int(640/2), int(480/2)))
                        else:
                            image = cv2.resize(image, (int(480/2), int(640/2)))
                    images.append(image)
                    lables.append(int(lable))
                self.id += 1
        self.max_target = self.id
        (self.images, self.lables) = [numpy.array(lis) for lis in [images, lables]]

    def find_instuments_in_target(self , image):
        frame = image
        gray = cv2.cvtColor(frame , cv2.COLOR_BGR2GRAY)
        ret, gray = cv2.threshold(gray, self.t_min, self.t_max, cv2.THRESH_BINARY_INV)
        im2, ctrs, hier = cv2.findContours(gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        origin_rects = [cv2.boundingRect(ctr) for ctr in ctrs]
        rects = []
        for rect in origin_rects:
            if rect[2] < self.s_min or rect[2] > self.s_max or rect[3] < self.s_min or rect[3] > self.s_max:
                continue
            rects.append(rect)
        return frame , gray , rects

    def make_train_data_set(self):
        image_origin = self.images[self.target].copy()
        index = self.make_train_imge_from_frame(image_origin.copy(),0)
        arr = [0, 1, -1]
        for i in arr:
            image = cv2.flip(image_origin.copy(), i)
            index = self.make_train_imge_from_frame(image , index)

    def make_train_imge_from_frame(self , frame , start_index):
        frame, gray, rects = self.find_instuments_in_target(frame.copy())
        for rect in rects:
            x, y, w, h = rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3]
            crop_img = gray[y: h, x: w]
            filename = "%s.png" % (str(start_index))
            filename = THIS_DIR + "/" + self.names[self.target] + "/" + filename
            start_index += 1
            crop_img = cv2.resize(crop_img, (28 * 3, 28 * 3))
            cv2.imwrite(filename, crop_img)
        return start_index

    def next_target(self):
        self.target +=1
        if self.target >= self.max_target:
            self.target = self.max_target - 1
            return False
        return True


    def __del__(self):
        self.timer.stop()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.ui = loadUi(os.path.join(THIS_DIR, 'mainwindow.ui'), self)
        self.thread = QThread()
        try:
            self.camera = CameraDevice()
        except ValueError:
            self.ui.video.setText("Device not found!\n\nIs FFMPEG available?")
        else:
            self.camera.frame_ready.connect(self.update_video_label)
            self.ui.video.setMinimumSize(*self.camera.size)
            self.camera.moveToThread(self.thread)

    @pyqtSlot()
    def start_recog(self):
        if not self.camera.next_target():
            self.ui.nameText.setText("all Done!!")
            return;


    @pyqtSlot()
    def train_start(self):
        print("load")
        self.camera.make_train_data_set()


    @pyqtSlot(QImage)
    def update_video_label(self, image):
        pixmap = QPixmap.fromImage(image)
        self.ui.video.setPixmap(pixmap)
        self.ui.video.update()

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

    def update_values(self):
        self.camera.set_values(self.ui.t_max.value(), self.ui.t_min.value(), self.ui.s_max.value(),
                               self.ui.s_min.value())


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


main()
