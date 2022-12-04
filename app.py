from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import os
import mysql.connector
from time import sleep


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
mycursor = connection.cursor(dictionary=True)

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
    # no cookie - not logged in
    if not session.get("name"): # use .get else session["name"] will cause error because no session is present
        return redirect("/login")

    # find user on database and request their timezones
    mycursor.execute( "SELECT * FROM usertimezones WHERE username = (%s)", (session["name"],) )
    rows = mycursor.fetchall()
    timezones = []

    # make a request for user's timezones
    for row in rows:
        sleep(1) # only one response per second,  specified by API documentation
        zone = row["zone"]
        url = f"http://api.timezonedb.com/v2.1/get-time-zone?key={API_KEY}&format=json&by=zone&zone={zone}"
        response = requests.get(url)
        responseDict = response.json()
        timezones.append( {"name": zone, "time": responseDict["formatted"], "note": row["note"]})

    return render_template("index.html", timezones=timezones, all_timezones=all_timezones)
        

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if user exists in database
        username = request.form.get("username")
        password = request.form.get("password")

        # server-side error checking
        if username == "" or password == "":
            return apology()

        mycursor.execute("SELECT * FROM users WHERE username = (%s)", (username, ))
        rows = mycursor.fetchall()

        # no row with specified username
        if len(rows) == 0:
            print("username does not exist")
            return apology()

        # check if username and password hash are both correct
        if username == rows[0]["username"] and check_password_hash(rows[0]["pwd_hash"], password):
            session["name"] = username
            return redirect("/")
        else:
            # incorrent user credentials
            return apology()

    return render_template("login.html")

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

@app.route("/addTimezone", methods=["POST"])
def addTimezone():
    # add timezone to database for a user
    if request.method == "POST":
        zone = request.form.get("selectedZone")
        note = request.form.get("note")

        # server-side error checking
        if zone not in all_timezones:
            return apology()

        mycursor.execute("INSERT INTO usertimezones VALUES (%s, %s, %s)", (session["name"], zone, note))
        connection.commit()
        print('adding timezone:', zone)
        return redirect("/")

    return apology()

@app.route("/deleteTimezone", methods=["POST"])
def deleteTimezone():
    # delete a user's timezone from database

    zone = None
    if request.method == "POST":
        zone = request.form.get("selectedZone")

        if zone not in all_timezones:
            return apology()

        mycursor.execute("DELETE FROM usertimezones WHERE username = (%s) AND zone = (%s)", (session["name"], zone))
        connection.commit()
        print('deleteing timezone:', zone)

        return redirect("/")

    return apology()

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/")

# server side - error checking
@app.route("/apology")
def apology():
    return render_template("apology.html")