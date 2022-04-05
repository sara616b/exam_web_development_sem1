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
        
        ##### get errors from query string
        errors = {}
        for error in [
            "display-name-missing",
            "display-name-length",
            "username-missing",
            "username-length",
            "email-missing",
            "email-invalid",
            "password-missing",
            "password-short",
            "passwords-different",
            "user-exists-username",
            "user-exists-email",
            ]:
            errors[error.replace("-", "_")] = request.params.get(error) if request.params.get(error) else 'none'
        
        print(errors)

        ##### get values in form from query string so they're remembered after reload
        form_values = {}
        for input in ["display-name", "username", "email"]:
            form_values[f"{input.replace('-', '_')}"] = request.params.get(input) if request.params.get(input) else ''

        ##### check whether there's a need for loading header and footer
        is_xhr = True if request.headers.get('spa') else False

        return dict(
            url="/signup",
            title="Sign up",
            modal='signup',
            is_xhr=is_xhr,
            errors=errors,
            form_values=form_values,
            )
    else:
        ##### if the user is logged in redirect to home feed
        return redirect("/home")
    