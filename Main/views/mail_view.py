import re
from datetime import timedelta

from flask import current_app, request, jsonify
from flask_mail import Message

from Main import mail, redis_conn
from Main.utils.commons import generate_verification_code
from Main.utils.response_code import RET
from . import index


@index.route('/send_email_code', methods=['POST'])
def send_email_code():
    email = request.json.get('email')
    if not email:
        current_app.logger.error('Email is required')
        return jsonify(re_code=RET.NODATA, msg='Email is required')

    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        current_app.logger.error('Invalid email format')
        return jsonify(re_code=RET.DATAERR, msg='Invalid email format')

    code = generate_verification_code()
    try:
        redis_conn.setex(f'verification_code:{email}', timedelta(minutes=5), code)
    except Exception as e:
        current_app.logger.error(f'Failed to store verification code in Redis: {str(e)}')
        return jsonify(re_code=RET.DBERR, msg='Failed to store verification code')

    try:
        msg = Message(
            subject='Your Verification Code',
            sender='1941227494@qq.com',
            recipients=[email],
            body=f'Your verification code is: {code}',
            charset='utf-8'
        )
        with mail.connect() as connection:
            connection.send(msg)
        current_app.logger.info(f'Verification code sent to {email}')
        return jsonify(re_code=RET.OK, msg='Verification code sent successfully')
    except Exception as e:
        current_app.logger.error(f'Failed to send email: {str(e)}')
        return jsonify(re_code=RET.REGISTERERR, msg=f'Failed to send email: {str(e)}')


@index.route('/verify_email_code', methods=['POST'])
def verify_email_code():
    user_code = request.json.get('code')
    email = request.json.get('email')
    if not user_code or not email:
        current_app.logger.error('Code and email are required')
        return jsonify(re_code=RET.PARAMERR, msg='Code and email are required')

    try:
        stored_code = redis_conn.get(f'verification_code:{email}')
        if not stored_code:
            current_app.logger.error('Verification code expired or not sent')
            return jsonify(re_code=RET.NODATA, msg='Verification code expired or not sent')

        if stored_code.decode('utf-8') != user_code:
            current_app.logger.error('Invalid verification code')
            return jsonify(re_code=RET.DATAERR, msg='Invalid verification code')

        redis_conn.delete(f'verification_code:{email}')
        current_app.logger.info(f'Verification successful for {email}')
        return jsonify(re_code=RET.OK, msg='Verification successful')
    except Exception as e:
        current_app.logger.error(f'Failed to verify code: {str(e)}')
        return jsonify(re_code=RET.DBERR, msg=f'Failed to verify code: {str(e)}')
