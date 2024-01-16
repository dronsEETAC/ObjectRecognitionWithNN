import cv2 as cv
import paho.mqtt.client as mqtt
import base64
import threading
import time
import numpy as np

#####################################################
import hubconf
import pathlib
#####################################################


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

            img = cv.resize(img, (640, 480))

            #####################################################
            # Inference
            pred = client.model(img)
            # xmin,ymin,xmax,ymax
            df = pred.pandas().xyxy[0]
            # Filter by confidence
            df = df[df["confidence"] > 0.5]

            for i in range(df.shape[0]):
                bbox = df.iloc[i][["xmin", "ymin", "xmax", "ymax"]].values.astype(int)

                # print bboxes: frame -> (xmin, ymin), (xmax, ymax)
                cv.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)
                # print text
                cv.putText(img,
                            f"{df.iloc[i]['name']}: {round(df.iloc[i]['confidence'], 4)}",
                            (bbox[0], bbox[1] - 15),
                            cv.FONT_HERSHEY_PLAIN,
                            1,
                            (255, 255, 255),
                            2)
            #####################################################


            # show stream in a separate opencv window
            cv.imshow("Stream", img)
            cv.waitKey(1)


#####################################################
# LOAD MODEL
def load_model(weights_path):
    # Needed to solve "Error: cannot instantiate 'PosixPath' on your system" in Windows
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath

    # Loading the model (pytorch-hub is not needed if yolov5 is cloned and with requirements intalled)
    myModel = hubconf.custom(path=weights_path)  # custom

    return myModel
#####################################################


def start_mqtt(weights_path):
    client = mqtt.Client("VideoStreamClient", transport="websockets")
    client.on_connect = on_connect
    client.on_message = on_message
    username = 'dronsEETAC'
    password = 'mimara1456.'

    client.username_pw_set(username, password)
    client.connect("classpip.upc.edu", 8000)
    client.subscribe('videoStreamServerFrame')
    #####################################################
    # Set the model as a client parameter
    client.model = load_model(weights_path=weights_path)
    #####################################################
    client.loop_forever()


if __name__ == '__main__':
    start_mqtt(weights_path='../weights/best.pt')
