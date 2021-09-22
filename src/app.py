from flask import Flask, g, redirect, url_for, request
from flask_admin.contrib.sqla import ModelView
from settings import UPLOAD_FOLDER
from flask_admin import BaseView
from flask_admin import Admin


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI='mysql+mysqlconnector://sajjad:12345600@localhost/products',
        SECRET_KEY='d0c90397995b2c31834b20d78574eaa0',
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
        MAIL_USERNAME='moiencompany@gmail.com',
        MAIL_PASSWORD='domainnamesystem',
        MAIL_SERVER='smtp.gmail.com',
        MAIL_USE_SSL=True,
        MAIL_PORT=465,
        UPLOAD_FOLDER=UPLOAD_FOLDER,
        FLASK_ADMIN_SWATCH='darkly',

    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    return app


app = create_app()


class MyModelView(ModelView):
    def is_accessible(self):
        if g.user is None:
            return False
        if g.user.admin:
            return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to index page if user doesn't have access
        return redirect(url_for('index.index', next=request.url))


if __name__ == '__main__':
    import base
    app.register_blueprint(base.bp)

    import account
    app.register_blueprint(account.bp)

    import api
    app.register_blueprint(api.bp)

    from databases import User, Release, Application, db
    admin = Admin(name='admin', template_mode='bootstrap4')
    admin.add_view(MyModelView(User, db.session))
    admin.add_view(MyModelView(Release, db.session))
    admin.add_view(MyModelView(Application, db.session))
    admin.init_app(app)
    db.init_app(app)
    app.run(host='0.0.0.0', port=5000, debug=True)
