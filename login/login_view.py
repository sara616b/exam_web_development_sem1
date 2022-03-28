from bottle import default_app, get, static_file, redirect, run, view
import sqlite3
from settings import *

##############################
@get("/login")
@view("login.html")
def _():
    try:
      return
    except Exception as ex:
      print(ex)
      return {"error":ex}
