from bottle import get, request, redirect, response, view
import jwt
from common import get_all_posts, only_update_body, get_all_tweets, get_all_users, confirm_user_is_logged_in, JWT_KEY

@get("/home")
@view("home.html")
def _():
    ##### the user needs to be logged in to access this page, else redirect to login modal
    if not confirm_user_is_logged_in():
        return redirect("/login?alert-info=You're not logged in.", code=303)

    try:
        ##### logged in user's id
        user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]

        ##### return view
        return dict(
            user_id=user_id,                                    # user who's logged in
            users=get_all_users(user_id),                       # all users to display 'who to follow'
            posts=get_all_posts(user_id),                       # all posts for feed
            tweets=get_all_tweets(user_id),                     # all tweets for feed
            url="/home",                                        # url
            title="Home",                                       # title
            only_update_body=only_update_body(),                # load header and footer?
            alert_info=request.params.get("alert-info") or None,# alert message if any
            )

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return {"error": str(ex)}
