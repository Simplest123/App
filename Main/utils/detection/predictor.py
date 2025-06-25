import math
import sys
import time
from pathlib import Path
from tqdm import tqdm
from typing import List

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import cv2
import onnxruntime
from Main.utils.detection.det_cfg import MODEL_CFG
from Main.utils.detection.nms import non_max_suppression
from Main.utils.detection.decoder import Decoder
from Main.utils.detection.preprocess import Preprocess

sys.path.append(str(Path(__file__).resolve().parents[0]))
IMG_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.ppm', '.bmp', '.pgm', '.tif',
                  '.tiff', '.webp')


def path_to_list(path: str):
    path = Path(path)
    if path.is_file() and path.suffix in IMG_EXTENSIONS:
        res_list = [str(path.absolute())]
    elif path.is_dir():
        res_list = [
            str(p.absolute()) for p in path.iterdir()
            if p.suffix in IMG_EXTENSIONS
        ]
    else:
        raise RuntimeError
    return res_list


class Predictor:
    def __init__(self, img, valid_cls: List[str] = [],
                 is_show_conf: bool = True,
                 is_show_class: bool = True,
                 model_type: str = 'multiscale', scale: str = 'S',
                 score_thr: float = 0.3, iou_thr: float = 0.60):
        self.img = img
        self.model_type = model_type
        self.scale = scale
        self.score_thr = score_thr
        self.iou_thr = iou_thr
        self.valid_cls = valid_cls
        self.is_show_conf = is_show_conf
        self.is_show_class = is_show_class

    def __call__(self):
        session = onnxruntime.InferenceSession(
            MODEL_CFG.get(self.model_type).get(self.scale),
            providers=['CPUExecutionProvider'],
        )
        preprocessor = Preprocess()
        decoder = Decoder()
        CLASS_NAMES = MODEL_CFG.get(self.model_type).get('CLASS_NAMES')
        CLASS_COLORS = MODEL_CFG.get(self.model_type).get('CLASS_COLORS')

        image = self.img
        if isinstance(image, str):
            image = cv2.imread(image)
        image_h, image_w = image.shape[:2]
        img, (ratio_w, ratio_h) = preprocessor(image, MODEL_CFG.get(self.model_type).get('input_size'))
        start_time = time.time()
        features = session.run(None, {'images': img})
        end_time = time.time()
        decoder_outputs = decoder(
            features,
            self.score_thr,
            num_labels=len(CLASS_NAMES)
        )
        objects = []
        nms_boxes, nms_scores, nms_labels = non_max_suppression(
            *decoder_outputs, conf_thres=self.score_thr, iou_thres=self.iou_thr)
        for box, score, label in zip(nms_boxes, nms_scores, nms_labels):
            if CLASS_NAMES[label] not in self.valid_cls:
                continue
            x0, y0, x1, y1 = box
            x0 = math.floor(min(max(x0 / ratio_w, 1), image_w - 1))
            y0 = math.floor(min(max(y0 / ratio_h, 1), image_h - 1))
            x1 = math.ceil(min(max(x1 / ratio_w, 1), image_w - 1))
            y1 = math.ceil(min(max(y1 / ratio_h, 1), image_h - 1))
            cv2.rectangle(image, (x0, y0), (x1, y1), CLASS_COLORS[label], 2)
            objects.append({
                'coordinates': [x0, y0, x1, y1],
                'cls': CLASS_NAMES[label],
                'conf': score
            })

            if self.is_show_conf and self.is_show_class:
                text = f'{CLASS_NAMES[label]}: {score:.3f}'
            elif self.is_show_conf and not self.is_show_class:
                text = f'{score:.3f}'
            elif not self.is_show_conf and self.is_show_class:
                text = f'{CLASS_NAMES[label]}'
            else:
                text = ''
            if text != '':
                (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                background_x0 = x0 - 1
                background_y0 = y0 - text_height - 7
                background_x1 = x0 + text_width
                background_y1 = y0
                cv2.rectangle(image, (background_x0, background_y0), (background_x1, background_y1),
                              CLASS_COLORS[label], -1)

                image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                try:
                    font = ImageFont.truetype("times.ttf", 20)
                except IOError:
                    font = ImageFont.load_default()
                draw = ImageDraw.Draw(image_pil)

                draw.text((background_x0, background_y0 - 2), text, font=font, fill=(255, 255, 255))
                image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

        # image = cv2.resize(image, (image_h, image_w), interpolation=cv2.INTER_LINEAR)
        inference_time = end_time - start_time
        # cv2.imshow('result', image)
        # cv2.waitKey(0)

        return image, {
            'objects': objects,
            'consumption_time': inference_time,
            'ob_counts': len(objects)
        }


if __name__ == '__main__':
    predictor = Predictor(
        img='C:\\Users\\86182\\Desktop\\02736.jpg',
        valid_cls=['ship'],
        scale='S',
        is_show_conf=True,
        is_show_class=True,
        model_type='multiscale'
    )
    print(predictor()[2])
