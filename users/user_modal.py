from bottle import get, redirect, request, view, response
import sqlite3
import jwt
from common import get_file_path, get_one_user, get_all_posts, is_uuid, only_update_body, get_all_tweets, get_all_users, confirm_user_is_logged_in, JWT_KEY

@get("/edit/<user_id>")
@view("user_modal.html")
def _(user_id):
    ##### the user needs to be logged in to access this page
    if not confirm_user_is_logged_in():
        return redirect("/login?alert-info=You're not logged in.", code=303)

    db = None
    redirect_path = None
    try:
        ##### validate that the id is a uuid4
        if is_uuid(user_id) == False:
            redirect_path = "/home?alert-info=Trying to edit the profile failed. Please try again."
            return
        
        ##### user id of logged in user
        logged_in_user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
        if not logged_in_user_id or is_uuid(logged_in_user_id) == False:
            redirect_path = "/home?alert-info=Trying to edit the profile failed. Please try again."
            return
        ##### make sure the user is trying to edit their own profile
        if logged_in_user_id != user_id:
            redirect_path = f"/home?alert-info=Trying to edit the profile failed. You can only edit your own profile."
            return

        ##### check that the user exsists in the database and get data
        ##### connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")
        ##### get user info from database
        user = db.execute("""
            SELECT user_display_name, user_username, user_profile_image, user_profile_header
            FROM users
            WHERE user_id = :user_id
            """,(user_id,)).fetchone()
        ##### redirect if user doesn't exist
        if not user:
            redirect_path = "/home?alert-info=User not found."
            return

        # if user is found, set info that's needed to display the editing inputs
        user_to_edit = {
            "user_id": user_id,
            "user_display_name": user[0],
            "user_username": user[1],
            "user_profile_image": user[2],
            "user_profile_header": user[3],
        }

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
            "header_color": [
                {
                    "error":"header_color_invalid",
                    "message": "Header color in invalid. Must be hex color."
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
        for input in ["user_display_name", "user_username", "user_profile_image", "user_profile_header"]:
            form_values[input] = request.params.get(input.replace("_", "-")) if request.params.get(input.replace("_", "-")) else ''

        #############################
        ##### the modal is displayed on top of the user profile, so get the data that's nessesary to display the user view

        ###### specify user profile to display
        user_to_display, error_redirect_path = get_one_user(user_to_edit["user_username"].lower(), user_id)
        if error_redirect_path != None:
            redirect_path = error_redirect_path
            return

        ##### return view
        return dict(
            user_id=user_id,                                            # user who's logged in
            users=get_all_users(user_id),                                                # all users to display 'who to follow'
            posts=get_all_posts(user_id, user_to_display["user_id"]),   # all posts from the user to display
            tweets=get_all_tweets(user_id),                             # all tweets 
            url=f"/edit/{user_id}",                                     # url
            title=f"Edit user",                                         # title
            modal='user',                                               # what modal is open
            only_update_body=only_update_body(),                        # load header and footer?
            user_to_display=user_to_display,                            # the user whose info we're viewing
            user_to_edit=user_to_edit,                                  # user to edit
            user_displayed_username=user_to_display['user_username'],
            possible_errors=possible_errors,                            # possible errors for form input
            errors=errors,
            form_values=form_values
            )

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return redirect("/home")

    finally:
        if db != None:
            db.close()
        if redirect_path != None:
            redirect(redirect_path)