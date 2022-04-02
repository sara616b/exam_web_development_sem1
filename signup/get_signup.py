from bottle import default_app, get, static_file, redirect, run, view, request
import sqlite3
from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

##############################
@get("/signup")
@view("index.html")
def _():
    try:
        check_if_logged_in()
    except:
        # if check_if_logged_in raises an exception
        # the user isn't logged in
        is_xhr = True if request.headers.get('spa') else False
        return dict(
            url="/signup",
            title="Sign up",
            modal='signup',
            is_xhr=is_xhr,
            )
    else:
        # if the user is logged in redirect to home feed
        return redirect("/home")
    