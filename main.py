import RPi.GPIO as GPIO
from device.Beep import Beep
from device.LED import LED
from device.Camera import Camera
from device.Radio import Radio
from device.RainDetector import RainDetector
from device.Button import Button
from device.TemWet import TemWet
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
from nakuru.entities.components import Plain,At,Image
import asyncio
from util.cmd_config import CmdConfig as cc
from addons.todo.todo import Todo
from addons.ChatGPT.chatgpt import ChatGPT
import json
import util.awtrix_anis as aa


BEEP_PIN = 18 #24
LED_R_PIN = 35 #19
LED_G_PIN = 38 #20
BUTTON_PIN = 33 #13
RADIO_PIN = 36 #16
ECHO_PIN = 12 #18
RAIN_PIN = 15 

beep: Beep = None
led: LED = None
radio: Radio = None 
rain: RainDetector = None
button: Button = None
awtrix: Awtrix = None
camera: Camera = None
temp_wet: TemWet = None

todo: Todo = None
chatgpt: ChatGPT = None


# 状态
in_detect_face = False
master_in_home = False
stranger_in_home = False
radio_obj_near_cnt = 0
radio_distance_threshold = 100
rain_detect_cnt = 0
rain_detect_threshold = 10
in_rainy = False


gocq_loop = None
gocq_app = None
gocq_bot:QQ = None
PLATFORM_GOCQ = 'gocq'



gocq_app = CQHTTP(
        host="wsqqtest.soulter.top",
        host_http="qqtest.soulter.top",
        port=80,
        http_port=80,
)

# todo_list = []

# QQ机器人
class gocqClient():
    @gocq_app.receiver("FriendMessage")
    async def _(app: CQHTTP, source: FriendMessage):
        if isinstance(source.message[0], Plain):
            new_sub_thread(oper_qq_msg, (source,))
        else:
            return

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
    if qq_msg != "":
        chatgpt_send(qq_msg)


def chatgpt_send(prompt):
    res, raw_message_list = chatgpt.get_completion(prompt)
    raw_message_list.append(res)
    # print(res)
    print(raw_message_list)
    if res.get("function_call"):
        available_functions = {
            "set_todo": set_todo,
            "view_todo": view_todo,
            "finish_todo": finish_todo
        }
        function_name = res["function_call"]["name"]

        if function_name == "set_todo":
            fuction_to_call = available_functions[function_name]
            function_args = json.loads(res["function_call"]["arguments"])
            fuction_to_call(
                resp=raw_message_list,
                content=str(function_args.get("content")),
                date=str(function_args.get("date")),
            )
        elif function_name == "view_todo":
            fuction_to_call = available_functions[function_name]
            function_args = json.loads(res["function_call"]["arguments"])
            fuction_to_call(
                resp=raw_message_list,
                date=str(function_args.get("date")),
                all=function_args.get("all"),
            )
        elif function_name == "finish_todo":
            fuction_to_call = available_functions[function_name]
            function_args = json.loads(res["function_call"]["arguments"])
            fuction_to_call(
                resp=raw_message_list,
                index=int(function_args.get("index")),
            )

def set_todo(resp, content, date, relative=None):
    todo.add(content, date)
    _r = f"已添加待办事项: \n{content} | {date}"
    res_msg = _r
    # res_msg = "{'res':\"" + _r + "\"}"
    # res_msg = chatgpt.func_call_step_2(resp,"set_todo", res_msg)
    gocq_bot.send(to=FakeFriendSource(905617992), res=[Plain(res_msg)])

def view_todo(resp, date, all=False):
    if all:
        todos = todo.get()
    else:
        todos = todo.get_by_time(date)
    res_msg = "===== 待 办 清 单 ===="
    # content, time, status
    for i in range(len(todos)):
        _content = todos[i]['content']
        _time = todos[i]['time']
        _status = todos[i]['status']
        if _status == 0:
            _status = "未完成"
        else:
            _status = "已完成"
        res_msg += f"\n{i+1}. 内容: {_content} \n时间: {_time} \n状态: {_status}\n"

    # res_msg = chatgpt.func_call_step_2(resp,"view_todo", str(todos))
    gocq_bot.send(to=FakeFriendSource(905617992), res=[Plain(res_msg)])

def finish_todo(resp, index):
    if index == -1:
        gocq_bot.send(to=FakeFriendSource(905617992), res=[Plain("删除失败~请重新指定序号呀")])
    todo.finish(index)
    res_msg="完成！"
    # res_msg = chatgpt.func_call_step_2(resp,"finish_todo", "{'res': 'OK'}")
    gocq_bot.send(to=FakeFriendSource(905617992), res=[Plain(res_msg)])
    
        
class FakeFriendSource:
    def __init__(self, user_id):
        self.user_id = user_id
        self.type = "FriendMessage"

def device_init():
    global beep, led, radio, rain, button, camera, temp_wet
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    gu.log(f"======初始化各传感器======", gu.LEVEL_INFO, "System")
    gu.log(f"|-蜂鸣器", gu.LEVEL_INFO, "System")
    time.sleep(0.2)
    beep = Beep(BEEP_PIN)
    gu.log(f"|-LED", gu.LEVEL_INFO, "System")
    time.sleep(0.2)
    led = LED(LED_R_PIN, LED_G_PIN)
    gu.log(f"|-超声", gu.LEVEL_INFO, "System")
    time.sleep(0.2)
    radio = Radio(RADIO_PIN, ECHO_PIN)
    gu.log(f"|-雨滴", gu.LEVEL_INFO, "System")
    time.sleep(0.2)
    rain = RainDetector(RAIN_PIN)
    gu.log(f"|-按钮", gu.LEVEL_INFO, "System")
    time.sleep(0.2)
    button = Button(BUTTON_PIN, btn_press_callback)
    time.sleep(0.2)
    gu.log(f"|-摄像头", gu.LEVEL_INFO, "System")
    camera = Camera()
    gu.log(f"|-温湿度", gu.LEVEL_INFO, "System")
    temp_wet = TemWet()


def addons_init():
    global todo, chatgpt
    todo = Todo()
    chatgpt = ChatGPT("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")

def btn_press_callback(res):
    gu.log(f"btn clicked: {str(res)}", gu.LEVEL_INFO, "System")

    # 输出todo
    todos = todo.get()
    res_msg = "===== 待 办 清 单 ===="
    # content, time, status
    for i in range(len(todos)):
        _content = todos[i]['content']
        _time = todos[i]['time']
        _status = todos[i]['status']
        if _status == 0:
            _status = "未完成"
        else:
            _status = "已完成"
        res_msg += f"\n{i+1}. 内容: {todos[i]['content']} \n时间: {todos[i]['time']} \n状态: {todos[i]['status']}\n"
    
    gocq_bot.send(to=FakeFriendSource(905617992), res=[Plain(res_msg)])

    aa.draw_basic_info(awtrix, todo, None)


def platform_init():
    global awtrix, gocq_loop, gocq_app, gocq_bot

    gu.log(f"======初始化各平台======", gu.LEVEL_INFO, "System")
    time.sleep(0.5)
    gu.log(f"======连接到Awtrix后端云======", gu.LEVEL_INFO, "System")
    time.sleep(0.5)
    awtrix = Awtrix("117.50.192.172", 1883, "123456", 7000)

    gu.log(f"======连接到远端GOCQ======", gu.LEVEL_INFO, "System")
    time.sleep(0.5)
    gocq_loop = asyncio.new_event_loop()
    gocq_bot = QQ(True, cc, gocq_loop)

    threading.Thread(target=run_gocq_bot, args=(gocq_loop, gocq_bot, gocq_app)).start()
    # run_gocq_bot(gocq_loop, gocq_bot, gocq_app)


def run_gocq_bot(loop, gocq_bot, gocq_app):
    asyncio.set_event_loop(loop)
    gu.log("正在执行WebSocket端口连接", tag="QQ")
    gu.log("正在执行Http端口连接", tag="QQ")
    # while True:
    #     if not gu.port_checker(5700) or not gu.port_checker(6700):
    #         gu.log("与GO-CQHTTP通信失败, 请检查GO-CQHTTP是否启动并正确配置。5秒后自动重试。", gu.LEVEL_CRITICAL, tag="QQ")
    #         time.sleep(5)
    #     else:
    #         gu.log("检查完毕，未发现问题。", tag="QQ")
    #         break

    global gocq_client
    gocq_client = gocqClient()
    try:
        gocq_bot.run_bot(gocq_app)
    except BaseException as e:
        input("启动QQ机器人出现错误"+str(e))

def radio_callback(distance):

    global radio_obj_near_cnt, radio_distance_threshold, master_in_home, in_detect_face, stranger_in_home
    # gu.log(f"入测阈值: {radio_obj_near_cnt} | 距离: {int(distance)}cm", gu.LEVEL_INFO, "Debug")
    if distance < radio_distance_threshold:
        if not in_detect_face:
            radio_obj_near_cnt += 1
            gu.log(f"疑似接近, 次数: {radio_obj_near_cnt} | 距离: {int(distance)}cm", gu.LEVEL_INFO, "System")
    else:
        if radio_obj_near_cnt > 0:
            radio_obj_near_cnt -= 1
    # 4次检测到物体靠近
    if radio_obj_near_cnt >= 5:
        # 防止重复检测
        
        if in_detect_face:
            return
        else:
            radio_obj_near_cnt *= 2 # 2*4*2s
        in_detect_face = True
        gu.log(f"IN DETECT MODE", gu.LEVEL_WARNING, "System")
        if camera != None:
            master_sig = camera.stranger_detect(10)
            if master_sig > 0:
                # 主人
                gu.log(f"MASTER DETECTED", gu.LEVEL_WARNING, "System")
                master_in_home = True
                threading.Thread(target=master_mode).start()
            elif master_sig < 0:
                # 陌生人
                radio_obj_near_cnt = 0 # 刷新，来变相重新检测
                in_detect_face = False # 刷新，来变相重新检测
                led.set_red()
                if stranger_in_home:
                    # 如果已经检测到陌生人，就不再检测了
                    pass
                else:
                    gu.log(f"STRANGER DETECTED", gu.LEVEL_WARNING, "System")
                    stranger_in_home = True
                    # 图片转bytes
                    imgp = "detect.jpg"
                    with open(imgp, 'rb') as f:
                        img = f.read()
                    gocq_bot.send(to=FakeFriendSource(905617992), res=[Plain("检测到异常人脸！！"), Image.fromBytes(img)])
                beep.beep([0.1, 0.1, 0.1, 0.1, 0.1])
                awtrix.send_from_http("GO OUT", color=[255, 0, 0])
            else:
                gu.log(f"没有识别到任何人脸，恢复正常模式", gu.LEVEL_WARNING, "System")
                master_in_home = False
                
                stranger_in_home = False
                pass
    if stranger_in_home:
        led.set_red()
    else:
        led.set_green()

    if radio_obj_near_cnt == 0:
        in_detect_face = False
        master_in_home = False
        stranger_in_home = False

# master在家的模式
def master_mode():
    global master_in_home
    led.set_green()
    awtrix.send_from_http("Welcome back, Soulter!", color=[0, 255, 0])
    time.sleep(5)
    while True:
        if not master_in_home:
            break
        pass

def camera_detect_face_callback():  
    gu.log(f"face_detect", gu.LEVEL_INFO, "System")

def rain_callback(res, isRain):
    global rain_detect_cnt, rain_detect_threshold, in_rainy
    if rain_detect_cnt >= rain_detect_threshold and not in_rainy:
        in_rainy = True
        awtrix.send_from_http("Rainy now", color=[0, 0, 255])
        gocq_bot.send("905617992", Plain("下雨了🌧"))

    if isRain:
        if rain_detect_cnt <= rain_detect_threshold:
            gu.log("检测到下雨, cnt自增。", gu.LEVEL_INFO)
            rain_detect_cnt += 1
    else:
        if rain_detect_cnt <= 0:
            pass
        else:
            rain_detect_cnt -= 1
            if rain_detect_cnt == 0:
                in_rainy = False
                gu.log("判断: 停止下雨", gu.LEVEL_INFO)

    # gu.log(f"rain data: {res} isRain: {isRain}", gu.LEVEL_INFO, "System")

def temperature_wet(temp, wet):
    gu.log(f"temp: {temp} wet: {wet}", gu.LEVEL_INFO, "System")

if __name__ == "__main__":
    # init
    gu.log(f"======初始化中======", gu.LEVEL_INFO, "System")
    device_init()
    platform_init()
    addons_init()
    gu.log(f"=====初始化完毕=====", gu.LEVEL_INFO, "System")

    gu.log(f"======加载各线程======", gu.LEVEL_INFO, "System")
    # welcome
    time.sleep(3)
    led.set_green()
    radio.start(radio_callback)
    rain.start(rain_callback)
    temp_wet.start(temperature_wet)
    awtrix.send_from_http("Welcome to Smart Home!", color=[0, 255, 0])
    # gocq_bot.send_qq_msg(FakeFriendSource(905617992), "Welcome to Smart Home!")
    gocq_bot.send(to=FakeFriendSource(905617992), res=[Plain("Welcome to Smart Home!")])
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


