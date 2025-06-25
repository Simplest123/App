import cv2
import numpy as np


def postprocess(self, input_image, output):
    outputs = np.transpose(np.squeeze(output[0]))
    rows = outputs.shape[0]
    boxes = []
    scores = []
    class_ids = []
    x_factor = self.img_width / self.input_width
    y_factor = self.img_height / self.input_height

    for i in range(rows):
        classes_scores = outputs[i][4:]
        max_score = np.amax(classes_scores)

        if max_score >= self.confidence_thres:
            class_id = np.argmax(classes_scores)
            x, y, w, h = outputs[i][0], outputs[i][1], outputs[i][2], outputs[i][3]
            left = int((x - w / 2) * x_factor)
            top = int((y - h / 2) * y_factor)
            width = int(w * x_factor)
            height = int(h * y_factor)
            class_ids.append(class_id)
            scores.append(max_score)
            boxes.append([left, top, width, height])

    # 应用非极大抑制以过滤重叠的边界框
    indices = cv2.dnn.NMSBoxes(boxes, scores, self.confidence_thres, self.iou_thres)

    # 遍历非极大抑制后选择的索引
    for i in indices:
        # 获取与索引对应的边界框、得分和类别ID
        box = boxes[i]
        score = scores[i]
        class_id = class_ids[i]
        # 在输入图像上绘制检测结果
        self.draw_detections(input_image, box, score, class_id)
    # 返回修改后的输入图像
    return input_image
