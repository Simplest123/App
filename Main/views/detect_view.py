import json
import uuid
from datetime import datetime

import cv2
import numpy as np
from flask import current_app, request, jsonify, g
from Main.utils.response_code import RET
from Main.utils.commons import login_required
from Main.database import User, Project, DetectionData, Action
from .. import db
from . import index

from Main.utils.detection.predictor import Predictor
from Main.utils.oss_utils import upload_file2oss


@index.route('/detect/image', methods=['POST'])
@login_required
def detect_image():
    try:
        img = request.files.get('image')
        img_name = img.filename
        score_thr = float(request.form.get('conf_threshold'))
        is_show_conf = request.form.get('show_confidence').lower() == 'true'
        is_show_class = request.form.get('show_class').lower() == "true"
        model_type = request.form.get('scenario')
        model_scale = request.form.get('model_scale')
        project_name = request.form.get('project_name')
        # lightweight = request.form['lightweight']
        valid_cls = json.loads(request.form.get('target_type'))
    except Exception as e:
        current_app.logger.error('Missing required parameters')
        return jsonify(re_code=RET.PARAMERR, msg='Missing required parameters')

    # try:
    img = cv2.imdecode(np.asarray(bytearray(img.stream.read()), dtype=np.uint8), cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if project_name:
        ori_url = upload_file2oss(file=img, name=img_name, file_type='image')

    detected_img, result = Predictor(img=img, valid_cls=valid_cls, scale=model_scale,
                                     is_show_conf=is_show_conf, is_show_class=is_show_class,
                                     model_type=model_type, score_thr=score_thr)()

    detected_url = upload_file2oss(file=detected_img, name=img_name, file_type='image')
    result['url'] = detected_url
    if project_name:
        user_id = g.user_id
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(re_code=RET.DBERR, msg='Query failed')
        if not user:
            current_app.logger.error('User does not exist')
            return jsonify(re_code=RET.NODATA, msg='User does not exist')

        project = Project(
            project_name=f"{project_name}",
            scenario=model_type,
            scale=model_scale,
            created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            detection_classes=valid_cls,
            conf_threshold=score_thr,
            source_path=ori_url,
            result_path=detected_url
        )
        data = DetectionData(
            results=result
        )
        action = Action(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            type='detect',
            description=f'场景{model_type}中通过大小为{model_scale}的模型进行目标检测任务',
        )
        project.data.append(data)
        user.projects.append(project)
        user.actions.append(action)
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.debug(e)
            db.session.rollback()

    return jsonify(re_code=RET.OK, msg='Detect Successfully', detectedResult=result)
    # except Exception as e:
    #     current_app.logger.error('Detection Failed')
    #     return jsonify(re_code=RET.PARAMERR, msg='Detection Failed')


@index.route('/detect/video', methods=['POST'])
def detect_video():
    pass


@index.route('/detect/save', methods=['POST'])
def detect_save():
    project_name = request.form.get('project_name')
    ori_url = request.form.get('ori_url')
    detected_url = request.form.get('detected_url')
    result = request.form.get('result')
    score_thr = float(request.form.get('conf_threshold'))
    model_type = request.form.get('scenario')
    model_scale = request.form.get('model_scale')
    # lightweight = request.form['lightweight']
    valid_cls = json.loads(request.form.get('target_type'))

    try:
        user = User.query.get(g.user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(re_code=RET.DBERR, msg='Query failed')
    if not user:
        current_app.logger.error('User does not exist')
        return jsonify(re_code=RET.NODATA, msg='User does not exist')

    project = Project(
        project_name=f"{project_name}",
        scenario=model_type,
        scale=model_scale,
        created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        detection_classes=valid_cls,
        conf_threshold=score_thr,
        source_path=ori_url,
        result_path=detected_url
    )
    data = DetectionData(
        results=result
    )
    action = Action(
        details={
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'model_type': model_type,
            'scale': model_scale,
        }
    )
    project.data.append(data)
    user.projects.append(project)
    user.actions.append(action)
    try:
        db.session.commit()
        return jsonify(re_code=RET.OK, msg='Saving successfully')
    except Exception as e:
        current_app.logger.debug(e)
        db.session.rollback()
        current_app.logger.error('Saving Failed')
        return jsonify(re_code=RET.PARAMERR, msg='Saving Failed')
