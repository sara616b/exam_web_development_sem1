from bottle import get, view, request, redirect, response
import jwt
from common import only_update_body, get_all_users, confirm_user_is_logged_in, is_uuid, JWT_KEY

@get("/users")
@view("all_users.html")
def _():
    ##### the user needs to be logged in to access this page else redirect to login page
    if not confirm_user_is_logged_in():
        return redirect("/login?alert-info=You're not logged in.", code=303)

    redirect_path = None
    try:
        ##### logged in user
        user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
        if not user_id or is_uuid(user_id) == False:
            redirect_path = "/home?alert-info=Trying to follow the user failed. Please try again."
            return

        ##### get all users data
        users = get_all_users(user_id)

        ##### return view
        return dict(
            user_id=user_id,                        # user who's logged in
            users=users,                            # all users
            url="/users",                           # url
            title="Users",                          # title
            only_update_body=only_update_body(),    # load header and footer?
            )

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return

    finally:
        if redirect_path != None:
            redirect(redirect_path)