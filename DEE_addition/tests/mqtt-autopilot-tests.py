import base64
import cv2
import numpy as np
import paho.mqtt.client as mqtt


def on_connect_autopilot(external_client, userdata, flags, rc):
    if rc == 0:
        print("Autopilot - Connection OK")
    else:
        print("Autopilot - Bad connection")


autopilot_client = mqtt.Client("AutopilotClient", transport="websockets")
autopilot_client.on_connect = on_connect_autopilot
# autopilot_client.on_message = on_message_autopilot
autopilot_client.connect("broker.hivemq.com", 8000)

autopilot_client.publish("AutopilotClient/autopilotService/land")
