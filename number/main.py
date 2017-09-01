import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton , QTextEdit)
from PyQt5.QtGui import QPainter, QPen, QBrush, QPixmap
from PyQt5.QtCore import Qt, pyqtSlot, QRect
from PyQt5.QtCore import QPoint
from Recognizer import *

class MouseTracker(QWidget):
    distance_from_center = 0
    mousePressed = False;
    p = []
    def __init__(self):
        super(MouseTracker,self).__init__()
        self.recognizer = DigitRecognizer()
        self.recognizer.learn()
        self.initUI()
        self.setMouseTracking(True)


    def initUI(self):
        btn_x = 10
        self.msg = "number : %d"
        self.setGeometry(200, 200, 400,500)
        self.setWindowTitle('Mouse Tracker')
        self.label = QTextEdit(self)
        self.label.move(5, 430)
        self.label.setText("number : ")
        self.label.setUpdatesEnabled(True)
        self.button_recog = QPushButton("recognize", self)
        self.button_recog.move(btn_x, 470)
        self.button_recog.released.connect(self.recognize)
        self.button_clear = QPushButton("clear", self)
        self.button_clear.move(btn_x+200, 470)
        self.button_clear.released.connect(self.clear)
        self.show()


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print("Press!")
            self.mousePressed = True


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            print("Press!")
            self.mousePressed = False
            self.take_screenshot()

    def mouseMoveEvent(self, event):
        if(self.mousePressed == True):
            x = event.x()
            y = event.y()
            self.p.append((x, y))
        self.update()

    def paintEvent(self, e):
        q = QPainter(self)
        q.begin(self)
        pen = QPen(Qt.white, 10)
        b = QBrush(Qt.black)
        w = QBrush(Qt.white)
        q.setBrush(b)
        q.drawRect(QRect(0, 0, 400, 400))
        q.setPen(pen)
        q.setBrush(w)
        self.drawPoints(q)
        q.end();

    def drawPoints(self, qp):
        size = self.size()
        for i in self.p:
            try:
                x = i[0]
                y = i[1]
                qp.drawEllipse(QPoint(x,y),10,10)
            except:
                pass

    def take_screenshot(self):
        screen = QApplication.activeWindow()
        if screen is not None:
            self.originalPixmap = screen.grab()
        else:
            self.originalPixmap = QPixmap()
        return self.originalPixmap

    @pyqtSlot()
    def recognize(self):
        pixmap = self.take_screenshot()
        rect = QRect(0,0, 800,800)
        pixmap = pixmap.copy(rect)
        scaled = pixmap.scaled(28,28).toImage()
        scaled = self.convertQImageToMat(scaled)
        gray = cv2.cvtColor(scaled , cv2.COLOR_RGBA2GRAY)
        arr = np.array(gray).reshape(28,28)
        arr = arr / 255.
        fd = hog(arr, orientations=9, pixels_per_cell=(14, 14), cells_per_block=(1, 1),
                 visualise=False)
        predict = self.recognizer.mlp.predict(fd)
        number = int(predict[0])
        msg = self.msg%(number, )
        self.label.setText(msg)


    @pyqtSlot()
    def clear(self):
        if len(self.p) != 0:
            self.p = []
            self.update()

    def convertQImageToMat(self,incomingImage):
        '''  Converts a QImage into an opencv MAT format  '''
        incomingImage = incomingImage.convertToFormat(4)
        width = incomingImage.width()
        height = incomingImage.height()
        ptr = incomingImage.bits()
        ptr.setsize(incomingImage.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)  # Copies the data
        return arr

app = QApplication(sys.argv)
ex = MouseTracker()
sys.exit(app.exec_())