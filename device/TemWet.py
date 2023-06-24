import RPi.GPIO as GPIO
import Adafruit_DHT as DHT
import util.general_utils as gu
import time
import threading

class TemWet():
    def __init__(self) -> None:
        self.type = DHT.DHT11

    def detect(self):
        humidity, temp = DHT.read_retry(self.type, 17)
        return temp, humidity
    
    def detect_thread(self, callback):
        while True:
            # temp, humidity = self.detect()
            import random
            temp = random.randint(3000, 3100)/100
            humidity = random.randint(5000, 5100)/100
            callback(temp, humidity)
            time.sleep(60)

    def start(self, callback):
        gu.log("TemWet -> start", level=gu.LEVEL_INFO, tag="TemWet")
        threading.Thread(target=self.detect_thread, args=(callback,)).start()