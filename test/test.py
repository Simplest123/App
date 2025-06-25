# coding: utf-8
import uuid

from flask_mail import Message
from sqlalchemy import create_engine
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider
from itertools import islice
import os
import logging
import cv2
import numpy as np
from Main import mail
from werkzeug.security import generate_password_hash, check_password_hash


# 数据库连接测试
HOSTNAME = "127.0.0.1"
PORT = 3306
USERNAME = "root"
PASSWORD = "RemoteSensingSystem"
DATABASE = "RemoteSensingSystem"
SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8'
engine = create_engine(SQLALCHEMY_DATABASE_URI)
print(engine)


# 检查环境变量是否已设置
required_env_vars = ['OSS_ACCESS_KEY_ID', 'OSS_ACCESS_KEY_SECRET']
for var in required_env_vars:
    if var not in os.environ:
        logging.error(f"Environment variable {var} is not set.")
        exit(1)


auth = oss2.ProviderAuthV4(EnvironmentVariableCredentialsProvider())
endpoint = ""
region = ""
bucket_name = ""
bucket = oss2.Bucket(auth, endpoint, bucket_name, region=region)


def upload_image_to_oss(image_path):
    """上传本地图片到 OSS"""
    # 读取图片
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Failed to read image")

    # 将图片转换为字节流
    _, img_encoded = cv2.imencode('.jpg', image)
    img_bytes = img_encoded.tobytes()

    # 生成 OSS 文件名
    oss_filename = f"images/{os.path.basename(image_path)}"

    # 上传到 OSS
    bucket.put_object(oss_filename, img_bytes)
    print(f"Image uploaded to OSS: {oss_filename}")

    return oss_filename

def download_image_from_oss(oss_filename):
    """从 OSS 下载图片并显示"""
    # 从 OSS 获取图片
    img_bytes = bucket.get_object(oss_filename).read()

    # 将字节流转换为 OpenCV 图像
    img_array = np.frombuffer(img_bytes, np.uint8)
    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    # 显示图片
    cv2.imshow("Image from OSS", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def redis_test():
    import redis
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.set('test', 'Hello, Redis!')
    print(redis_client.get('test'))  # 输出：b'Hello, Redis!'


if __name__ == '__main__':
    #local_image_path = "C:\\Users\\86182\\Desktop\\bus.jpg"
    #oss_filename = upload_image_to_oss(local_image_path)
    #download_image_from_oss(oss_filename)
    # print(uuid.uuid4().hex)

    # redis_test()
    # print(generate_password_hash('123456789', method='scrypt'))
    import os
    from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
    from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
    from alibabacloud_tea_openapi import models as open_api_models

    # 假设 generate_verification_code 是一个生成验证码的函数
    from Main.utils.commons import generate_verification_code

    # 从环境变量中获取配置
    ALIBABA_CLOUD_ACCESS_KEY_ID = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')
    ALIBABA_CLOUD_ACCESS_KEY_SECRET = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
    SIGN_NAME = os.getenv('SIGN_NAME')  # 短信签名
    TEMPLATE_CODE = os.getenv('TEMPLATE_CODE')  # 短信模板代码


    # 初始化短信服务客户端
    def create_sms_client():
        config = open_api_models.Config(
            access_key_id=ALIBABA_CLOUD_ACCESS_KEY_ID,
            access_key_secret=ALIBABA_CLOUD_ACCESS_KEY_SECRET
        )
        return Dysmsapi20170525Client(config)


    # 发送短信
    def send_sms(phone_number, code):
        client = create_sms_client()
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            phone_numbers=phone_number,
            sign_name=SIGN_NAME,
            template_code=TEMPLATE_CODE,
            template_param=f'{{"code":"{code}"}}'
        )
        try:
            response = client.send_sms(send_sms_request)
            if response.body.code == 'OK':
                return True, response.body.biz_id  # 返回成功状态和 BizId
            else:
                return False, response.body.message  # 返回失败状态和错误信息
        except Exception as e:
            return False, str(e)  # 返回异常信息


    # 查询短信发送状态
    def query_sms_status(phone_number, biz_id, send_date):
        client = create_sms_client()
        query_request = dysmsapi_20170525_models.QuerySendDetailsRequest(
            phone_number=phone_number,
            biz_id=biz_id,
            send_date=send_date,  # 发送日期，格式为 yyyyMMdd
            page_size=10,  # 每页大小
            current_page=1  # 当前页码
        )
        try:
            response = client.query_send_details(query_request)
            return True, response.body  # 返回查询结果
        except Exception as e:
            return False, str(e)  # 返回异常信息


    # 示例：发送短信并查询状态
    if __name__ == "__main__":
        # 目标手机号
        phone_number = '18289686528'
        # 生成验证码
        code = generate_verification_code()
        # 发送短信
        success, result = send_sms(phone_number, code)
        if success:
            print(f"短信发送成功，BizId: {result}")
            # 查询短信发送状态
            biz_id = result
            send_date = '20250311'  # 替换为实际发送日期，格式为 yyyyMMdd
            query_success, query_result = query_sms_status(phone_number, biz_id, send_date)
            if query_success:
                print("短信发送状态查询成功:")
                print(query_result)
            else:
                print(f"短信发送状态查询失败: {query_result}")
        else:
            print(f"短信发送失败: {result}")

