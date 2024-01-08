import os

import cv2 as cv
import paho.mqtt.client as mqtt
import base64
import threading
import time




def on_connect(external_client, userdata, flags, rc):
    if rc == 0:
        print("Connection OK")
    else:
        print("Bad connection")

def send_video_stream(client, quality, frequency):
    cap = cv.VideoCapture(0)

    while True:
        # Read Frame
        ret, frame = cap.read()
        if ret:
            encode_param = [int(cv.IMWRITE_JPEG_QUALITY), quality]
            _, frame = cv.imencode(".jpg", frame,encode_param)

            print('size: ', frame.shape[0]) # asi vemos el tamaño de la imagen
            jpg_as_text = base64.b64encode(frame)
            client.publish('videoStreamServerFrame', jpg_as_text)
            time.sleep(frequency)




client = mqtt.Client("VideoStreamServer", transport="websockets")
client.on_connect = on_connect
username = 'dronsEETAC'
password = 'mimara1456.'

client.username_pw_set(username, password)
client.connect("classpip.upc.edu", 8000)
client.loop_start()
quality = 50
# valor entre 1 y 100. Cuanto mas grande mayor es a calidad de a imagen
# pero ocupa más bytes y más retraso tendrá la transmisión a través del broker
frequency = 0.2 # un frame cada 0.2 segundos
send_video_stream(client, quality, frequency)
