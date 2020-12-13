from flask import Flask, render_template, request, redirect, session, logging, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_mail import Mail
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin
import os
import time
import json
from passlib.hash import sha256_crypt

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True

engine = create_engine("mysql+pymysql://root:@localhost/queue")
db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail_user'],
    MAIL_PASSWORD=params['gmail_password']
)
mail = Mail(app)

@app.route("/")
def home():
    return render_template('index.html', params=params)


@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        Name = request.form.get("Name")
        Username = request.form.get("Username")
        Phone = request.form.get("Phone")
        Password = request.form.get("Password")
        secure_password = sha256_crypt.encrypt(str(Password))
        db.execute("INSERT INTO registration(Name,Username,Phone,Password) VALUES(:Name,:Username,:Phone,:Password)",
                   {"Name": Name, "Username": Username, "Phone": Phone, "Password": secure_password})
        db.commit()
        flash("You are registered and can login", "success")
        return redirect(url_for('login', params=params))

    return render_template('registration.html', params=params)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        Username = request.form.get("Username")
        Password = request.form.get("Password")

        Usernamedata = db.execute("SELECT Username FROM registration WHERE Username=:Username", {"Username": Username}).fetchone()
        Passwordata = db.execute("SELECT Password FROM registration WHERE Username=:Username", {"Username": Username}).fetchone()

        if Usernamedata is None:
            return render_template("login.html")
        else:
            for Passwor_data in Passwordata:
                if sha256_crypt.verify(Password, Passwor_data):
                    session["log"] = True
                    return redirect(url_for('information', params=params))
                else:
                    return render_template("login.html", params=params)

    return render_template('login.html', params=params)

@app.route("/admindashboard", methods=["GET", "POST"])
def admindashboard():
    if request.method == "POST":
        Username = request.form.get("Username")
        Password = request.form.get("Password")

        if (Username == params['admin_user'] and Password == params['admin_pass']):
            session["log"] =True

            flash("Successfully logged in", "success")
            return render_template('admindashboard.html', params=params)
        else:
            flash("Invalid Username or Password", "danger")
            return render_template('adminlogin.html', params=params)

    else:
        if 'log' in session:
            return render_template('admindashboard.html', params=params)

        else:
            return render_template('adminlogin.html', params=params)

@app.route("/information")
def information():
    if 'log' in session:
        return render_template('information.html', params=params)
    else:
        return redirect(url_for('login', params=params))

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        Name = request.form.get("Name")
        Email = request.form.get("Email")
        Subject = request.form.get("Subject")
        Message = request.form.get("Message")
        db.execute("INSERT INTO contact(Name,Email,Subject,Message) VALUES(:Name,:Email,:Subject,:Message)",
                   {"Name": Name, "Email": Email, "Subject": Subject, "Message": Message})
        db.commit()
        mail.send_message('New message from ' + Name,
                          sender=Email,
                          recipients=[params['gmail_user']],
                          body=Message
                          )

    return render_template('index.html', params=params)

@app.route("/adminlogout")
def adminlogout():
    session.clear()
    flash("You are successfully logged out", "success")
    return redirect(url_for('home', params=params))

@app.route("/logout")
def logout():
    session.clear()
    flash("You are successfully logged out", "success")
    return redirect(url_for('home', params=params))

@app.route("/user")
def user():
    return render_template('user.html', params=params)


if __name__ == "__main__":
    app.run(debug=True)