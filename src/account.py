from flask import (
    Blueprint, g, render_template, url_for, request, redirect, session, flash, current_app
)

bp = Blueprint('account', __name__, url_prefix='/account')


