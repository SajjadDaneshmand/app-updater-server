def check_form_not_null(*args):
    for i in args:
        if len(i) == 0:
            return False
    return True


def allowed_file(filename, *args):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in args


def file_name(filename):
    return filename.rsplit('.', 1)[0]

