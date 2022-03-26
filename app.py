from bottle import default_app, get, static_file, run, view

# STYLESHEET #########################
@get("/static/style.css")
def style():
    return static_file("/static/style.css", root=".")
    
##############################
@get("/")
@view("index.html")
def _():
    return

##############################
try:
  # Production
  import production
  application = default_app()
except:
  # Development
    run(host='127.0.0.1', port=3333, server="paste", reloader=True, debug=True)