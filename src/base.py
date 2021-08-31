from flask import (
    Blueprint, g, render_template, url_for, request, redirect, session, flash, current_app
)
from mysql.connector.errors import IntegrityError
from flask_mail import Mail, Message
import re
import os
import random

from werkzeug.security import check_password_hash, generate_password_hash

import functools
from database_functions import get_db
from mysql.connector.errors import IntegrityError

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
        elif g.user[-1] == 0:
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


@bp.route('/account', methods=('GET', 'POST'))
@access_checker
def account():
    if request.method == 'POST':
        pass

    return render_template('account.html')


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
        error = None
        code = request.form['activation_code']
        if int(code) == int(session.get('activation_code')):
            session['check'] = True
            return redirect(url_for('index.information'))  # TODO: create information function for confirm info of user
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
        db = get_db()
        cursor = db.cursor()
        error = None
        command = """
                INSERT INTO users(id, first_name, last_name, email, password)
                VALUES(%s, %s, %s, %s, %s)
            """
        values = (username, first_name, last_name, email, password)
        try:
            cursor.execute(command, values)
        except IntegrityError:
            error = 'This user was exist.'
        else:
            db.commit()
            return redirect(url_for('index.login'))

        flash(error)
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

        db = get_db()
        cursor = db.cursor()
        error = None

        cursor.execute(
            "SELECT * FROM users WHERE id = %s", (username,)
        )
        user = cursor.fetchone()
        if not check_password_hash(session.get('security_code'), captcha):
            error = 'Incorrect security code.'
        elif user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user[4], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('index.account'))
        else:
            img_list = os.listdir("static/captcha")
            img = img_list[random.randint(0, 1000)]
            img_path = os.path.join("static/captcha", img)
            security_code = re.findall(r'^(.+)\.jpg$', img)[0]
            session.clear()
            session['security_code'] = security_code
            flash(error)
            return render_template('auth/login.html', variable=img_path)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE id = %s", (user_id,)
        )
        g.user = cursor.fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
