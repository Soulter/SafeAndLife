import datetime
from addons.todo.todo import Todo
from ui.Awtrix import Awtrix
import time

def draw_basic_info(awtrix, todo:Todo, weather=None):
    today = datetime.date.today().strftime("%Y年%m月%d日")

    todos = todo.get_by_time(today)
    todos = [i for i in todos if i["status"] == 0]
    awtrix.send_from_http(override_data={
        "fallingText":True,
        "data":"TODAY TODO",
        "rainbow":True,
        "force":True,
        "speed":1000
    })
    awtrix.send_from_http(override_data={
        "text":f"TODO:{str(len(todos))}",
        "rainbow":True,
        "icon": 1736,
        "background":[33,33,33],
        "repeat":1,
        "duration":5
    })
    time.sleep(2)
    awtrix.send_from_http(override_data={
        "text":todos[0]['content'],
        "rainbow":True,
        "icon": 1736,
        "background":[33,33,33],
        "repeat":2
    })

if __name__ == "__main__":

    awtrix = Awtrix("117.50.192.172", 1883, "123456", 7000)
    todo = Todo()
    weather = None
    draw_basic_info(awtrix, todo, weather)