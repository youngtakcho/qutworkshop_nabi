# facerec.py
import cv2, sys, numpy, os


class FaceRec:
    def __init__(self):
        self.size = 1
        self.fn_haar = 'haarcascade_frontalface_default.xml'
        self.fn_dir = 'att_faces'

    def learn(self):
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
                    images.append(cv2.imread(path, 0))
                    lables.append(int(lable))
                self.id += 1
        self.im_size = (112, 92)
        (images, lables) = [numpy.array(lis) for lis in [images, lables]]
        self.model = cv2.face.createFisherFaceRecognizer()
        self.model.train(images, lables)

    def recogize(self, frame, gray, cascade):
        haar_cascade = cascade
        mini = cv2.resize(gray, (int(gray.shape[1] / self.size), int(gray.shape[0] / self.size)))
        faces = haar_cascade.detectMultiScale(mini)
        for i in range(len(faces)):
            face_i = faces[i]
            (x, y, w, h) = [v * self.size for v in face_i]
            face = gray[y:y + h, x:x + w]
            face_resize = cv2.resize(face, self.im_size)
            prediction = self.model.predict(face_resize)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            print(self.names[prediction])
            cv2.putText(frame,
                        '%s' % (self.names[prediction],),
                        (x - 10, y - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
        return frame
