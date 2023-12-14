# Import libraries
import os
import sys
from pathlib import Path

import fiftyone as fo
import fiftyone.zoo as foz
from fiftyone import ViewField as F

import shutil

# Get yolov5 root directory
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative


def download_dataset(classes_selected: list):
    # Load dataset in Fiftyone format
    name = "open-images-v7"
    splits = ["train", "validation"]
    label_types = ["detections"]
    classes = classes_selected  # classes_selected=["Tin can", "Apple", "Pear"]
    FiftyoneDataset_dir = str(ROOT / "datasets/FiftyoneDataset")  # "D:\projects\TFG\yolov5\datasets\FiftyoneDataset"
    max_samples = len(classes_selected)*10  # change to *200 or more after testing

    dataset = foz.load_zoo_dataset(
        name,
        dataset_dir=FiftyoneDataset_dir,
        splits=splits,
        label_types=label_types,
        classes=classes,
        shuffle=True,
        max_samples=max_samples,
    )

    # Export dataset in Fiftyone format to YOLOv5 format
    view = dataset.filter_labels("ground_truth", F("label").is_in(classes))
    export_dir = str(ROOT / "datasets/YOLOv5Dataset_1")  # "D:\projects\TFG\yolov5\datasets\YOLOv5Dataset_1" || ROOT / 'datasets/YOLOv5Dataset_1'
    label_field = "ground_truth"

    for split in splits:
        split_view = view.match_tags(split)
        if split == "validation":
            split = "val"
        split_view.export(
            export_dir=export_dir,
            dataset_type=fo.types.YOLOv5Dataset,
            label_field=label_field,
            split=split,
            classes=classes,
        )

    # Remove the dataset in Fiftyone format, we don't need it, we only need dataset in YOLOv5 format
    shutil.rmtree(FiftyoneDataset_dir)


if __name__ == '__main__':
    classes_selected = ["Tin can", "Apple", "Pear"]
    download_dataset(classes_selected)
