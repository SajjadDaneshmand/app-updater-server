from werkzeug.security import check_password_hash, generate_password_hash
from flask import (
    Blueprint, g, render_template, url_for, request, redirect, session, flash, current_app, jsonify, send_file
)
from databases import Release, User, db
from werkzeug.exceptions import BadRequestKeyError
from sqlalchemy.exc import IntegrityError
from flask_mail import Mail, Message
import functools
import random
import re
import os

bp = Blueprint('index', __name__, url_prefix='/')


@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('index.login'))

        return view(**kwargs)
    return wrapped_view


def access_checker(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('index.login'))
        elif g.user.access == 0:
            return redirect(url_for('index.access'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/do-not-access', methods=['GET'])
@login_required
def access():
    return render_template('access.html')


def signup_email_confirm_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('activation_code'):
            return redirect(url_for('index.email_sender'))

        return view(**kwargs)

    return wrapped_view


def signup_information(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('check'):
            return redirect(url_for('index.email_sender'))
        return view(**kwargs)

    return wrapped_view


@bp.route('/signup', methods=('GET', 'POST'))
def email_sender():
    if request.method == 'POST':
        email = request.form['email']
        receivers = [email]
        mail = Mail(current_app)
        activation_code = random.randint(1000, 9999)
        session.clear()
        session['email'] = email
        session['activation_code'] = activation_code
        msg = Message('Activation Code', sender='moiencompany@gmail.com', recipients=receivers)
        msg.html = f"<h1>Hi :)</h1><p>This is your activation code from moien app updater: <strong>{activation_code}" \
                   f"</strong></p>"
        mail.send(msg)
        return redirect(url_for('index.email_verification'))

    return render_template('auth/signup.html')


@bp.route('/confirm-email', methods=['GET', 'POST'])
@signup_email_confirm_required
def email_verification():
    if request.method == 'POST':
        code = request.form['activation_code']
        if int(code) == int(session.get('activation_code')):
            session['check'] = True
            return redirect(url_for('index.information'))
        else:
            error = 'Incorrect activation code.'
        flash(error)

    return render_template('auth/confirm_email.html')


@bp.route('/signup/information', methods=['GET', 'POST'])
@signup_information
def information():
    if request.method == 'POST':
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = session.get('email')
        password = generate_password_hash(request.form['password'])
        try:
            add_user = User(username=username, first_name=first_name, last_name=last_name,
                            email=email, password=password, token=os.urandom(64).hex())
            db.session.add(add_user)
            db.session.commit()
        except IntegrityError:
            error = 'This username was for another person'
            flash(error)
            return redirect(request.url)
        return redirect(url_for('index.login'))

    return render_template('auth/information.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'GET':
        img_list = os.listdir("static/captcha")
        img = img_list[random.randint(0, 1000)]
        img_path = os.path.join("static/captcha", img)
        security_code = re.findall(r'^(.+)\.jpg$', img)[0]
        session.clear()
        session['security_code'] = security_code
        return render_template('auth/login.html', variable=img_path)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        captcha = request.form['captcha']
        user = User.query.filter_by(username=username).first()

        error = None

        if not check_password_hash(session.get('security_code'), captcha):
            error = 'Incorrect security code.'
        elif user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.username
            return redirect(url_for('account.account'))
        else:
            img_list = os.listdir("static/captcha")
            img = img_list[random.randint(0, 1000)]
            img_path = os.path.join("static/captcha", img)
            security_code = re.findall(r'^(.+)\.jpg$', img)[0]
            session.clear()
            session['security_code'] = security_code
            flash(error)
            return render_template('auth/login.html', variable=img_path)


@bp.route('/uploads/<name>', methods=['POST'])
def upload(name):
    try:
        token = request.form['token']
    except BadRequestKeyError:
        error = {
            'status': 'failed',
            'message': 'please send requirement (token)'
        }
        return jsonify(error)

    token_verification = db.session.query(User).filter_by(token=token).first()

    if token_verification is None:
        error = {
            'status': 'failed',
            'message': 'this token does not exist'
        }
        return jsonify(error)
    simple_version = db.session.query(Release.app_link).first()[0]
    upload_dir = simple_version.rsplit('/', 1)[0]
    app_full_path = upload_dir + '/' + name
    apps = os.listdir(upload_dir)

    user_access_checker = int(db.session.query(User.access).filter_by(token=token).first()[0])

    if not user_access_checker:
        error = {
            'status': 'failed',
            'message': 'you don\'t have permission'
        }
        return jsonify(error)

    if name not in apps:
        error = {
            'status': 'failed',
            'message': 'this file does not exist'
        }
        return jsonify(error)

    get_version = db.session.query(Release.app_link).filter(Release.app_link == app_full_path).first()[0]
    return send_file(get_version)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(username=user_id).first()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index.login'))
