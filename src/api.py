from databases import Application, Release, User, db
from werkzeug.exceptions import BadRequestKeyError
from flask import Blueprint, jsonify, request
from settings import SITE_PATH

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/get-app', methods=['POST'])
def app_api():
    try:
        name = request.form['name']
        version = request.form['version']
        token = request.form['token']
    except BadRequestKeyError:
        error = {
            'status': 'failed',
            'message': 'please send all of requirement (name, version and token)'
        }
        return jsonify(error)

    token_verification = db.session.query(User).filter_by(token=token).first()

    if token_verification is None:
        error = {
            'status': 'failed',
            'message': 'this token does not exist'
        }
        return jsonify(error)

    name_verification = db.session.query(Application).filter_by(name=name).first()

    if name_verification is None:
        error = {
            'status': 'failed',
            'message': 'this name does not exist'
        }
        return jsonify(error)

    access_checker = int(db.session.query(User.access).filter_by(token=token).first()[0])

    if not access_checker:
        error = {
            'status': 'failed',
            'message': 'you don\'t have permission'
        }
        return jsonify(error)

    if version == 'latest':
        version_verification = db.session.query(Release).filter(Application.name == name)\
            .order_by(Release.date_of_release.desc()).limit(1).first()
        if version_verification is None:
            error = {
                'status': 'failed',
                'message': 'this does not have any version'
            }
            return jsonify(error)

        app_link = version_verification.app_link[version_verification.app_link.find('/upload'):]
        app_link = SITE_PATH + app_link
        data = {
            'status': 'ok',
            'application_info': {
                'name': name_verification.name,
                'author': name_verification.author,
                'description': name_verification.description
            },
            'version_info': {
                'version': version_verification.version,
                'changelog': version_verification.changelog,
                'app_link': app_link,
                'date_of_release': version_verification.date_of_release
            }
        }
        return jsonify(data)

    version_verification = Release.query.filter(Application.name == name, Release.version == version).first()

    if version_verification is None:
        error = {
            'status': 'failed',
            'message': 'this version of that app does not exist'
        }
        return jsonify(error)

    app_link = version_verification.app_link[version_verification.app_link.find('/upload'):]
    app_link = SITE_PATH + app_link
    data = {
        'status': 'ok',
        'application_info': {
            'name': name_verification.name,
            'author': name_verification.author,
            'description': name_verification.description
        },
        'version_info': {
            'version': version_verification.version,
            'changelog': version_verification.changelog,
            'app_link': app_link,
            'date_of_release': version_verification.date_of_release
        }
    }
    return jsonify(data)







