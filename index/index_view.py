from bottle import default_app, get, static_file, redirect, request, run, view, template

from settings import get_file_path, only_update_body, confirm_user_is_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY
##############################
@get("/")
@view("index.html")
def _():
    ##### if user is logged in redirect to home, if not stay on page
    if confirm_user_is_logged_in():
        return redirect("/home", code=303)

    ##### return view
    return dict(
        url="/",            # url
        title="Buzzer",     # title
        only_update_body=only_update_body(),      # load header and footer?
        )
    