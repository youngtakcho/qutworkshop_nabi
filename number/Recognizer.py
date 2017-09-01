import cv2, os
import numpy as np
from sklearn.datasets import fetch_mldata
from sklearn.externals import joblib
from skimage.feature import hog
from sklearn.neural_network import MLPClassifier

class DigitRecognizer():
    def __init__(self):
        pass

    def learn(self):
        mnist = fetch_mldata("MNIST original")
        load = False
        try:
            self.mlp = joblib.load("digits_cls.pkl")
            load = True
        except:
            self.mlp = None

        if load:
            return
        X, y = mnist.data / 255., mnist.target
        list_hog_fd = []
        for feature in X:
            fd = hog(feature.reshape((28, 28)), orientations=9, pixels_per_cell=(14, 14), cells_per_block=(1, 1),
                     visualise=False)
            list_hog_fd.append(fd)
        hog_features = np.array(list_hog_fd, 'float64')

        X = hog_features

        X_train = X[0:60000]
        X_test = X[60000:len(X)]
        y_train = y[0:60000]
        y_test = y[60000:len(y)]

        print(X_train.shape, ",", X_test.shape)

        self.mlp = MLPClassifier(hidden_layer_sizes=(100, 150), max_iter=300, alpha=1e-2,
                                 solver='sgd', verbose=1, tol=1e-4, random_state=1,
                                 learning_rate_init=.1, shuffle=True)

        self.mlp.fit(X_train, y_train)
        joblib.dump(self.mlp, "digits_cls.pkl", compress=3)
        print("Training set score: %f" % self.mlp.score(X_train, y_train))
        print("Test set score: %f" % self.mlp.score(X_test, y_test))


    def recogize(self, frame, gray, s_max, s_min):
        im = frame
        im2, ctrs, hier = cv2.findContours(gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        rects = [cv2.boundingRect(ctr) for ctr in ctrs]
        for rect in rects:
            if rect[2] < s_min or rect[2] > s_max or rect[3] < s_min or rect[3] > s_max:
                continue
            cv2.rectangle(im, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (0, 255, 0), 3)
            leng = int(rect[3] * 1.6)
            pt1 = int(rect[1] + rect[3] // 2 - leng // 2)
            pt2 = int(rect[0] + rect[2] // 2 - leng // 2)
            if pt1 < 0 or pt2 < 0:
                continue
            roi = gray[pt1:pt1 + leng, pt2:pt2 + leng]
            roi = cv2.resize(roi, (28, 28), interpolation=cv2.INTER_AREA)
            roi = cv2.dilate(roi, (3, 3))
            roi_hog_fd = hog(roi, orientations=9, pixels_per_cell=(14, 14), cells_per_block=(1, 1), visualise=False)
            nbr = self.mlp.predict(np.array([roi_hog_fd], 'float64'))
            cv2.putText(im, str(int(nbr)), (rect[0], rect[1]), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 255), 3)
        return im, gray