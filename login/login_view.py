from bottle import default_app, get, static_file, redirect, request, run, view, response
import sqlite3
from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

##############################
@get("/login")
@view("index.html")
def _():
    try:
        check_if_logged_in()
    except:
        # if check_if_logged_in raises an exception
        # the user isn't logged in
        
        ##### get errors from query string
        error = request.params.get("error")

        ##### get email from params to set as value in input 
        email = request.params.get("email")

        ##### check whether there's a need for loading header and footer
        is_xhr = True if request.headers.get('spa') else False

        ##### return view
        return dict(
            url="/login",       # url
            title="Log in",     # title
            modal="login",      # modal open
            is_xhr=is_xhr,      # load header and footer?
            error=error,        # input error
            email=email,        # email to display in input
            )

    else:
        ##### if the user is logged in redirect to home feed
        return redirect("/home")
