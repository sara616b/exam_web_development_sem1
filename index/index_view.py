from bottle import get, redirect, response, request, view
from common import only_update_body, confirm_user_is_logged_in

@get("/")
@view("index.html")
def _():
    ##### if a user is logged in redirect to home, if not stay on page
    if confirm_user_is_logged_in():
        return redirect("/home", code=303)

    try:
        ##### alert info that may come with the query string
        alert_info = request.params.get("alert-info") or None

        ##### return view
        return dict(
            url="/",                                # url
            title="Buzzer",                         # title
            only_update_body=only_update_body(),    # load header and footer?
            alert_info=alert_info,                  # alert message that may be None
            )

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return
