import os
import sys
from pathlib import Path

import detect

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

detect.run(
    weights=ROOT / 'yolov5s.pt',
    source=ROOT / '0',
    classes=[0, 5], # 0: person | 5:bus (see coco128.yaml)
)