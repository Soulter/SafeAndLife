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

    def send_from_http(self, text, color=[0, 255, 255]):
        url = f"http://{self.host}:{self.port_http}/api/v3/notify"
        print(url)
        data = {
            "force": True,
            "text": text,
            "color": [0, 255, 255],
            "count": 2
        }
        data = json.dumps(data)
        res = requests.post(url, data=data, headers={"Content-Type": "application/json"})
        print(res.text)


if __name__ == "__main__":
    awtrix = Awtrix("117.50.192.172", 1883, "123456", 7000)
    json_str = """{"get": "installedApps"}"""
    awtrix.send_from_http("Soulter")
    # awtrix.send_from_mqtt(json_str)
    # awtrix.get_from_mqtt("awtrix/response")

# curl -d {"force":true,"text":"Awesome","icon":1,"color":[0,255,255],"count":2} -H "Content-Type: application/json" -X POST http://[HOST_IP]:7000/api/v3/notify
