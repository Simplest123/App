from typing import List, Tuple, Union

import cv2
import numpy as np
from numpy import ndarray


class Preprocess:

    def __init__(self):
        self.mean = np.array([0, 0, 0], dtype=np.float32).reshape((3, 1, 1))
        self.std = np.array([255, 255, 255], dtype=np.float32).reshape((3, 1, 1))
        self.is_rgb = True

    def __call__(self,
                 image: ndarray,
                 new_size: Union[List[int], Tuple[int]] = (512, 512),
                 **kwargs) -> Tuple[ndarray, Tuple[float, float]]:
        # new_size: (height, width)
        height, width = image.shape[:2]
        ratio_h, ratio_w = new_size[0] / height, new_size[1] / width
        image = cv2.resize(
            image, (0, 0),
            fx=ratio_w,
            fy=ratio_h,
            interpolation=cv2.INTER_LINEAR)
        image = np.ascontiguousarray(image.transpose(2, 0, 1))
        image = image.astype(np.float32)
        image -= self.mean
        image /= self.std
        return image[np.newaxis], (ratio_w, ratio_h)
