# IMPORT LIBRARIES
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import ImageTk, Image
import cv2
import imutils
import paho.mqtt.client as mqtt
import base64
import numpy as np
import pathlib
import hubconf


# DEFINE VARIABLES
object = None
detectionPlace = None
showStream = False


# ROOT CONFIGURATION
root = tk.Tk()
root.title("Demonstrative application")
root.config(bg="bisque")
root.geometry("1000x600")
root.resizable(False, False)
root.iconbitmap('assets/drone.ico')


# FUNCTIONS
def EndConnections():
    try:
        videoStream_client.publish("VideoStreamClient/cameraService/stopVideoStream")
        videoStream_client.unsubscribe("cameraService/VideoStreamClient/videoFrame")
        videoStream_client.loop_stop()
    except:
        pass
    root.destroy()


def show_stream():
    global showStream
    showStream = True


def stop_stream():
    global showStream
    showStream = False


def load_model(weights_path):
    # Needed to solve "Error: cannot instantiate 'PosixPath' on your system" in Windows
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath

    # Loading the model (pytorch-hub is not needed if yolov5 is cloned and with requirements intalled)
    myModel = hubconf.custom(path=weights_path)  # custom

    return myModel


def on_connect_videoStream(external_client, userdata, flags, rc):
    if rc == 0:
        print("Camera - Connection OK")
    else:
        print("Camera - Bad connection")


def on_message_videoStream(client, userdata, message):
    if message.topic == "cameraService/VideoStreamClient/videoFrame":
            img = base64.b64decode(message.payload)
            # converting into numpy array from buffer
            npimg = np.frombuffer(img, dtype=np.uint8)
            # Decode to Original Frame
            img = cv2.imdecode(npimg, 1)
            # Resize image
            img = cv2.resize(img, (640, 480))
            # Convert to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            #####################################################
            # Inference
            pred = client.model(img)
            # xmin,ymin,xmax,ymax
            df = pred.pandas().xyxy[0]
            # Filter by confidence
            df = df[df["confidence"] > 0.5]

            for i in range(df.shape[0]):
                bbox = df.iloc[i][["xmin", "ymin", "xmax", "ymax"]].values.astype(int)

                # Give land order if object is detected
                if df.iloc[i]['name'] == object and df.iloc[i]['confidence'] > 0.6:
                    print(f"{df.iloc[i]['name']} detected. Sending land order...")
                    # publish land order (autopilotService)
                    autopilot_client.publish("AutopilotClient/autopilotService/land")
                    # publish stopVideostream and unsubscribe from video frame (cameraService)
                    videoStream_client.publish("VideoStreamClient/cameraService/stopVideoStream")
                    videoStream_client.unsubscribe("cameraService/VideoStreamClient/videoFrame")
                    # stop the loop of videoStream_client
                    videoStream_client.loop_stop()


                # print bboxes: frame -> (xmin, ymin), (xmax, ymax)
                cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)
                # print text
                cv2.putText(img,
                            f"{df.iloc[i]['name']}: {round(df.iloc[i]['confidence'], 4)}",
                            (bbox[0], bbox[1] - 15),
                            cv2.FONT_HERSHEY_PLAIN,
                            1,
                            (255, 255, 255),
                            2)
            #####################################################

            if showStream == True:
                # Show image (converted to a Tkinter compatible PhotoImage object) in videoStream_label
                imgtk = ImageTk.PhotoImage(Image.fromarray(img))

                videoStream_label.configure(image=imgtk)
                videoStream_label.imgtk = imgtk



def on_connect_autopilot(external_client, userdata, flags, rc):
    if rc == 0:
        print("Autopilot - Connection OK")
    else:
        print("Autopilot - Bad connection")


def connect():
    global videoStream_client
    global autopilot_client

    # Just in case the Connect button is pressed more than once
    try:
        videoStream_client.publish("VideoStreamClient/cameraService/stopVideoStream")
        videoStream_client.unsubscribe("cameraService/VideoStreamClient/videoFrame")
        videoStream_client.loop_stop()
    except:
        pass

    try:
        global object
        global detectionPlace
        object = objects_dropdown.get()
        detectionPlace = detectionPlaces_dropdown.get()

        if detectionPlace == "On board":
            pass
        elif detectionPlace == "Ground station":
            # Video stream client
            videoStream_client = mqtt.Client("VideoStreamClient", transport="websockets")
            videoStream_client.on_connect = on_connect_videoStream
            videoStream_client.on_message = on_message_videoStream
            videoStream_client.connect("broker.hivemq.com", 8000)

            # Autopilot client
            autopilot_client = mqtt.Client("AutopilotClient", transport="websockets")
            autopilot_client.on_connect = on_connect_autopilot
            # autopilot_client.on_message = on_message_autopilot
            autopilot_client.connect("broker.hivemq.com", 8000)

            # Load model depending on the selected object
            if object == "Tin can":
                weights_path = 'weights/demonstrative-app/tin-can.pt'
            elif object == "Book":
                weights_path = 'weights/demonstrative-app/book.pt'
            model = load_model(weights_path)
            videoStream_client.model = model

            # Publish startVideoStream and subscribe to videoFrame (cameraService)
            videoStream_client.publish("VideoStreamClient/cameraService/startVideoStream")
            videoStream_client.subscribe("cameraService/VideoStreamClient/videoFrame")
            videoStream_client.loop_start()

    except:
        messagebox.showerror("Error", "Please try again.")



# LABELS, COMBOBOXES, BUTTONS
# objects dropdown menu
objects = ['Tin can', 'Book']
objects_label = tk.Label(root, text='Select an object:')
objects_label.grid(row=1, column=0, sticky="W", padx=10, pady=10)
objects_dropdown = ttk.Combobox(root, state='readonly', values=objects)
objects_dropdown.bind("<<ComboboxSelected>>", lambda e: root.focus()) # to remove highlighting of the chosen object
objects_dropdown.grid(row=2, column=0, sticky="W", padx=10)

# place of detection dropdown menu
detectionPlaces = ['On board', 'Ground station']
detectionPlaces_label = tk.Label(root, text='Select where you want the detection to take place:')
detectionPlaces_label.grid(row=3, column=0, sticky="W", padx=10, pady=10)
detectionPlaces_dropdown = ttk.Combobox(root, state='readonly', values=detectionPlaces)
detectionPlaces_dropdown.bind("<<ComboboxSelected>>", lambda e: root.focus()) # to remove highlighting of the chosen object
detectionPlaces_dropdown.grid(row=4, column=0, sticky="W", padx=10)

# connect button
connect_button = tk.Button(root, text='CONNECT', command=connect)
connect_button.grid(row=5, column=0, sticky="WE", pady=10)

# video stream buttons
showStream_button = tk.Button(root, text='Show stream', command=show_stream)
showStream_button.grid(row=0, column=1, pady=10)
stopStream_button = tk.Button(root, text='Stop stream', command=stop_stream)
stopStream_button.grid(row=0, column=2, pady=10)

# Label to show video stream
img = Image.open('assets/videoStream_label-size.jpg')
tkimage = ImageTk.PhotoImage(img)
videoStream_label = tk.Label(root, image=tkimage)
videoStream_label.grid(row=1, column=1, rowspan=1000, columnspan=2)


# RUN THE APP
root.protocol("WM_DELETE_WINDOW", EndConnections) # Just in case the app is closed and the videoStream_client is still running
root.mainloop()
