from bottle import default_app, get, static_file, redirect, run, view, request, template
from settings import get_file_path, only_update_body, confirm_user_is_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

##############################
@get("/signup")
@view("signup_modal.html")
def _():
    
    ##### if user is logged in redirect to home, if not stay on page
    if confirm_user_is_logged_in():
        return redirect("/home", code=303)
    
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

    possible_errors = {
        "display_name": [
            {
                "error":"display_name_missing",
                "message":"Display name missing"
            },
            {
                "error":"display_name_length",
                "message":"Display name must be less than 100 characters"
            },
        ],
        "username": [
            {
                "error":"username_missing",
                "message":"Username missing"
            },
            {
                "error":"username_length",
                "message":"Username must be less than 100 characters"
            },
            {
                "error":"user_exists_username",
                "message":"A user with this username already exists"
            },
        ],
        "email": [
            {
                "error":"email_missing",
                "message": "Email missing"
            },
            {
                "error":"email_invalid",
                "message": "Email is invald"
            },
            {
                "error":"user_exists_email",
                "message": "A user with this email already exists"
            }
        ], 
        "password": [
            {
                "error":"password_missing",
                "message": "Password missing"
            },
            {
                "error":"password_short",
                "message": "Password must be more than 3 characters long"
            },
            {
                "error":"passwords_different",
                "message": "Passwords don't match"
            }
        ]
    }

    ##### get values in form from query string so they're remembered after reload
    form_values = {}
    for input in ["display-name", "username", "email"]:
        form_values[f"{input.replace('-', '_')}"] = request.params.get(input) if request.params.get(input) else ''

    return dict(
        url="/signup",
        title="Sign up",
        only_update_body=only_update_body(),      # load header and footer?
        errors=errors,
        form_values=form_values,
        possible_errors=possible_errors,
        )
