import uuid
import cv2
import numpy as np
from flask import current_app

from Main import bucket


def upload_file2oss(file, name, file_type='image', task='detect'):
    """
    file: image / video
    """
    if file_type not in ['image', 'video']:
        current_app.logger.error("wrong file format")
        return None

    if task == 'detect':
        file = cv2.cvtColor(file, cv2.COLOR_BGR2RGB)
    success, encoded_image = cv2.imencode('.jpg', file, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
    if not success:
        raise ValueError("Failed to encode image")
    image_bytes = encoded_image.tobytes()
    filename = f"{file_type}s/{uuid.uuid4().hex}-{name}"
    try:
        bucket.put_object(filename, image_bytes)
        return filename
    except Exception as e:
        current_app.logger.error(f"OSS upload failed: {e}")
        return None
