# Import libraries
import os
import sys
from pathlib import Path

# Import files
import detect
import train
import dataset

# Get yolov5 root directory
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative


# Downloading dataset function
def downloading_dataset(classes_selected: list):
    dataset.download_dataset(classes_selected)


# Training model with a dataset
def training():
    pass # TODO


# Detection function
def detection(weights_selected: str, classes_selected: list):
    detect.run(
        weights=ROOT / weights_selected, # weights_selected='yolov5s.pt'
        source=ROOT / '0',
        classes=classes_selected, # classes_selected=[0, 5] || 0: person | 5:bus (see coco128.yaml)
    )


if __name__ == '__main__':
    classes_selected = ["Tin can", "Apple", "Pear"]
    downloading_dataset(classes_selected)
