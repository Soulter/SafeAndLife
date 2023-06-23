import RPI.GPIO as GPIO
import util.general_utils as gu
import time
import threading

class Beep:
    def __init__(self, pin) -> None:
        self.p = pin
        GPIO.setup(pin, GPIO.OUT) # 设置有源蜂鸣器管脚为输出模式
        GPIO.output(pin, GPIO.HIGH) # 蜂鸣器设置为高电平，关闭.

    def beep_thread(self, route: list):
        gu.log("beep -> on", level=gu.LEVEL_INFO, tag="Beep")
        for r in route:
            GPIO.output(self.p, GPIO.LOW)
            time.sleep(r)
            GPIO.output(self.p, GPIO.HIGH)
            time.sleep(r)

    
    def beep(self, route: list):
        '''
        route: 奇数位为响，偶数位为不响，单位为秒
        '''
        threading.Thread(target=self.beep_thread, args=(route,)).start()
