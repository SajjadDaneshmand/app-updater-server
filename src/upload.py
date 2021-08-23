from flask import (
    Blueprint, g, render_template, url_for
)
from auth import login_required

bp = Blueprint('index', __name__, url_prefix='/')


@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@bp.route('/upload', methods=('GET', 'POST'))
@login_required
def upload():
    name = g.user[1]
    index_page = 'index'
    return f'<h1>Hello {name}</h1><a href="{url_for(index_page)}"><br>This is a index page</a>'
