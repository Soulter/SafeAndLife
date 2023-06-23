import RPI.GPIO as GPIO
import util.general_utils as gu
import time
import threading
import PCF8591 as ADC

# Board
class RainDetector:
    def __init__(self, gpio_pin) -> None:
        self.pin = gpio_pin
        GPIO.setup(gpio_pin, GPIO.IN)
        ADC.setup(0x48)

    def detect(self):
        res = ADC.read(0)
        isRain = False
        if res < 200:
            isRain = True
        return res, isRain
    
    def detect_thread(self, callback):
        while True:
            callback(self.detect())
            time.sleep(5)