from flask import Flask, session, render_template, request, redirect
from flask_session import Session

# "flask --debug run" to enable reload on save

# configure app
app = Flask(__name__)

# configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    # should display users list validated by cookies, else redirect to login page

    if not session.get("name"): # use .get else session["name"] will cause error because no session is present
        return redirect("/login")

    print("index", session['name'])
    return render_template("index.html")
        

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print(username, password)

        session["name"] = username
        # print(session['name'])

        return redirect("/")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # validate user's password
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