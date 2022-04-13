from bottle import get, view, request, redirect, response, template
import sqlite3
import jwt
import datetime
import json

from settings import get_file_path, only_update_body, get_all_users, create_dictionary_from_data, confirm_user_is_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@get("/users")
@view("all_users.html")
def _():
    ##### the user needs to be logged in to access this page
    if not confirm_user_is_logged_in():
        return redirect("/login", code=303)

    try:
        ##### logged in user
        user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]

        ##### get all users data
        users = get_all_users(user_id)

        ##### return view
        return dict(
            user_id=user_id,    # user who's logged in
            users=users,        # all users to display 'who to follow'
            url="/users",    # url
            title="Users",      # title
            modal=None,         # what modal is opened
            only_update_body=only_update_body(),      # load header and footer?
            )

    except Exception as ex:
        print(ex)
        response.status = 500
        return
