import os
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models

from Main.utils.commons import generate_verification_code

ALIBABA_CLOUD_ACCESS_KEY_ID = ''
ALIBABA_CLOUD_ACCESS_KEY_SECRET = ''
SIGN_NAME = ''
TEMPLATE_CODE = ''

send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
    phone_numbers='18673326973',
    sign_name=SIGN_NAME,
    template_code=TEMPLATE_CODE,
    template_param=f'{{"code":"{generate_verification_code()}"}}'
)
client = Dysmsapi20170525Client(open_api_models.Config(  # Phone
    access_key_id=ALIBABA_CLOUD_ACCESS_KEY_ID,
    access_key_secret=ALIBABA_CLOUD_ACCESS_KEY_SECRET
))

try:
    response = client.send_sms(send_sms_request)
    if response.body.code == 'OK':
        print(True)
    else:
        print(False)
except Exception as e:
    print(False)
