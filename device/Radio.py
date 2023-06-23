import RPI.GPIO as GPIO
import util.general_utils as gu
import time
import threading

# Board
class Radio:
    def __init__(self, TRIG, ECHO) -> None:
        self.TRIG = TRIG
        self.ECHO = ECHO
        GPIO.setup(TRIG, GPIO.OUT)
        GPIO.setup(ECHO, GPIO.IN)

    def distance(self):
        GPIO.output(self.TRIG, 0)
        time.sleep(0.000002)

        GPIO.output(self.TRIG, 1)
        time.sleep(0.00001)
        GPIO.output(self.TRIG, 0)

        while GPIO.input(self.ECHO) == 0:
            pass
        t1 = time.time()
        while GPIO.input(self.ECHO) == 1:
            pass
        t2 = time.time()

        return (t2 - t1) * 340 / 2 * 100
    
    def distance_thread(self, callback):
        while True:
            callback(self.distance())
            time.sleep(1)

    def start(self, callback):
        gu.log("Radio -> start", level=gu.LEVEL_INFO, tag="Radio")
        threading.Thread(target=self.distance_thread, args=(callback,)).start()