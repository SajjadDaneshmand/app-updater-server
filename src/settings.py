import os


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
SITE_PATH = 'http://127.0.0.1:5000'
INFO_FILE_NAME = 'info.conf'
INFO_FiLE_PATH = os.path.join(BASE_DIR, INFO_FILE_NAME)

