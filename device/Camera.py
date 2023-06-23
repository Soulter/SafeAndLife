# import RPI.GPIO as GPIO
import util.general_utils as gu
import time
import threading
import cv2
# import imutils
import numpy as np
import os

pi_haar_path = r'./.local/lib/python3.7/site-packages/cv2/data/haarcascade_frontalface_default.xml'
windows_haar_path = r'C:\Users\90561\AppData\Local\Programs\Python\Python39\Lib\site-packages\cv2\data\haarcascade_frontalface_default.xml'


class Camera:
    def __init__(self) -> None:
        self.signal = False
        pass

    # def detect_face_thread(self, callback):
    #     while True:
    #         if not self.signal:
    #             callback(self.stranger_detect())
    #         time.sleep(5)

    # def start(self, callback):
    #     gu.log("Camera -> start", level=gu.LEVEL_INFO, tag="Camera")
    #     self.signal = True
    #     threading.Thread(target=self.detect_face_thread, args=(callback,)).start()

    # def stop(self):
    #     gu.log("Camera -> stop", level=gu.LEVEL_INFO, tag="Camera")
    #     self.signal = False
    #     pass

    # 采集人脸特征
    def _collect(self):
        # 加载人脸分类器

        face_cascade = cv2.CascadeClassifier(windows_haar_path)
        # 打开摄像头
        cap = cv2.VideoCapture(0)
        # 设置摄像头分辨率
        cap.set(3, 640)
        cap.set(4, 480)
        # 设置字体
        font = cv2.FONT_HERSHEY_SIMPLEX
        # 设置颜色
        color = (255, 255, 255)
        # 设置线宽
        stroke = 2
        # 设置阈值
        face_threshold = 50
        # 设置人脸个数
        count = 1
        while True:
            # 读取摄像头数据
            ret, frame = cap.read()
            # 转换为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 人脸检测
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            # 画矩形框
            for (x, y, w, h) in faces:
                # 画矩形框
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, stroke)
                # 保存人脸图像
                print('save image:', count)
                cv2.imwrite('dataset/' + str(count) + '.jpg', gray[y:y + h, x:x + w])
                # 显示人脸个数
                cv2.putText(frame, 'num:%d/50' % (count), (x + 30, y + 30), font, 1, color, stroke)
                # 人脸个数增加
                count += 1
            # 显示图像
            cv2.imshow('frame', frame)
            # 等待退出
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            # 采集够30个人脸后退出
            elif count >= face_threshold:
                break
        # 释放摄像头
        cap.release()
        # 关闭窗口
        cv2.destroyAllWindows()

    # 从dataset/目录下读取人脸特征,并进行训练
    def _train(self, name):
        print("Training...")
        # 读取人脸特征
        faces, ids = self._read_path('dataset')

        # 加载人脸识别器
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        # 训练
        recognizer.train(faces, np.array(ids))
        # 保存训练结果
        recognizer.save(f'trainer/{name}_face_data.yml')
        print("Train success!")

    # 读取dataset/目录下的人脸特征
    def _read_path(self, path_name):
        # 保存人脸特征
        faces = []
        # 保存人脸id
        ids = []
        # 遍历目录下的所有文件
        for path, dir_names, file_names in os.walk(path_name):
            # 遍历文件
            for file_name in file_names:
                # 如果不是jpg文件则跳过
                if not file_name.endswith('.jpg'):
                    continue
                # 拼接文件路径
                path = path_name + '/' + file_name
                print(path)
                # 读取图片
                img = cv2.imread(path)
                # 转换为灰度图
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # 人脸检测
                faces.append(gray)
                # 获取id, id为文件名中的第一个数字
                ids.append(int(file_name.split('.')[0]))
                os.remove(path_name + '/' + file_name)
        
        # 返回人脸特征和id
        return faces, ids
    
    def stranger_detect(self, face_time_threshold=5):
        # face_time_threshold = 5 # 5s
        return self._recognize(face_time_threshold)
    
    # 识别人脸特征
    def _recognize(self, name, face_frame_threshold=10):
        # 加载人脸分类器
        print("Loading...")
        face_cascade = cv2.CascadeClassifier(windows_haar_path)
        # 加载LBPH人脸识别器
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(f'trainer/{name}.yml')
        print("Load success!")
        font = cv2.FONT_HERSHEY_SIMPLEX
        color = (255, 255, 255)
        stroke = 2
        # 设置人脸个数
        master_count = 0
        # 打开摄像头
        print("open camera")
        cap = cv2.VideoCapture(0)
        print("open camera success")
        print("set camera resolution")
        cap.set(3, 640)
        cap.set(4, 480)
        print("set camera resolution success")

        cap_time = time.time()
        while True:
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            # 识别人脸
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, stroke)
                Id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
                # 设置阈值
                if (confidence < 50):
                    # 显示人名和置信度
                    cv2.putText(frame, '%s - %.0f' % ({name}, confidence), (x + 30, y + 30), font, 1, color, stroke)
                    master_count += 1
                else:
                    master_count -= 1
                    # 显示未识别
                    cv2.putText(frame, 'not recognized', (x + 30, y + 30), font, 1, color, stroke)
            cv2.imshow('frame', frame)
            # 等待退出
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break

            # face_frame_threshold是秒数
            if time.time() - cap_time > face_frame_threshold: 
                break
        cap.release()
        cv2.destroyAllWindows()
        if master_count > 0:
            return True
        else:
            return False
        

if __name__ == '__main__':
    camera = Camera()
    camera._collect('Soulter')
    camera._train('Soulter')
    camera._recognize()
    
