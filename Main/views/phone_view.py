from datetime import timedelta

from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from flask import request, jsonify, current_app

from Main import redis_conn, client, SIGN_NAME, TEMPLATE_CODE
from Main.utils.commons import generate_verification_code
from Main.utils.response_code import RET
from . import index


def send_sms(phone_number, code):
    send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
        phone_numbers=phone_number,
        sign_name=SIGN_NAME,
        template_code=TEMPLATE_CODE,
        template_param=f'{{"code":"{code}"}}'
    )
    try:
        response = client.send_sms(send_sms_request)
        if response.body.code == 'OK':
            return True
        else:
            current_app.logger.error(f"Failed to send SMS: {response.body.message}")
            return False
    except Exception as e:
        current_app.logger.error(f"Failed to send SMS: {str(e)}")
        return False


@index.route('/send_phone_code', methods=['POST'])
def send_phone_code():
    phone_number = request.json.get('phone')
    if not phone_number:
        current_app.logger.error('Phone number is required')
        return jsonify(re_code=RET.NODATA, msg='Phone number is required')

    code = generate_verification_code()
    redis_conn.setex(f'verification_code:{phone_number}', timedelta(minutes=5), code)

    if send_sms(phone_number, code):
        return jsonify(re_code=RET.OK, msg='Verification code sent successfully')
    else:
        current_app.logger.error('Failed to send verification code')
        return jsonify(re_code=RET.REGISTERERR, msg='Failed to send verification code')


@index.route('/verify_phone_code', methods=['POST'])
def verify_phone_code():
    user_code = request.json.get('code')
    phone_number = request.json.get('phone')

    stored_code = redis_conn.get(f'verification_code:{phone_number}')
    if not stored_code:
        current_app.logger.error('Verification code expired or not sent')
        return jsonify(re_code=RET.NODATA, msg='Verification code expired or not sent')

    if stored_code.decode('utf-8') != user_code:
        current_app.logger.error('Invalid verification code')
        return jsonify(re_code=RET.REGISTERERR, msg='Invalid verification code')

    redis_conn.delete(f'verification_code:{phone_number}')
    return jsonify(re_code=RET.OK, msg='Verification successful')
