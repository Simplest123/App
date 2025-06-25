from typing import List, Tuple, Union

import numpy as np
from numpy import ndarray


def softmax(x: ndarray, axis: int = -1) -> ndarray:
    e_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
    y = e_x / e_x.sum(axis=axis, keepdims=True)
    return y


def sigmoid(x: ndarray) -> ndarray:
    return 1. / (1. + np.exp(-x))


class Decoder:
    def __init__(self, model_only: bool = True):
        self.model_only = model_only
        self.boxes_pro = []
        self.scores_pro = []
        self.labels_pro = []
        self.is_logging = False

    def __call__(self,
                 feats: Union[List, Tuple],
                 conf_thres: float,
                 num_labels: int = 20,
                 **kwargs) -> Tuple:
        self.boxes_pro.clear()
        self.scores_pro.clear()
        self.labels_pro.clear()

        if self.model_only:
            # transpose channel to last dim for easy decoding
            feats = [
                np.ascontiguousarray(feat[0].transpose(1, 2, 0))
                for feat in feats
            ]
        else:
            # ax620a horizonX3 transpose channel to last dim by default
            feats = [np.ascontiguousarray(feat) for feat in feats]

        self.__decoding(feats, conf_thres, num_labels, **kwargs)
        return self.boxes_pro, self.scores_pro, self.labels_pro

    def __decoding(self,
                   feats: List[ndarray],
                   conf_thres: float,
                   num_labels: int = 20,
                   **kwargs):
        reg_max: int = kwargs.get('reg_max', 16)
        dfl = np.arange(0, reg_max, dtype=np.float32)
        for i, feat in enumerate(feats):
            stride = 8 << i
            score_feat, box_feat = np.split(feat, [
                num_labels,
            ], -1)
            score_feat = sigmoid(score_feat)
            _argmax = score_feat.argmax(-1)
            _max = score_feat.max(-1)
            indices = np.where(_max > conf_thres)
            hIdx, wIdx = indices
            num_proposal = hIdx.size
            if not num_proposal:
                continue

            scores = _max[hIdx, wIdx]
            boxes = box_feat[hIdx, wIdx].reshape(num_proposal, 4, reg_max)
            boxes = softmax(boxes, -1) @ dfl
            labels = _argmax[hIdx, wIdx]

            for k in range(num_proposal):
                score = scores[k]
                label = labels[k]

                x0, y0, x1, y1 = boxes[k]

                x0 = (wIdx[k] + 0.5 - x0) * stride
                y0 = (hIdx[k] + 0.5 - y0) * stride
                x1 = (wIdx[k] + 0.5 + x1) * stride
                y1 = (hIdx[k] + 0.5 + y1) * stride

                w = x1 - x0
                h = y1 - y0

                self.scores_pro.append(float(score))
                self.boxes_pro.append(
                    np.array([x0, y0, w, h], dtype=np.float32))
                self.labels_pro.append(int(label))
