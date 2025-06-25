# --*-- coding:utf-8 --*--
from flask import session
from flask_migrate import Migrate
from Main import get_app, db
from Main import database
import click


##############################
# app.register_blueprint(user_blue)
# migrate:
#   1、flask db init
#   2、flask db migrate -m
#   3、flask db upgrade
#   4、flask db downgrade <version_id>
#   5、flask db current
#   6、flask db history
##############################

app = get_app('develop')
migrate = Migrate(app, db)


@app.cli.command("list-routes")
def list_routes():
    for rule in app.url_map.iter_rules():
        print(f"Endpoint: {rule.endpoint}, Path: {rule.rule}")


if __name__ == '__main__':
    app.run(debug=True)
