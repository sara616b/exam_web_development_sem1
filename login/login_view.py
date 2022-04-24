from bottle import get, redirect, response, request, view
from common import only_update_body, confirm_user_is_logged_in

@get("/login") # /login?error=email-invalid&email=hello&alert-info=You're not logged in
@view("login_modal.html")
def _():
    ##### if user is logged in redirect to home, if not stay on page
    if confirm_user_is_logged_in():
        return redirect("/home", code=303)

    try:
        ##### possible validation errors
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

        ##### return view
        return dict(
            url="/login",                                           # url
            title="Log in",                                         # title
            only_update_body=only_update_body(),                    # load header and footer?
            error=request.params.get("error"),                      # form input validation error
            possible_errors=possible_errors,                        # the possible errors that could be with the validation
            email=request.params.get("email"),                      # email to display in input
            alert_info=request.params.get("alert-info") or None,    # alert message
            )

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return {"error": str(ex)}
