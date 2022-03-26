from bottle import default_app, get, static_file, run, view
import sqlite3

# STYLESHEET #########################
@get("/static/style.css")
def style():
    return static_file("/static/style.css", root=".")
# SCRIPT #########################
@get("/static/script.js")
def script():
    return static_file("/static/script.js", root=".")
    
##############################
@get("/")
@view("index.html")
def _():

    message = "Database is not connected"
    # connect to database
    try:
      import production
      db = sqlite3.connect("/home/buzzer/site/database/database.db")
    except:
      print("not production")
      db = sqlite3.connect("./database/database.db")

    try:
      if db:

        message = "Database is connected"
        # get tweet info from database
        user = db.execute("""
            SELECT *
            FROM users
            WHERE user_id = :user_id
        """,(1,)).fetchone()

      if user:
        message += f" and SELECTED this user: {user[1]}"
        user = {
          "user_id": user[0],
          "user_display_name": user[1],
          "user_username": user[2],
          "user_email": user[3],
        }

    except Exception as ex:
      print(ex)
    

    return dict(message=message)

##############################
try:
  # Production
  import production
  application = default_app()
except:
  # Development
    run(host='127.0.0.1', port=3333, server="paste", reloader=True, debug=True)