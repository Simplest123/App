import re
from datetime import datetime
import os
import json
import urllib.parse
import urllib.request
import ssl

import cv2
import numpy as np
from flask import session, jsonify, request, current_app, g

from . import index
from Main.utils.commons import login_required
from Main.utils.oss_utils import upload_file2oss
from Main.utils.response_code import RET
from Main.database import User, Action
from .. import db


@index.route('/user/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    phone = data.get('phone')
    email_code = data.get('emailCode')
    phone_code = data.get('phoneCode')
    password = data.get('password')
    confirm_password = data.get('confirm')

    if not all([username, email, phone, email_code, phone_code, password, confirm_password]):
        current_app.logger.error('Missing required parameters')
        jsonify(re_code=RET.PARAMERR, msg='缺失注册必要信息')
    if password != confirm_password:
        current_app.logger.error('Password is required to match the confirmed password')
        jsonify(re_code=RET.DATAERR, msg='两次密码不一致')

    if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9]+$', username):
        current_app.logger.error('Only numbers, letters, and Chinese characteristics are allowed')
        jsonify(re_code=RET.DATAERR, msg='用户名仅支持数字、字母和中文')
    if not re.match(r'^[a-zA-Z0-9~!?;@#]+$', password):
        current_app.logger.error('Only numbers, letters, and a fraction of special symbols (~!?;@#) are allowed')
        jsonify(re_code=RET.DATAERR, msg='密码仅支持数字、字母和部分特殊字符(~!?;@#)')
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        current_app.logger.error('Right email format is required')
        jsonify(re_code=RET.DATAERR, msg='请输入正确的邮箱')

    new_user = User(
        username=username,
        email=email,
        phone=phone,
        password_hash=password,
        created_at=datetime.utcnow()
    )
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Register failed: {e}")
        return jsonify(re_code=RET.REGISTERERR, msg=f"注册失败")

    return jsonify(re_code=RET.OK, msg='注册成功', user=new_user.to_dict())


@index.route('/user/login', methods=['POST'])
def login():
    """
    User login
    Frontend: phone + password / email + password
    """
    json_dict = request.json
    phone = json_dict.get('phone')
    email = json_dict.get('email')
    password = json_dict.get('password')
    user = None

    # Parameter validation
    if not password or (not phone and not email):
        current_app.logger.error('Missing required parameters')
        return jsonify(re_code=RET.PARAMERR, msg='请输入登录所需信息')

    try:
        if phone:
            user = User.query.filter(User.phone == phone).first()
        elif email:
            user = User.query.filter(User.email == email).first()
    except Exception as e:
        current_app.logger.error(f"Database query failed: {e}")
        return jsonify(re_code=RET.DBERR, msg='未登录用户，请先注册')

    if not user:
        current_app.logger.error('User not registered')
        return jsonify(re_code=RET.NODATA, msg='未登录用户，请先注册')

    if not user.check_password(password):
        current_app.logger.error('Incorrect password')
        return jsonify(re_code=RET.PARAMERR, msg='请输入正确的密码')

    action = Action(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        type='login',
        description=f'登录',
    )
    user.actions.append(action)
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.debug(e)
        db.session.rollback()
        return jsonify(re_code=RET.DBERR, msg='信息记录失败')

    session['user_id'] = user.user_id
    session['username'] = user.username
    if user.email:
        session['email'] = user.email
    if user.phone:
        session['phone'] = user.phone

    return jsonify(re_code=RET.OK, msg='登录成功', user=user.to_dict())


@index.route('/user/unsubscribe', methods=['DELETE'])
@login_required
def unsubscribe():
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify(re_code=RET.NODATA, msg='User does not exist')
        db.session.delete(user)
        db.session.commit()
        session.clear()
        return jsonify(re_code=RET.OK, msg='Account unsubscribed successfully')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Account unsubscribe failed: {e}")
        return jsonify(re_code=RET.DBERR, msg='Account unsubscribe failed')


@index.route('/sessions', methods=['DELETE'])
def logout():
    """
    :return: Frontend Index
    """
    try:
        csrf_token = session.get('csrf_token')
        session.clear()
        session['csrf_token'] = csrf_token
        return jsonify(re_code=RET.OK, msg='退出成功')
    except Exception as e:
        current_app.logger.error(f"Logout failed: {e}")
        return jsonify(re_code=RET.DBERR, msg='退出失败')


@index.route('/user', methods=['GET'])
@login_required
def get_user_info():
    """
    Get user information
    Requires authentication (login_required decorator)
    """
    user_id = g.user_id

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(f"Database query failed: {e}")
        return jsonify(re_code=RET.DBERR, msg='Database query failed')

    if not user:
        return jsonify(re_code=RET.NODATA, msg='User does not exist')

    user_info = user.to_dict()
    return jsonify(re_code=RET.OK, msg='Query successful', user=user_info)


@index.route('/user/action', methods=['GET'])
@login_required
def get_user_action_info():
    user_id = g.user_id

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(f"Database query failed: {e}")
        return jsonify(re_code=RET.DBERR, msg='Database query failed')

    if not user:
        return jsonify(re_code=RET.NODATA, msg='User does not exist')

    sorted_actions = sorted(user.actions, key=lambda action: action.timestamp, reverse=True)
    actions = {i: action.to_dict() for i, action in enumerate(sorted_actions)}

    return jsonify(re_code=RET.OK, msg='Query successful', actions=actions)


@index.route('/user', methods=['PUT'])
@login_required
def update_user_info():
    json_dict = request.json
    user_id = g.user_id
    username = json_dict.get('username')
    gender = json_dict.get('gender')
    career = json_dict.get('career')
    birth_day = json_dict.get('birth_day')

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(f"查询用户失败: {e}")
        return jsonify(re_code=RET.DBERR, msg='查询用户失败')
    if not user:
        return jsonify(re_code=RET.NODATA, msg='用户不存在')

    need_update = False
    update_fields = {}
    if username != user.username:
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9]+$', username):
            return jsonify(re_code=RET.PARAMERR, msg='用户名不支持特殊字符')
        update_fields['username'] = username
        need_update = True
    if gender is not None and gender != user.gender:
        update_fields['gender'] = gender
        need_update = True

    if career is not None and career != user.career:
        update_fields['career'] = career
        need_update = True

    if birth_day is not None and birth_day != user.birth_day:
        update_fields['birth_day'] = birth_day
        need_update = True

    if not need_update:
        return jsonify(re_code=RET.OK, msg='数据未变化，无需更新')

    try:
        for field, value in update_fields.items():
            setattr(user, field, value)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新失败: {e}")
        return jsonify(re_code=RET.DBERR, msg='更新失败')

    if 'username' in update_fields:
        session['username'] = username

    action = Action(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        type='update',
        description=f'修改基本信息',
    )
    user.actions.append(action)
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.debug(e)
        db.session.rollback()
        return jsonify(re_code=RET.DBERR, msg='记录失败')

    return jsonify(
        re_code=RET.OK,
        msg='更新成功',
    )


@index.route('/user/pwd', methods=['PUT'])
@login_required
def update_user_pwd():
    json_dict = request.json
    user_id = g.user_id
    password = json_dict.get('password')
    old_password = json_dict.get('old_password')

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(f"查询用户失败 - 用户ID: {user_id}, 错误: {e}")
        return jsonify(re_code=RET.DBERR, msg='查询用户失败')

    if not user:
        return jsonify(re_code=RET.NODATA, msg='用户不存在')

    if not user.check_password(old_password):
        return jsonify(re_code=RET.PARAMERR, msg='原密码输入错误')

    if user.check_password(password):
        return jsonify(re_code=RET.OK, msg='密码未变化，无需更新')

    if not re.match(r'^[a-zA-Z0-9~!?;@#]+$', password):
        current_app.logger.error('Only numbers, letters, and a fraction of special symbols (~!?;@#) are allowed')
        jsonify(re_code=RET.DATAERR, msg='密码仅支持数字、字母和部分特殊字符(~!?;@#)')

    try:
        user.password_hash = password

        action = Action(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            type='update',
            description=f'修改密码',
        )
        user.actions.append(action)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"密码更新失败 - 用户ID: {user_id}, 错误: {e}")
        return jsonify(re_code=RET.DBERR, msg='更新失败')

    return jsonify(
        re_code=RET.OK,
        msg='密码更新成功',
    )


@index.route('/user/avatar', methods=['PUT'])
@login_required
def update_user_avatar():
    avatar = request.files.get('avatar')
    avatar_name = os.path.basename(avatar.filename)
    user_id = g.user_id

    if not avatar:
        current_app.logger.error('update avatar: empty file')
        return jsonify(re_code=RET.PARAMERR, msg='空头像')
    if avatar_name.split('.')[1] not in ['png', 'jpg', 'jpeg', 'bmp', 'ico']:
        current_app.logger.error('update avatar: wrong format')
        return jsonify(re_code=RET.PARAMERR, msg='请使用恰当的头像格式')

    img = cv2.imdecode(np.asarray(bytearray(avatar.stream.read()), dtype=np.uint8), cv2.IMREAD_COLOR)
    avatar_url = upload_file2oss(img, avatar_name, 'image', task='upload')
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.debug(e)
        return jsonify(re_code=RET.DBERR, msg='Query failed')

    if not user:
        current_app.logger.error('update avatar: User does not exist')
        return jsonify(re_code=RET.NODATA, msg='User does not exist')
    if not avatar_url:
        current_app.logger.error('update avatar: oss upload failed')
        return jsonify(re_code=RET.PARAMERR, msg='update avatar: oss upload failed')

    user.avatar = avatar_url
    action = Action(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        type='update',
        description=f'修改头像',
    )
    user.actions.append(action)
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.debug(e)
        db.session.rollback()
        return jsonify(re_code=RET.DBERR, msg='头像更新失败')
    avatar = user.avatar
    return jsonify(re_code=RET.OK, msg='头像更新成功', avatar=avatar)


@index.route('/user/auth')
@login_required
def get_user_auth():
    pass


@index.route('/user/auth', methods=['POST'])
@login_required
def set_user_auth():
    json_dict = request.json
    real_name = json_dict.get('real_name')
    id_card = json_dict.get('id_card')

    if not all([real_name, id_card]):
        current_app.logger.error('Failed')
        return jsonify(re_code=RET.NODATA, msg='缺失真实姓名或身份证号码')

    url = 'https://idenauthen.market.alicloudapi.com/idenAuthentication'
    appcode = '59d70c4fe95f4a9daaf7ba20635f2348'
    bodys = {}
    bodys['idNo'] = f'''{real_name}'''
    bodys['name'] = f'''{id_card}'''
    post_data = urllib.parse.urlencode(bodys).encode('utf-8')

    urllib_request = urllib.request.Request(url, data=post_data)
    urllib_request.add_header('Authorization', 'APPCODE ' + appcode)
    urllib_request.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        response = urllib.request.urlopen(urllib_request, context=ctx)
        content = response.read().decode('utf-8')
    except urllib.error.URLError as e:
        current_app.logger.error('Failed')
        return jsonify(re_code=RET.PARAMERR, msg='认证失败')

    try:
        user = User.query.get(g.user_id)
    except Exception as e:
        current_app.logger.debug(e)
        return jsonify(re_code=RET.DBERR, msg='Query failed')
    if not user:
        current_app.logger.error('update avatar: User does not exist')
        return jsonify(re_code=RET.NODATA, msg='User does not exist')

    data = json.loads(content)
    user.real_name = real_name
    user.id_card = id_card

    action = Action(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        type='update',
        description=f'实名认证',
    )
    user.actions.append(action)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.debug(e)
        db.session.rollback()
        return jsonify(re_code=RET.DBERR, msg='update real_name failed')
    return jsonify(re_code=RET.OK, msg=data.get('respMessage'), real_name=real_name)


@index.route('/sessions', methods=['GET'])
def check_login():
    user_id = session.get('user_id')
    username = session.get('username')
    return jsonify(re_code=RET.OK, msg='OK', user={'user_id': user_id, 'username': username})
