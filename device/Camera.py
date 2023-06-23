# import RPI.GPIO as GPIO
# import util.general_utils as gu
import time
import threading
import cv2
# import imutils
import numpy as np
import os

class Camera:
    def __init__(self) -> None:
        pass

    # 采集人脸特征
    def collect(self, name):
        # 加载人脸分类器
        face_cascade = cv2.CascadeClassifier('/home/pi/.local/lib/python3.7/site-packages/cv2/data/haarcascade_frontalface_default.xml')
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
        face_threshold = 30
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
                cv2.imwrite('dataset/' + str(count) + '.jpg', gray[y:y + h, x:x + w])
                # 显示人脸个数
                cv2.putText(frame, 'num:%d/30' % (count), (x + 30, y + 30), font, 1, color, stroke)
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
    def train(self, name):
        print("Training...")
        # 读取人脸特征
        faces, ids = self.read_path('dataset')

        # 加载人脸识别器
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        # 训练
        recognizer.train(faces, np.array(ids))
        # 保存训练结果
        recognizer.save('trainer/trainer.yml')
        print("Train success!")

    # 读取dataset/目录下的人脸特征
    def read_path(self, path_name):
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
                path = os.path.join(path, file_name)
                # 读取图片
                img = cv2.imread(path)
                # 转换为灰度图
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # 人脸检测
                faces.append(gray)
                # 获取id, id为文件名中的第一个数字
                ids.append(int(file_name.split('.')[0]))
        # 返回人脸特征和id
        return faces, ids
    
    # 识别人脸特征
    def recognize(self):
        # 加载人脸分类器
        face_cascade = cv2.CascadeClassifier('./.local/lib/python3.7/site-packages/cv2/data/haarcascade_frontalface_default.xml')
        # 加载LBPH人脸识别器
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        # 读取训练数据
        recognizer.read('trainer/trainer.yml')
        # 设置字体
        font = cv2.FONT_HERSHEY_SIMPLEX
        # 设置颜色
        color = (255, 255, 255)
        # 设置线宽
        stroke = 2
        # 设置阈值
        face_threshold = 30
        # 设置人脸个数
        count = 0
        # 打开摄像头
        cap = cv2.VideoCapture(0)
        # 设置摄像头分辨率
        cap.set(3, 640)
        cap.set(4, 480)
        while True:
            # 读取摄像头数据
            ret, frame = cap.read()
            # 转换为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 人脸检测
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            # 识别人脸
            for (x, y, w, h) in faces:
                # 画矩形框
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, stroke)
                # 预测人脸
                Id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
                # 设置阈值
                if (confidence < 100):
                    # 显示人名和置信度
                    cv2.putText(frame, '%s - %.0f' % ("Master", confidence), (x + 30, y + 30), font, 1, color, stroke)
                    # 人脸个数增加
                    count += 1
                else:
                    # 显示未识别
                    cv2.putText(frame, 'not recognized', (x + 30, y + 30), font, 1, color, stroke)
            # 显示图像
            cv2.imshow('frame', frame)
            # 等待退出
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            # 识别够30个人脸后退出
            # elif count >= face_threshold:
            #     break
        # 释放摄像头
        cap.release()
        # 关闭窗口
        cv2.destroyAllWindows()
        

if __name__ == '__main__':
    camera = Camera()
    camera.collect('Soulter')
    camera.train('Soulter')
    camera.recognize()
    
