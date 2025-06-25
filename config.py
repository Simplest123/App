# --*-- coding:utf-8 --*--
import logging
import os

from redis import StrictRedis


class Config(object):
    DEBUG = True

    # logging
    LOGGING_LEVEL = logging.DEBUG

    SECRET_KEY = 'ix4En7l1Hau10aPq8kv8987gVl1s2Zo6eA+5+R+CXor8G3Jo0I++ks001jz3XuXl'
    session_protection = 'strong'

    # MySQL
    HOSTNAME = "127.0.0.1"
    PORT = 3306
    USERNAME = "root"
    PASSWORD = "RemoteSensingSystem"
    DATABASE = "RemoteSensingSystem"
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # mail
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = '1941227494@qq.com'

    # Redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_DB = 1

    # session
    SESSION_TYPE = 'redis'  # session
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 3600 * 3600 * 24  # session limitation


class DevelopConfig(Config):
    LOGGING_LEVEL = logging.INFO


class UnitTestConfig(Config):
    LOGGING_LEVEL = logging.DEBUG
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@127.0.0.1:3306/test'


class ProductionConfig(Config):
    LOGGING_LEVEL = logging.WARNING
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@47.106.93.190:3306/SkyEye'
    REDIS_HOST = '47.106.93.190'


configs = {
    'default': Config,
    'develop': DevelopConfig,
    'unittest': UnitTestConfig,
    'production': ProductionConfig
}
