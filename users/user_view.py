from bottle import get, view, request, redirect, response, template
import sqlite3
import jwt
import datetime
import json

from settings import get_file_path, get_all_posts, only_update_body, get_all_tweets, get_all_users, create_dictionary_from_data, confirm_user_is_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@get("/users/<username>")
@view("user.html")
def _(username):
    ##### the user needs to be logged in to access this page
    if not confirm_user_is_logged_in():
        return redirect("/login", code=303)

    try:
        ##### logged in user_id
        user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]

        ##### get all users data and all tweets data
        users = get_all_users(user_id)
        tweets = get_all_tweets(user_id)

        ###### specify user profile to display
        user_profile_to_display = None
        for user in users:
            if user["user_username"] == username:
                user_profile_to_display = user

        posts = get_all_posts(user_id, user_profile_to_display["user_id"])
        
        ##### return view
        return dict(
            user_id=user_id,                # user who's logged in
            users=users,                    # all users to display 'who to follow'
            posts=posts,
            tweets=tweets,                  # all tweets for feed
            url=f"/users/{username}",       # url
            title=username,                 # title
            modal=None,                     # what modal is opened
            only_update_body=only_update_body(),               # load header and footer?
            user_profile_to_display=user_profile_to_display,
            )

    except Exception as ex:
        print(ex)
        response.status = 500
        return redirect("/home")
