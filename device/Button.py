import RPI.GPIO as GPIO
import util.general_utils as gu

class Button:
    def __init__(self, pin, callback) -> None:
        self.pin = pin
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=callback, bouncetime=300)