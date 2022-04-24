from bottle import get, view, request, redirect, response
import jwt
from common import get_all_posts, get_one_user, only_update_body, get_all_tweets, is_uuid, get_all_users, confirm_user_is_logged_in, JWT_KEY

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

        ##### get the user to display's data
        user_to_display, error_redirect_path = get_one_user(username, user_id)
        if error_redirect_path != None:
            redirect_path = error_redirect_path
            return

        ##### return view
        return dict(
            user_id=user_id,                                            # user who's logged in
            users=get_all_users(user_id),                                                # all users to display 'who to follow'
            posts=get_all_posts(user_id, user_to_display["user_id"]),   # all posts from the user to display
            tweets=get_all_tweets(user_id),                             # all tweets 
            url=f"/users/{username}",                                   # url
            title=f"@{username}",                                       # title
            modal=None,                                                 # what modal is open
            only_update_body=only_update_body(),                        # load header and footer?
            user_to_display=user_to_display,                            # the user whose info we're viewing
            )

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        redirect_path = '/home?alert-info=Something went wrong.'
        return
    
    finally:
        if redirect_path != None:
            redirect(redirect_path)
