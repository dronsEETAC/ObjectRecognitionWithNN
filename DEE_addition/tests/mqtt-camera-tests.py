import base64
import cv2
import numpy as np
import paho.mqtt.client as mqtt


def on_connect(external_client, userdata, flags, rc):
    if rc == 0:
        print("Connection OK")
    else:
        print("Bad connection")


def on_message(client, userdata, message):
    if message.topic == "cameraService/VideoStreamClient/videoFrame":
        img = base64.b64decode(message.payload)
        # converting into numpy array from buffer
        npimg = np.frombuffer(img, dtype=np.uint8)
        # Decode to Original Frame
        img = cv2.imdecode(npimg, 1)

        img = cv2.resize(img, (640, 480))

        # show stream in a separate opencv window
        cv2.imshow("Stream", img)
        cv2.waitKey(1)



client = mqtt.Client("VideoStreamClient", transport="websockets")
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.hivemq.com", 8000)
client.publish("VideoStreamClient/cameraService/startVideoStream")
client.subscribe("cameraService/VideoStreamClient/videoFrame")
client.loop_forever()
