# Import libraries
import os
import sys
from pathlib import Path
import torch.cuda

# Import files
import detect
import train
import dataset


class User:
    def __init__(self):
        self.cuda_available = torch.cuda.is_available()
        self.root_path = self.set_root_path()
        self.dataset_directory = None
        self.weights_directory = None

    def set_root_path(self):
        FILE = Path(__file__).resolve()
        ROOT = FILE.parents[0]  # YOLOv5 root directory
        if str(ROOT) not in sys.path:
            sys.path.append(str(ROOT))  # add ROOT to PATH
        ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative
        return ROOT

    # Downloading dataset function
    def downloading_dataset(self, classes_selected: list):
        self.dataset_directory = dataset.download_dataset(classes_selected)

    # Training model with a dataset
    def training(self):
        train.run(
            weights='yolov5m.pt',
            data=self.root_path / self.dataset_directory,
            epochs=5,
            batch_size=16,
            imgsz=640,
        )

        trained_path = Path(user.root_path / 'runs/train')
        exp_number = ''
        for file in trained_path.glob('*'):
            exp_number = file.name

        self.weights_directory = 'runs/train/'+exp_number+'/weights/best.pt'

    # Detection function
    def detection(self, classes_selected=None):
        detect.run(
            weights=self.root_path / self.weights_directory,  # weights_selected='yolov5s.pt'
            source=self.root_path / '0',  # 0-->webcam
            classes=classes_selected,
            # classes_selected=[0, 5] --> 0: person | 5:bus (see coco128.yaml) ||| classes_selected=None --> detect all classes
            vid_stride=1,
            # In which fotogram the inference is done. If we have 30 fps and vid_stride=30, it will do the inference in the fps number 30, so it will do one inference per second. PROBLEM: to be able to set the number of inferences per second we must know the fps of the video input.
        )


if __name__ == '__main__':
    user = User()
    user.downloading_dataset(classes_selected=["Spoon", "Fork", "Kitchen knife"])
    user.training()
    user.detection()
