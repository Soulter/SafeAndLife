from device.Beep import Beep
from device.LED import LED
from device.Camera import Camera
from device.Radio import Radio
from device.RainDetector import RainDetector
from device.Button import Button
from ui.Awtrix import Awtrix
from ui.QQ import QQ
# from RPI.GPIO import GPIO

BEEP_PIN = 18
LED_R_PIN = 12
LED_G_PIN = 13
BUTTON_PIN = 11
RADIO_PIN = 36
RAIN_PIN = 15

beep: Beep = None
led: LED = None
radio: Radio = None 
rain: RainDetector = None
button: Button = None
awtrix: Awtrix = None

def device_init():
    global beep, led, radio, rain, button
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    beep = Beep(BEEP_PIN)
    led = LED(LED_R_PIN, LED_G_PIN)
    radio = Radio(RADIO_PIN)
    rain = RainDetector(RAIN_PIN)
    button = Button(BUTTON_PIN)

def platform_init():
    global awtrix
    awtrix = Awtrix("117.50.192.172", 1883, "123456", 7000)
    pass

def radio_callback(distance):
    print("distance:", distance)

def camera_detect_face_callback():  
    print("face detected")

def rain_callback(res, isRain):
    print("res:", res, "isRain:", isRain)


if __name__ == "__main__":
    # init
    # device_init()
    # platform_init()

    # # welcome
    # led.set_green()
    # radio.start(radio_callback)
    # rain.start(rain_callback)
    # awtrix.send_from_http("Welcome to Smart Home!")

    # while True:
    #     pass
    camera = Camera()
    camera.collect("Soulter")
    