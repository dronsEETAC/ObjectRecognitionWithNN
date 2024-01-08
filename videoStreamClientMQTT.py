import cv2 as cv
import paho.mqtt.client as mqtt
import base64
import threading
import time
import numpy as np

def on_connect(external_client, userdata, flags, rc):
    if rc == 0:
        print("Connection OK")
    else:
        print("Bad connection")

def on_message(client, userdata, message):

    if message.topic == "videoStreamServerFrame":
            img = base64.b64decode(message.payload)
            # converting into numpy array from buffer
            npimg = np.frombuffer(img, dtype=np.uint8)
            # Decode to Original Frame
            img = cv.imdecode(npimg, 1)
            # show stream in a separate opencv window
            img = cv.resize(img, (640, 480))
            cv.imshow("Stream", img)
            cv.waitKey(1)


client = mqtt.Client("VideoStreamClient", transport="websockets")
client.on_connect = on_connect
client.on_message = on_message
username = 'dronsEETAC'
password = 'mimara1456.'

client.username_pw_set(username, password)
client.connect("classpip.upc.edu", 8000)
client.subscribe('videoStreamServerFrame')
client.loop_forever()

