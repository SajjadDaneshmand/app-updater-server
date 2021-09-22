from flask import (
    Blueprint, render_template, request, redirect, flash, current_app, g
)
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from tools import allowed_file, file_name
from tools import check_form_not_null
from base import access_checker
from databases import Application, Release, User, db
import hashlib
import os

bp = Blueprint('account', __name__, url_prefix='/account')


@bp.route('/', methods=['GET'])
@access_checker
def account():
    token = db.session.query(User.token).filter_by(username=g.user.username).first()[0]
    return render_template('account/account.html', token=token)


@bp.route('/add-app', methods=['GET', 'POST'])
@access_checker
def add_app():
    if request.method == 'POST':
        error = None
        if check_form_not_null(request.form['app_name'], request.form['app_author'], request.form['app_description']):
            name = request.form['app_name']
            author = request.form['app_author']
            description = request.form['app_description']
        else:
            error = 'یکی از فرم ها خالیست. بررسی شود'

        if error is None:
            try:
                app_add = Application(name=name, author=author, description=description)
                db.session.add(app_add)
                db.session.commit()
            except IntegrityError:
                message = 'این اپلیکیشن از قبل وجود داشته است.' \
                        '\n لطفا نام دیگری انتخاب کنید'
            else:
                message = 'اپلیکیشن با موفقیت وارد دیتابیس شد.'
            flash(message)
        else:
            flash(error)

    return render_template('account/add_app.html')


@bp.route('/add-version', methods=['GET', 'POST'])
@access_checker
def add_version():
    tuple_apps = db.session.query(Application.name).all()
    apps = [app[0] for app in tuple_apps]

    if request.method == 'POST':
        if request.form['apps'] in apps:
            app = request.form['apps']
            app_id = db.session.query(Application.id).filter_by(name=app).all()[0][0]
            version = request.form['version']
            changelog = request.form['changelog']
            file = request.files['app_file']
            if file.filename == '':
                error = 'فایل اپلیکیشن را انتخاب کنید'
                flash(error)
                return redirect(request.url)

            if check_form_not_null(version, changelog) and allowed_file(file.filename, 'exe'):
                exe_file_name = file_name(secure_filename(file.filename))
                file_name_hash = hashlib.sha256(bytes(exe_file_name.encode('utf-8'))).hexdigest() + '.exe'
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_name_hash)
                if file_name_hash in os.listdir(current_app.config['UPLOAD_FOLDER']):
                    error = 'این فایل از قبل وجود داشته است'
                    flash(error)
                    return redirect(request.url)

                file.save(file_path)

                release = Release(app_id=app_id, version=version, changelog=changelog, app_link=file_path)
                db.session.add(release)
                db.session.commit()

                error = 'فایل ذخیره و اطلاعات با موفقیت وارد دیتابیس شد'
            else:
                error = 'فیلدی را پر نکردید یا فایل مجاز به آپلود نبوده است'
        else:
            error = 'لطفا اپلیکیشن مد نظر را انتخاب کنید'
        if error:
            flash(error)

    apps.insert(0, 'انتخاب کنید')
    return render_template('account/add_version.html', apps=apps)
