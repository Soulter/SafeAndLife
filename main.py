from device.Beep import Beep
from device.LED import LED
from device.Camera import Camera
from device.Radio import Radio
from device.RainDetector import RainDetector
from device.Button import Button
from ui.Awtrix import Awtrix
from ui.QQ import QQ
import util.general_utils as gu
import threading
import time
from ui.QQ import QQ
from nakuru import (
    CQHTTP,
    GroupMessage,
    GroupMemberIncrease,
    FriendMessage,
    GuildMessage
)
from nakuru.entities.components import Plain,At
import asyncio
from util.cmd_config import CmdConfig as cc
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
camera: Camera = None

radio_obj_near_cnt = 0
radio_distance_threshold = 50

in_detect_face = False
master_in_home = False

gocq_loop = None
gocq_app = None
gocq_bot:QQ = None
PLATFORM_GOCQ = 'gocq'

def new_sub_thread(func, args=()):
    thread = threading.Thread(target=func, args=args, daemon=True)
    thread.start()

def oper_qq_msg(message):
    qq_msg = ""
    if message.type == "FriendMessage":
        for i in message.message:
            if isinstance(i, Plain):
                qq_msg += i.text
    qq_msg = qq_msg.strip()
    gu.log(f"QQ消息: {qq_msg}", gu.LEVEL_INFO, "QQ")

# QQ机器人
class gocqClient():
    @gocq_app.receiver("FriendMessage")
    async def _(app: CQHTTP, source: FriendMessage):
        if isinstance(source.message[0], Plain):
            new_sub_thread(oper_qq_msg, (source))
        else:
            return
        
class FakeFriendSource:
    def __init__(self, user_id):
        self.user_id = user_id
        self.type = "FriendMessage"

def device_init():
    global beep, led, radio, rain, button, camera
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    gu.log(f"======初始化各传感器======", gu.LEVEL_INFO, "System")
    gu.log(f"|-蜂鸣器", gu.LEVEL_INFO, "System")
    beep = Beep(BEEP_PIN)
    gu.log(f"|-LED", gu.LEVEL_INFO, "System")
    led = LED(LED_R_PIN, LED_G_PIN)
    gu.log(f"|-超声", gu.LEVEL_INFO, "System")
    radio = Radio(RADIO_PIN)
    gu.log(f"|-雨滴", gu.LEVEL_INFO, "System")
    rain = RainDetector(RAIN_PIN)
    gu.log(f"|-按钮", gu.LEVEL_INFO, "System")
    button = Button(BUTTON_PIN)
    gu.log(f"|-摄像头", gu.LEVEL_INFO, "System")
    camera = Camera()

def platform_init():
    global awtrix, gocq_loop, gocq_app, gocq_bot

    gu.log(f"======初始化各平台======", gu.LEVEL_INFO, "System")
    gu.log(f"======连接到Awtrix后端云======", gu.LEVEL_INFO, "System")
    awtrix = Awtrix("117.50.192.172", 1883, "123456", 7000)

    gu.log(f"======连接到远端GOCQ======", gu.LEVEL_INFO, "System")
    gocq_loop = asyncio.new_event_loop()
    gocq_bot = QQ(True, cc, gocq_loop)
    
    gocq_app = CQHTTP(
        host="117.50.192.172",
        port=6700,
        http_port=5700,
    )
    thread_inst = threading.Thread(target=run_gocq_bot, args=(gocq_loop, gocq_bot, gocq_app), daemon=False)
    thread_inst.start()

def run_gocq_bot(loop, gocq_bot, gocq_app):
    asyncio.set_event_loop(loop)
    gu.log("正在检查本地GO-CQHTTP连接...端口5700, 6700", tag="QQ")
    while True:
        if not gu.port_checker(5700) or not gu.port_checker(6700):
            gu.log("与GO-CQHTTP通信失败, 请检查GO-CQHTTP是否启动并正确配置。5秒后自动重试。", gu.LEVEL_CRITICAL, tag="QQ")
            time.sleep(5)
        else:
            gu.log("检查完毕，未发现问题。", tag="QQ")
            break

    global gocq_client
    gocq_client = gocqClient()
    try:
        gocq_bot.run_bot(gocq_app)
    except BaseException as e:
        input("启动QQ机器人出现错误"+str(e))

def radio_callback(distance):
    gu.log(f"distance: {distance}", gu.LEVEL_INFO, "System")
    global radio_obj_near_cnt, radio_distance_threshold, master_in_home
    if distance < radio_distance_threshold:
        radio_obj_near_cnt += 1
    else:
        radio_obj_near_cnt = 0
    # 3次检测到物体靠近
    if radio_obj_near_cnt >= 3:
        # 防止重复检测
        if in_detect_face:
            return
        in_detect_face = True
        gu.log(f"radio detect", gu.LEVEL_INFO, "System")
        gu.log(f"IN DETECT MODE", gu.LEVEL_WARNING, "System")
        # awtrix.send_from_http("Radio detect")
        if camera != None:
            is_master = camera.stranger_detect(5)
            if is_master:
                master_in_home = True
                threading.Thread(target=master_mode).start()
            else:
                led.set_red()
                awtrix.send_from_http("GO OUT!", color=[255, 0, 0])
    else:
        in_detect_face = False
        master_in_home = False
        gu.log(f"OUT DETECT MODE", gu.LEVEL_WARNING, "System")
        led.set_green()

# master在家的模式
def master_mode():
    global master_in_home
    led.set_green()
    awtrix.send_from_http("Welcome home, Master!")
    time.sleep(5)
    while True:
        if not master_in_home:
            break
        pass

def camera_detect_face_callback():  
    gu.log(f"face_detect", gu.LEVEL_INFO, "System")


def rain_callback(res, isRain):
    gu.log(f"rain data: {res} isRain: {isRain}", gu.LEVEL_INFO, "System")


if __name__ == "__main__":
    # init
    gu.log(f"======初始化中======", gu.LEVEL_INFO, "System")
    device_init()
    platform_init()
    gu.log(f"=====初始化完毕=====", gu.LEVEL_INFO, "System")

    gu.log(f"======加载各线程======", gu.LEVEL_INFO, "System")
    # welcome
    led.set_green()
    radio.start(radio_callback)
    rain.start(rain_callback)
    awtrix.send_from_http("Welcome to Smart Home!")
    gocq_bot.send_qq_msg(FakeFriendSource(905617992), "Welcome to Smart Home!")
    gu.log(f"=====加载各线程完毕=====", gu.LEVEL_INFO, "System")

    # face data check
    if gu.check_filefolder("trainer") == 0:
        gu.log(f"======未检测到任何人脸数据，开始录入======", gu.LEVEL_INFO, "System")
        awtrix.send_from_http("Face data record")
        camera._collect()
        camera._train("Soulter")
        gu.log(f"=====录入完毕=====", gu.LEVEL_INFO, "System")

    while True:
        pass

