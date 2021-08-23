from mysql.connector import connect
from flask import g
import settings


def get_db():
    if 'db' not in g:
        g.db = connect(option_files=settings.INFO_FiLE_PATH)
    return g.db
