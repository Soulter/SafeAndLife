from paho.mqtt import client as mqtt_client
import requests
import json
class Awtrix:
    def __init__(self, host, port, token, port_http) -> None:
        self.host = host
        self.port = port
        self.token = token
        self.port_http = port_http
        self.client = mqtt_client.Client()
        i = self.client.connect(host, port)
        self.client.loop_start()

    def send_from_mqtt(self, text):
        self.client.publish(f"awtrix/notify", text)
    
    def get_from_mqtt(self, topic):
        self.client.subscribe(topic)
        self.client.on_message = self.on_message
        self.client.loop_forever()

    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))

    def send_from_http(self, text="", color=[0, 255, 255], override_data=None):
        url = f"http://{self.host}:{self.port_http}/api/v3/notify"

        data = {
            "force": True,
            "text": text,
            "color": color,
            "repeat": 1
        }

        if override_data != None:
            data = override_data

        data = json.dumps(data)
        res = requests.post(url, data=data, headers={"Content-Type": "application/json"})
        print(res.text)

if __name__ == "__main__":
    awtrix = Awtrix("117.50.192.172", 1883, "123456", 7000)
    
    # json_str = """{"get": "installedApps"}"""
    # awtrix.send_from_http("Soulter")
    # awtrix.send_from_http(override_data={
    #     "fallingText":True,
    #     "data":"Geht gut das Ding",
    #     "rainbow":True,
    #     "force":True
    # })

    # awtrix.send_from_http(override_data={
    #     "force":True,
    #     "drawing":True,
    #     "data":[
    #         {
    #         "type": "fill",
    #         "color": [100,100,100]
    #         },
    #         {
    #         "type": "text",
    #         "string": "Hello",
    #         "position": [0,0],
    #         "color": [255,0,0]
    #         },
    #         {
    #         "type": "show"
    #         },
    #         {
    #         "type": "wait",
    #         "ms": 3000
    #         },
    #         {
    #         "type": "circle",
    #         "radius": 3,
    #         "position": [24,3],
    #         "color": [255,0,255]
    #         },
    #         {
    #         "type": "show"
    #         },
    #         {
    #         "type": "wait",
    #         "ms": 3000
    #         },
    #         {
    #         "type": "clear"
    #         },
    #         {
    #         "type": "line",
    #         "start": [0,0],
    #         "end": [31,7],
    #         "color": [255,255,255]
    #         },
    #         {
    #         "type": "show"
    #         },
    #         {
    #         "type": "wait",
    #         "ms": 3000
    #         },
    #         {
    #         "type": "exit"
    #         }
    #     ]
    # })
    # awtrix.send_from_mqtt(json_str)
    # awtrix.get_from_mqtt("awtrix/response")
