from bottle import default_app, get, static_file, redirect, request, run, view

from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY
##############################
@get("/")
@view("index.html")
def _():
    try:
        check_if_logged_in()
    except:
        # if check_if_logged_in raises an exception
        # the user isn't logged in
        is_xhr = True if request.headers.get('spa') else False
        return dict(
            url="/",
            title="Buzzer",
            modal=None,
            is_xhr=is_xhr,
            )
    else:
        # if the user is logged in redirect to home feed
        return redirect("/home")
    