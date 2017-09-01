import cv2, sys, numpy, os


class FaceTrain:
    def __init__(self , name):
        self.count = 0
        self.pause = 0
        self.count_max = 20
        self.size = 1
        self.fn_name = name
        self.path = os.path.join("./att_faces", name)
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        self.im_size = (112, 92)
        self.pin = sorted([int(n[:n.find('.')]) for n in os.listdir(self.path) if n[0] != '.'] + [0])[-1] + 1

    def train(self , frame , cascade):
        print("\n\033[94mThe program will save 20 samples. \
        Move your head around to increase while it runs.\033[0m\n")
        if self.count < self.count_max:
            height, width, channels = frame.shape
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mini = cv2.resize(gray, (int(gray.shape[1] / self.size), int(gray.shape[0] / self.size)))
            faces = cascade.detectMultiScale(mini)
            faces = sorted(faces, key=lambda x: x[3])
            if faces:
                face_i = faces[0]
                (x, y, w, h) = [v * self.size for v in face_i]
                face = gray[y:y + h, x:x + w]
                face_resize = cv2.resize(face, self.im_size)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                cv2.putText(frame, self.fn_name, (x - 10, y - 10), cv2.FONT_HERSHEY_PLAIN,
                    1,(0, 255, 0))
                if(w * 6 < width or h * 6 < height):
                    print("Face too small")
                else:
                    if(self.pause == 0):
                        print("Saving training sample "+str(self.count+1)+"/"+str(self.count_max))
                        cv2.imwrite('%s/%s.png' % (self.path, self.pin), face_resize)
                        self.pin += 1
                        self.count += 1
                        self.pause = 1
            if(self.pause > 0):
                self.pause = (self.pause + 1) % 5
            return False;
        else:
            return True;