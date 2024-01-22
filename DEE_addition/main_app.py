# IMPORT LIBRARIES
import time
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
autopilotConnected = False
takenOff = False
connected = False


# ROOT CONFIGURATION
root = tk.Tk()
root.title("Demonstrative application")
root.config(bg="bisque")
root.geometry("1000x600")
root.resizable(False, False)
root.iconbitmap('assets/drone.ico')


# FUNCTIONS
def endConnections():
    try:
        app_client.unsubscribe("cameraService/appClient/videoFrame")
        app_client.publish("appClient/cameraService/stopVideoStream")
        app_client.publish("appClient/cameraService/stopDetection")
        app_client.loop_stop()
    except:
        pass

    try:
        app_client.publish("appClient/autopilotService/disconnect")
    except:
        pass


def endConnections_beforeClosing():
    endConnections()
    root.destroy()


def show_stream():
    global showStream
    showStream = True


def stop_stream():
    global showStream
    showStream = False


def load_model(object):
    # Needed to solve "Error: cannot instantiate 'PosixPath' on your system" in Windows
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath

    model_path = f"weights/demonstrative-app/{object}.pt"
    # Loading the model (pytorch-hub is not needed if yolov5 is cloned and with requirements intalled)
    model = hubconf.custom(path=model_path)  # custom

    return model


def on_connect(external_client, userdata, flags, rc):
    if rc == 0:
        print("Connection OK")
    else:
        print("Bad connection")


def on_message(client, userdata, message):
    if message.topic == "cameraService/appClient/videoFrame":
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
                    client.publish("appClient/autopilotService/land")
                    # publish stopVideostream and unsubscribe from video frame (cameraService)
                    client.publish("appClient/cameraService/stopVideoStream")
                    client.unsubscribe("cameraService/appClient/videoFrame")
                    # stop the loop of videoStream_client
                    client.loop_stop()


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

    if message.topic == "cameraService/appClient/objectDetected":
        client.publish("appClient/cameraService/stopDetection")
        client.publish("appClient/autopilotService/land")
        client.loop_stop()

    if message.topic == "cameraService/appClient/detectionVideoFrame":
            img = base64.b64decode(message.payload)
            # converting into numpy array from buffer
            npimg = np.frombuffer(img, dtype=np.uint8)
            # Decode to Original Frame
            img = cv2.imdecode(npimg, 1)
            # Resize image
            img = cv2.resize(img, (640, 480))
            # Convert to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            if showStream == True:
                # Show image (converted to a Tkinter compatible PhotoImage object) in videoStream_label
                imgtk = ImageTk.PhotoImage(Image.fromarray(img))

                videoStream_label.configure(image=imgtk)
                videoStream_label.imgtk = imgtk


def connect():
    global object
    global detectionPlace
    global app_client
    global autopilotConnected
    global connected

    if connected is True:
        endConnections()
        connect_button.config(text="CONNECT", bg="lime green")
        connected = False

    elif connected is False:
        # Get the quality and period values
        quality = quality_slider.get()
        period = period_slider.get()

        try:
            object = objects_dropdown.get()
            detectionPlace = detectionPlaces_dropdown.get()

            app_client = mqtt.Client("appClient", transport="websockets")
            app_client.on_connect = on_connect
            app_client.on_message = on_message
            app_client.connect("broker.hivemq.com", 8000)

            time.sleep(5)  # give some time to connect before publishing (needed)

            # Publish connect order (autopilotService)
            app_client.publish("appClient/autopilotService/connect")
            autopilotConnected = True

            if detectionPlace == "On board":
                # Publish startDetection and subscribe to objectDetected (cameraService)
                app_client.publish("appClient/cameraService/startDetection", f"{object}/{quality}/{period}")
                app_client.subscribe("cameraService/appClient/objectDetected")
                app_client.subscribe("cameraService/appClient/detectionVideoFrame")
                app_client.loop_start()

            elif detectionPlace == "Ground station":
                # Load model depending on the selected object
                model = load_model(object)
                app_client.model = model

                # Publish startVideoStream and subscribe to videoFrame (cameraService)
                app_client.publish(f"appClient/cameraService/startVideoStream", f"{quality}/{period}")
                app_client.subscribe("cameraService/appClient/videoFrame")
                app_client.loop_start()

            connected = True
            connect_button.config(text="DISCONNECT", bg="indian red")

        except:
            messagebox.showerror("Error", "Please try again.")


def arm_takeoff():
    global takenOff
    if autopilotConnected is True:
        # Publish armDrone & takeOff orders (autopilotService)
        app_client.publish("appClient/autopilotService/armDrone")
        app_client.publish("appClient/autopilotService/takeOff", "2")
        takenOff = True
    else:
        messagebox.showerror("Error", "Please press CONNECT first.")


def flyNorth():
    if autopilotConnected is True:
        if takenOff is True:
            # Publish go North order (autopilotService)
            app_client.publish("appClient/autopilotService/go", "North")
        else:
            messagebox.showerror("Error", "Please ARM & TAKE-OFF first.")
    else:
        messagebox.showerror("Error", "Please press CONNECT first.")


# LABELS, COMBOBOXES, BUTTONS
# detection parameters label
detectionParameters_label = tk.Label(root, text='Detection parameters:', bg="dark orange")
detectionParameters_label.grid(row=0, column=0, sticky="WE", padx=10, pady=(20, 10))

# objects dropdown menu
objects = ['Tin can', 'Book']
objects_label = tk.Label(root, text='Select an object:')
objects_label.grid(row=1, column=0, sticky="W", padx=10, pady=(0, 10))
objects_dropdown = ttk.Combobox(root, state='readonly', values=objects)
objects_dropdown.bind("<<ComboboxSelected>>", lambda e: root.focus()) # to remove highlighting of the chosen object
objects_dropdown.grid(row=2, column=0, sticky="W", padx=10, pady=(0, 10))

# Place of detection dropdown menu
detectionPlaces = ['On board', 'Ground station']
detectionPlaces_label = tk.Label(root, text='Select where you want the detection to take place:')
detectionPlaces_label.grid(row=3, column=0, sticky="W", padx=10, pady=(0, 10))
detectionPlaces_dropdown = ttk.Combobox(root, state='readonly', values=detectionPlaces)
detectionPlaces_dropdown.bind("<<ComboboxSelected>>", lambda e: root.focus()) # to remove highlighting of the chosen object
detectionPlaces_dropdown.grid(row=4, column=0, sticky="W", padx=10, pady=(0, 10))

# Image parameters label
imageParameters_label = tk.Label(root, text='Video stream Image parameters:', bg="dark orange")
imageParameters_label.grid(row=5, column=0, sticky="WE", padx=10, pady=(10, 10))

# Quality and Period sliders
quality_slider = tk.Scale(root, label="Quality:", resolution=10, from_=10, to=100, tickinterval=10, orient=tk.HORIZONTAL)
quality_slider.set(50)
quality_slider.grid(row=6, column=0, sticky="WE", pady=(0, 10))
period_slider = tk.Scale(root, label="Period:", resolution=0.1, from_=0.1, to=1, tickinterval=0.1, orient=tk.HORIZONTAL)
period_slider.set(0.2)
period_slider.grid(row=7, column=0, sticky="WE", pady=(0, 10))

# Connect button
connect_button = tk.Button(root, text='CONNECT', bg="lime green", font='sans 13 bold', command=connect)
connect_button.grid(row=8, column=0, sticky="WE", pady=(10, 10))

# Drone operations label
droneOperations_label = tk.Label(root, text='Drone operations:', bg="dark orange")
droneOperations_label.grid(row=9, column=0, sticky="WE", padx=10, pady=(10, 10))

# Arm & Take-off button
arm_takeoff_button = tk.Button(root, text='ARM & TAKE-OFF', bg="CadetBlue1", font='sans 13 bold', command=arm_takeoff)
arm_takeoff_button.grid(row=10, column=0, sticky="WE", pady=(0, 10))

# Fly North button
flyNorth_button = tk.Button(root, text='FLY NORTH', bg="CadetBlue1", font='sans 13 bold', command=flyNorth)
flyNorth_button.grid(row=11, column=0, sticky="WE", pady=(0, 10))

# Video stream buttons
showStream_button = tk.Button(root, text='Show stream', font='sans 12 bold', command=show_stream)
showStream_button.grid(row=0, column=1, pady=(20, 5))
stopStream_button = tk.Button(root, text='Stop stream', font='sans 12 bold', command=stop_stream)
stopStream_button.grid(row=0, column=2, pady=(20, 5))

# Label to show video stream
img = Image.open('assets/videoStream_label-size.jpg')
tkimage = ImageTk.PhotoImage(img)
videoStream_label = tk.Label(root, image=tkimage)
videoStream_label.grid(row=1, column=1, rowspan=1000, columnspan=2, padx=30)


# RUN THE APP
root.protocol("WM_DELETE_WINDOW", endConnections_beforeClosing) # Just in case the app is closed and the videoStream_client is still running
root.mainloop()
