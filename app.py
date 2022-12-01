from flask import Flask, session, render_template, request, redirect
from flask_session import Session
import requests
import os

# Note: API can only retrieve one request per second
# "flask --debug run" to enable reload on save
# todo:
#   store api key in env variables: can use $env:var_name = "key" to set key
#   access timezone via api
#   dropdown for all timezones that can be searched? can retrieve all timezone and loop to make a list
#   implement a database
#   implement searches in utc?
#   implement password hashing



# configure app
app = Flask(__name__)

# configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    # display users list if there is a session. Else, redirect to login page

    if not session.get("name"): # use .get else session["name"] will cause error because no session is present
        return redirect("/login")

    # print("index", session['name'])

    # retrieve api and make a list
    API_KEY = os.getenv("API_KEY")
    url = f"http://api.timezonedb.com/v2.1/get-time-zone?key={API_KEY}&format=json&by=zone&zone=America/Vancouver"
    response = requests.get(url)
    print(response.text)

    responseDict = response.json()
    timezones = []
    timezones.append(responseDict["formatted"])
    print(timezones)

    return render_template("index.html", timezones=timezones)
        

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if user exists in database
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "123":
            print(username, password)
            session["name"] = username
            return redirect("/")
        else:
            # incorrent user credentials
            return redirect("/login")

        # print(session['name'])

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # validate username and password
        # add to database
        username = request.form.get("username")
        password = request.form.get("password")
        print(username, password)
        return render_template("register.html")
    else:
        return render_template("register.html")

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/")