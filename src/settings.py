import os


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

INFO_FILE_NAME = 'info.conf'
INFO_FiLE_PATH = os.path.join(BASE_DIR, INFO_FILE_NAME)

