from bottle import redirect, request, put, response
import time
import sqlite3
import os
import jwt
import re
from common import get_file_path, REGEX_HEX_COLOR, REGEX_NO_SPECIAL_CHARACTERS, check_the_image, confirm_user_is_logged_in, is_uuid, JWT_KEY

@put("/edit/<user_id>")
def _(user_id):

    ##### the user needs to be logged in to access this page
    if not confirm_user_is_logged_in():
        return redirect("/login?alert-info=You're not logged in.", code=303)

    db = None
    redirect_path = None
    try:
        ##### check whether the id is a uuid4
        if is_uuid(user_id) == False:
            redirect_path = "/edit/{user_id}?alert-info=Trying to edit the user failed. Please try again."
            return
        
        ##### user id of logged in user
        logged_in_user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
        if logged_in_user_id != user_id:
            redirect_path = "/edit/{user_id}?alert-info=Trying to edit the user failed. Please try again."
            return

        ##### form validation errors
        errors = []
        ##### user id stays the same
        updated_user_data = {"user_id":user_id}

        ##### display name
        display_name = request.forms.get("user_display_name")
        if not display_name:
            errors.append("display-name-missing")
        elif len(display_name) < 1 or len(display_name) > 100:
            errors.append("display-name-length")

        ##### username
        username = request.forms.get("user_username")
        if not username:
            errors.append("username-missing")
        elif not re.match(REGEX_NO_SPECIAL_CHARACTERS, username):
            errors.append("username-no-special-characters")
        elif " " in username:
            errors.append("username-no-spaces")
        elif len(display_name) < 1 or len(display_name) > 100:
            errors.append("username-length")

        ##### user_header_color
        user_header_color = request.forms.get("user_header")
        if user_header_color and not re.match(REGEX_HEX_COLOR, user_header_color):
            errors.append("header-color-invalid")

        ##### connect database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")


        ##### select users that matches input
        users_in_database = db.execute("""
            SELECT user_username
            FROM users
            WHERE user_username = :username and user_id != :user_id
            """, (username, user_id)).fetchall()

        ##### if any users were found, check whether username or email is already in use
        if users_in_database:
            for user in users_in_database:
                if username and user[0] == username:
                    errors.append("user-exists-username")
    
        current_user_data = db.execute(f"""
            SELECT user_display_name, user_username, user_profile_image, user_profile_header
            FROM users
            WHERE user_id == :user_id
            """, (user_id,)).fetchone()

        if display_name and display_name != current_user_data[0]:
            updated_user_data["user_display_name"] = display_name
        if username and username != current_user_data[1]:
            updated_user_data["user_username"] = username
        if user_header_color != current_user_data[3]:
            updated_user_data["user_profile_header"] = user_header_color
    
        print(user_header_color, current_user_data[3])
        ##### image - remove, add new
        current_image = current_user_data[2]

        new_image_name = None
        image_name = request.forms.get("image_name")
        print(image_name, current_image)
        ##### if there's no image or the image name isn't the same as the current image name, delete current image
        if image_name and current_image != "NULL":
            if os.path.exists(f"{get_file_path()}/static/images/profiles/{current_image}"):
                os.remove(f"{get_file_path()}/static/images/profiles/{current_image}")
            updated_user_data["user_profile_image"] = None
        
        if image_name:
            ##### check if there's an image in request.files and if so, validate it 
            redirect_image_error, new_image_name = check_the_image(request.files.get("user_image"), "profiles")
            if redirect_image_error:
                redirect_path = f"/edit/{user_id}{redirect_image_error}&display-name={display_name}&username={username}"
                return

            ##### set new image name
            if new_image_name:
                updated_user_data["user_profile_image"] = new_image_name

        ##### create string for all values that need to be set in the database query
        set_parts = []
        for value in updated_user_data:
            if str(value) != "tweet_id":
                set_parts.append(f"{str(value)} = :{str(value)}")
        set_parts = ",".join(set_parts)

        print(set_parts)
        ##### update tweet in database
        counter = db.execute(f"""
            UPDATE users
            SET {set_parts}
            WHERE user_id = :user_id
            """, updated_user_data).rowcount
        
        ##### check that 1 and only 1 tweet was updated
        if counter != 1:
            redirect_path = f"/edit/{user_id}?alert-info=Editing user failed. Please try again."
            return
        else:
            db.commit()
            redirect_path = f"/users/{username}"
            return

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return redirect("/home?alert-info=Editing tweet failed. Please try again.")

    finally:
        if db != None:
            db.close()
        if redirect_path != None: 
            return redirect(redirect_path)
