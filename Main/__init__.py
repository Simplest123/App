# --*-- coding:utf-8 --*--
import os
import oss2
import logging
from logging.handlers import RotatingFileHandler

from flask_mail import Mail
from oss2.credentials import EnvironmentVariableCredentialsProvider
from alibabacloud_tea_openapi import models as open_api_models

import redis
from flask import Flask, current_app
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from config import configs
from Main.utils.commons import RegexConverter
from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client

ALIBABA_CLOUD_ACCESS_KEY_ID = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')
ALIBABA_CLOUD_ACCESS_KEY_SECRET = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
SIGN_NAME = os.getenv('SIGN_NAME')
TEMPLATE_CODE = os.getenv('TEMPLATE_CODE')

db = SQLAlchemy()
redis_conn = None
mail = None
client = None


def setupLogging(level):
    logging.basicConfig(level=level)
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1000, backupCount=10)
    formatter = logging.Formatter('%(levelname)s %(filename)s: %(lineno)d %(message)s')
    file_log_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_log_handler)


def get_app(config_name):
    setupLogging(configs[config_name].LOGGING_LEVEL)

    app = Flask(__name__)
    app.config.from_object(configs[config_name])

    global db, redis_conn, mail, client
    db.init_app(app)  # Database
    redis_conn = redis.StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT)  # Redis
    mail = Mail(app)  # Email
    client = Dysmsapi20170525Client(open_api_models.Config(  # Phone
        access_key_id=ALIBABA_CLOUD_ACCESS_KEY_ID,
        access_key_secret=ALIBABA_CLOUD_ACCESS_KEY_SECRET
    ))
    mail.debug = True

    Session(app)
    CSRFProtect(app)

    app.url_map.converters['re'] = RegexConverter

    from Main.static_html import html
    from Main.views import index
    app.register_blueprint(html)
    app.register_blueprint(index)

    return app


def get_oss():
    required_env_vars = ['OSS_ACCESS_KEY_ID', 'OSS_ACCESS_KEY_SECRET']
    for var in required_env_vars:
        if var not in os.environ:
            current_app.logger.error('oss services are not yet prepared')
            exit(1)

    auth = oss2.ProviderAuthV4(EnvironmentVariableCredentialsProvider())
    endpoint = "https://oss-cn-beijing.aliyuncs.com"
    region = "cn-beijing"
    bucket_name = "remote-sensing-system"
    return oss2.Bucket(auth, endpoint, bucket_name, region=region)


bucket = get_oss()
