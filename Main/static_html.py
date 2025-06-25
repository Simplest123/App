# --*-- coding:utf-8 --*--
from flask import Blueprint, current_app, make_response, send_from_directory, session, jsonify
from flask_wtf.csrf import generate_csrf
import os

from Main.utils.response_code import RET

html = Blueprint('html', __name__, static_folder='static')


@html.route('/<re(".*"):file_name>')
def get_static_html(file_name):
    if not file_name:
        file_name = 'index.html'
    if file_name == 'favicon.ico':
        return current_app.send_static_file(file_name)
    if not file_name.endswith('.html'):
        file_name += '.html'
    file_name = 'html/' + file_name

    allowed_pages = ['html/index.html']
    if file_name not in allowed_pages and 'user_id' not in session:
        current_app.logger.error('User does not logged in')
        return '''
            <script>
                alert("请先登录");
                window.location.href = "/index.html";
            </script>
        '''

    response = make_response(current_app.send_static_file(file_name))
    csrf_token = generate_csrf()
    response.set_cookie('csrf_token', csrf_token)
    return response
