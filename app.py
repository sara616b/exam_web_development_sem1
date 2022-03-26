from bottle import default_app, get, static_file, run

##############################
@get("/")
def _():
    return "Hi"

##############################
try:
  # Production
  import production
  application = default_app()
except:
  # Development
    run(host='127.0.0.1', port=3333, server="paste", reloader=True, debug=True)