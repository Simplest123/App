# --*-- coding:utf-8 --*--
from functools import wraps
import random
import string

from flask import session, jsonify, g
from werkzeug.routing import BaseConverter

from Main.utils.response_code import RET


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]


def generate_verification_code(length=6):
    return ''.join(random.choices(string.digits, k=length))


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify(re_code=RET.SESSIONERR, msg='User has not logged in yet')
        else:
            g.user_id = user_id
            return view_func(*args, **kwargs)
    return wrapper
