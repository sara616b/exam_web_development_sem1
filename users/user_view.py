from bottle import get, view, request, redirect, response
import jwt
from common import get_all_posts, only_update_body, get_all_tweets, is_uuid, get_all_users, confirm_user_is_logged_in, JWT_KEY

@get("/users/<username>")
@view("user.html")
def _(username):
    ##### the user needs to be logged in to access this page else redirect
    if not confirm_user_is_logged_in():
        return redirect("/login?alert-info=You're not logged in.", code=303)

    redirect_path = None
    try:
        ##### check that a username has been passed
        if not username or username == '' or username == None:
            redirect_path = "/home?alert-info=Couldn't find user. Please try again."
            return

        ##### logged in user_id
        user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
        if not user_id or is_uuid(user_id) == False:
            redirect_path = "/home?alert-info=Couldn't find user. Please try again."
            return

        ##### get all users and tweets data
        users = get_all_users(user_id)
        tweets = get_all_tweets(user_id)

        ###### specify user profile to display
        user_profile_to_display = None
        for user in users:
            if user["user_username"] == username:
                user_profile_to_display = user

        ##### if no user with the right username is found redirect with error
        if user_profile_to_display == None:
            redirect_path = "/home?alert-info=Couldn't find user. Please try again."
            return

        ##### get all posts data
        posts = get_all_posts(user_id, user_profile_to_display["user_id"])

        print(user_profile_to_display)
        ##### return view
        return dict(
            user_id=user_id,                                # user who's logged in
            users=users,                                    # all users to display 'who to follow'
            posts=posts,                                    # all posts from the user to display
            tweets=tweets,                                  # all tweets 
            url=f"/users/{username}",                       # url
            title=f"@{username}",                                 # title
            modal=None,                                     # what modal is open
            only_update_body=only_update_body(),            # load header and footer?
            user_profile_to_display=user_profile_to_display,# the user whose info we're viewing
            )

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return
    
    finally:
        if redirect_path != None:
            redirect(redirect_path)
