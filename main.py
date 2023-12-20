import cv2
from time import time
import pandas
import torch

from user import User


def capture(model):
    cap = cv2.VideoCapture(0)

    previous = time()
    delta = 0

    while cap.isOpened():
        current = time()
        delta = current - previous

        if delta > 2:
            status, frame = cap.read()

            if not status:
                break

            # Inference
            pred = model(frame)
            # xmin,ymin,xmax,ymax
            df = pred.pandas().xyxy[0]
            # Filter by confidence
            df = df[df["confidence"] > 0.5]

            for i in range(df.shape[0]):
                bbox = df.iloc[i][["xmin", "ymin", "xmax", "ymax"]].values.astype(int)

                # print bboxes: frame -> (xmin, ymin), (xmax, ymax)
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)
                # print text
                cv2.putText(frame,
                            f"{df.iloc[i]['name']}: {round(df.iloc[i]['confidence'], 4)}",
                            (bbox[0], bbox[1] - 15),
                            cv2.FONT_HERSHEY_PLAIN,
                            1,
                            (255, 255, 255),
                            2)

            cv2.imshow("frame", frame)

            previous = current

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()


if __name__ == '__main__':
    user = User()
    user.weights_directory = 'runs/train/exp3/weights/best.pt'
    # I think that the following loads the local model without needing Internet connection
    myModel = torch.hub.load('.', 'custom', path='runs/train/exp3/weights/best.pt', source='local')
    capture(myModel)
