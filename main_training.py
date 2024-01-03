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
        self.cuda_available = None
        self.root_path = None
        self.dataset_directory = None
        self.weights_directory = None

    def initial_settings(self):
        FILE = Path(__file__).resolve()
        ROOT = FILE.parents[0]  # YOLOv5 root directory
        if str(ROOT) not in sys.path:
            sys.path.append(str(ROOT))  # add ROOT to PATH
        ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

        self.root_path = ROOT
        self.cuda_available = torch.cuda.is_available()
        print("CUDA available: ", self.cuda_available)

    # Downloading dataset function
    def downloading_dataset(self, classes_selected: list, images_per_class=200):
        print("\nStarting download!\n")

        self.dataset_directory = dataset.download_dataset(classes_selected, images_per_class=images_per_class)

        print("\nDataset downloaded!\n")

    # Training model with a dataset
    def training(self, epochs=100, batch_size=16, imgsz=640, weights='yolov5s.pt'):
        print("\nStarting training!\n")

        train.run(
            weights=weights,
            data=self.root_path / self.dataset_directory,
            epochs=epochs,
            batch_size=batch_size,
            imgsz=imgsz,
        )

        trained_path = Path(self.root_path / 'runs/train')
        exp_number = ''
        for file in trained_path.glob('*'):
            exp_number = file.name

        self.weights_directory = 'runs/train/'+exp_number+'/weights/best.pt'

        print("\nModel trained!\n")

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
    user.initial_settings()
    user.downloading_dataset(classes_selected=["Car", "Jellyfish"], images_per_class=20)
    user.training(epochs=5)
