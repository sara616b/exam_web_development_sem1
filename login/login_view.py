from bottle import default_app, get, static_file, redirect, request, run, view, response, template
import sqlite3
from settings import get_file_path, only_update_body, confirm_user_is_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

##############################
@get("/login")
@view("login_modal.html")
def _():
    ##### if user is logged in redirect to home, if not stay on page
    if confirm_user_is_logged_in():
        return redirect("/home", code=303)
        
    ##### get errors from query string
    error = request.params.get("error")
    possible_errors = {
        "email": [
            {
                "error":"email-missing",
                "message": "Email missing"
            },
            {
                "error":"email-invalid",
                "message": "Email is invald"
            },
            {
                "error":"no-match",
                "message": "Email and password don't match"
            }
        ], 
        "password": [
            {
                "error":"password-missing",
                "message": "Password missing"
            },
            {
                "error":"password-short",
                "message": "Password too short"
            },
            {
                "error":"no-match",
                "message": "Email and password don't match"
            }
        ]
    }
     

    ##### get email from params to set as value in input 
        ##### get email from params to set as value in input 
    ##### get email from params to set as value in input 
    email = request.params.get("email")

    ##### return view
    return dict(
        url="/login",       # url
        title="Log in",     # title
        only_update_body=only_update_body(),      # load header and footer?
        error=error,        # input error
        possible_errors=possible_errors,
        email=email,        # email to display in input
        )
