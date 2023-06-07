import GPIO
import util.general_utils as gu

class LED:
    def __init__(self, Rpin, Gpin) -> None:
        self.r = Rpin
        self.g = Gpin
        GPIO.setup (Rpin,GPIO.OUT) 
        GPIO.setup (Gpin, GPIO.OUT)
    
    def set_red(self):
        gu.log("led -> red", level=gu.LEVEL_INFO, tag="LED")
        GPIO.output(self.r, 1)
        GPIO.output(self.g, 0)

    def set_green(self):
        gu.log("led -> green", level=gu.LEVEL_INFO, tag="LED")
        GPIO.output(self.r, 0)
        GPIO.output(self.g, 1)