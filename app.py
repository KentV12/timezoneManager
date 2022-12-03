from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import os
import mysql.connector


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

connection = mysql.connector.connect(host="localhost", user=os.getenv("db_user"), passwd=os.getenv("db_pwd"), db="testdb")
mycursor = connection.cursor(prepared=True)

API_KEY = os.getenv("API_KEY")

# request all available timezones
url = f"http://api.timezonedb.com/v2.1/list-time-zone?key={API_KEY}&format=json"
response = requests.get(url)
responseDict = response.json()

# add timezones to list
all_timezones = []
for zone in responseDict["zones"]:
    all_timezones.append(zone["zoneName"])

@app.route("/")
def index():
    # display users list if there is a session. Else, redirect to login page
    if not session.get("name"): # use .get else session["name"] will cause error because no session is present
        return redirect("/login")
    # print("index", session['name'])

    # retrieve api and make a list
    url = f"http://api.timezonedb.com/v2.1/get-time-zone?key={API_KEY}&format=json&by=zone&zone=America/Vancouver"
    response = requests.get(url)
    # print(response.text)

    responseDict = response.json()
    timezones = []
    timezones.append(responseDict["formatted"])
    # print(timezones)

    return render_template("index.html", timezones=timezones, all_timezones=all_timezones)
        

@app.route("/login", methods=["GET", "POST"])
def login():
    # if request.method == "POST":
        # check if user exists in database
        # username = request.form.get("username")

        # mycursor.execute("SELECT * FROM users WHERE username = (%s)", (username, hash))
        # print('username correct')
        # password = request.form.get("password")

        # if username == "admin" and password == "123":
        #     print(username, password)
        #     session["name"] = username
        #     return redirect("/")
        # else:
        #     # incorrent user credentials
        #     return redirect("/login")

        # print(session['name'])

    # return render_template("login.html")
    return False

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":        
        print("registering...")

        # validate username and password
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        if username == "" or password == "" or password2 == "" or password != password2:
            return apology()

        mycursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        rows = mycursor.fetchall()

        if len(password) < 3 or len(rows) == 1:
            print('password invalid or username exists')
            return apology()

        # add to database
        hash = generate_password_hash(password)
        mycursor.execute("INSERT INTO users VALUES (%s, %s)", (username, hash))
        connection.commit()
        

        return render_template("login.html")
    else:
        return render_template("register.html")

@app.route("/add")
def addTimezone():
    # add timezone to database for a user
    return redirect("/")

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/")

# server side - error checking
@app.route("/apology")
def apology():
    return render_template("apology.html")