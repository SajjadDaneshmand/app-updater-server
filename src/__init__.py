from mysql.connector import connect
from flask import Flask

import settings
import os


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='d0c90397995b2c31834b20d78574eaa0',
        DATABASE=connect(option_files=settings.INFO_FiLE_PATH),
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=465,
        MAIL_USERNAME='moiencompany@gmail.com',
        MAIL_PASSWORD='domainnamesystem',
        MAIL_USE_SSL=True
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    import base
    app.register_blueprint(base.bp)
    app.add_url_rule('/', endpoint='index')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
