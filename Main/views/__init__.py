# --*-- coding:utf-8 --*--
from flask.blueprints import Blueprint

index = Blueprint('index', __name__, url_prefix='/')

from . import index_view, user_view, detect_view, forum_view, mail_view, phone_view, project_view
