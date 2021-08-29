from flask import (
    Blueprint, g, render_template, url_for, request, redirect, session, flash
)

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
            return redirect(url_for('auth.login'))

        return view(**kwargs)
    return wrapped_view


@bp.route('/upload', methods=('GET', 'POST'))
@login_required
def upload():
    if request.method == 'POST':
        pass

    return render_template('upload.html')


@bp.route('/signup', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        error = None

        if not username:
            error = 'username is required.'
        elif not password:
            error = 'password is required.'

        if error is None:
            try:
                cursor.execute(
                    "INSERT INTO User (username, password) VALUE (%s, %s)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except IntegrityError:
                error = f'User {username} is already registered.'
            else:
                return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        error = None

        cursor.execute(
            "SELECT * FROM User WHERE username = %s", (username,)
        )
        user = cursor.fetchone()
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user[2], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('index.upload'))

        flash(error)
    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM User WHERE id = %s", (user_id,)
        )
        g.user = cursor.fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))



