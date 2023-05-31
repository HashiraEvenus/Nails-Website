import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date

from helpers import apology, login_required

#configure application
app = Flask(__name__)

#ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)

#Configure cs50 library to use sql database
db = SQL("sqlite:///nails.db")


# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/login",methods=["GET","POST"])
def login():
    """Log in user"""

    # Forget any user_id
    session.clear()

    # User reached route via post (as by submitting the log-in form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username",400)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("Must provide password",400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username=?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username and/or password",403)

        # Remember which user has logged in
        session["user_id"]=rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
@app.route("/logout")
def logout():
    """Log out"""
    #Forget any id
    session.clear()

    #redirect user to login form
    return redirect("/")

@app.route("/contact", methods=["GET"])
@login_required
def contact():
    return render_template("contact.html")

@app.route("/", methods=["GET","POST"])
@login_required
def index():
    db.execute("CREATE TABLE IF NOT EXISTS user_appt (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER, date DATE, FOREIGN KEY(user_id) REFERENCES users(id))")
    appts = db.execute("SELECT * FROM user_appt where user_id=?",session["user_id"])
    today = date.today()
    if request.method=="POST":
        id=request.form.get("id")
        db.execute("DELETE FROM user_appt WHERE id=?",int(id))
        return redirect("/")
    return render_template("index.html", appts=appts, today=str(today))

@app.route("/about", methods=["GET"])
@login_required
def about():
    return render_template("about.html")


@app.route("/appointment", methods=["GET","POST"])
@login_required
def appointment():
    if request.method=="POST":
        date = request.form.get("date")
        time = request.form.get("hours")

        #INSERT the time and date on database
        if date and time:
            db.execute("INSERT INTO user_appt(user_id, time,date) VALUES(?,?,?)",session["user_id"],time,date)


        else:
            return apology("You did not input DATE or hours",400)
        return redirect("/")

    else:
        return render_template("appointment.html")



@app.route("/register", methods=["GET","POST"])
def register():
    """Register User"""
    if request.method=="POST":
        #Ensure username was provided
        if not request.form.get("username"):
            return ("error")
        elif not request.form.get("name"):
            return("Please insert a name")
         #Ensure password was provided
        elif not request.form.get("password"):
            return ("Please insert password")
        #Ensure verification password was provided
        elif not request.form.get("confirmation"):
            return ("Please confirm password")
        #Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return ("The password needs to be matching")
        #Ensure email was provided
        elif not request.form.get("email"):
            return ("Please insert e-mail")
        username=request.form.get("username")
        password=request.form.get("password")
        email=request.form.get("email")
        name=request.form.get("name")
        rows=db.execute("SELECT username FROM users WHERE username=?",username)
        if len(rows)==1:
            return ("Username already exists")
        else:
            hash=generate_password_hash(password)
            db.execute("INSERT INTO users(username, hash, email, name) VALUES (?,?,?,?)", username, hash, email, name)

    return render_template("register.html")



