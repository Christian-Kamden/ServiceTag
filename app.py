from flask import Flask, render_template, abort, redirect, url_for,request,flash
from flask_login import LoginManager,login_user,logout_user,login_required
from database import db 
import os 
from dotenv import load_dotenv
from models import User,Car,ServiceRecord


app = Flask(__name__)
load_dotenv()
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cars.db"
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def loader(user_id):
    return db.session.get(User, int(user_id))


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/car/<token>")
def show_qr(token):
     car = Car.query.filter_by(qr_token = token).first()
     if car is None:
        abort(404)
     return render_template("car.html", car = car )

@app.route("/signup",methods = ["GET","POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].lower().strip()

        if User.query.filter_by(email = email).first():
            flash("This E-mail Is Already Registered","error")
            return render_template("signup.html")
        
        phone = request.form.get("phone_number")

        password = request.form["password"]
        if len(password) < 8:
            flash("Password must be atleast 8 character","error")
            return render_template("home")
        
        user = User(email = email, name = name, phone_number = phone)
        user.set_password(password)
    
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("home"))

    
    return render_template("/home.html")


@app.route("/login", methods = ["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower().strip()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash("Email or Password is incorrect, Try again")
            return render_template("login.html")

        login_user(user)
        return redirect(url_for("home"))

    return render_template("login.html")

    
    
    



if __name__ == "__main__":
    app.run(debug = True)

