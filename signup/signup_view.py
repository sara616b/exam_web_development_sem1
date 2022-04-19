from bottle import get, response, redirect, view, request
from common import only_update_body, confirm_user_is_logged_in

@get("/signup")
@view("signup_modal.html")
def _():
    ##### if user is logged in redirect to home, if not stay on page
    if confirm_user_is_logged_in():
        return redirect("/home", code=303)

    try:
        ##### dictionary with the possible form validation errors
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
                    "error":"username_no_special_characters",
                    "message":"Username can't contain special characters"
                },
                {
                    "error":"username_no_spaces",
                    "message":"Username can't contain spaces"
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

        ##### possible errors in list
        possible_errors_list = []
        for value in possible_errors:
            for error_dict in possible_errors[value]:
                possible_errors_list.append(error_dict["error"])

        ##### get errors from query string
        errors = {}
        for error in possible_errors_list:
            errors[error] = request.params.get(error.replace("_", "-")) if request.params.get(error.replace("_", "-")) else 'none'

        ##### get values for form from query string
        form_values = {}
        for input in ["display_name", "username", "email"]:
            form_values[input] = request.params.get(input.replace("_", "-")) if request.params.get(input.replace("_", "-")) else ''

        ##### get alert info
        alert_info = request.params.get("alert-info") or None

        return dict(
            url="/signup",                          # url
            title="Sign up",                        # title
            only_update_body=only_update_body(),    # load header and footer?
            errors=errors,                          # form validation errors
            form_values=form_values,                # values for form input
            possible_errors=possible_errors,        # possible errors for form input
            alert_info=alert_info,                  # alert message
            )
    
    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return
