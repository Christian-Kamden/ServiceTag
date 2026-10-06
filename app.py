from flask import Flask, render_template, abort, redirect, url_for,request,flash
from flask_login import LoginManager,login_user,logout_user,login_required,current_user
from database import db 
import os 
from dotenv import load_dotenv
from models import User,Car,ServiceRecord
from datetime import datetime


app = Flask(__name__)
load_dotenv()
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cars.db"
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

with app.app_context():
    db.create_all()

@login_manager.user_loader
def loader(user_id):
    if user_id is None or user_id == "None":
     return None

    return db.session.get(User, int(user_id))


@app.route("/")
def intro():
    return render_template("intro.html")

@app.route("/car/<token>")
def show_qr(token):
     car = Car.query.filter_by(qr_token = token).first()
     latest_service_record = ServiceRecord.query.filter_by(car_id = car.id).order_by(ServiceRecord.visit_date.desc()).first()
     if car is None:
        abort(404)
     
     if current_user.is_authenticated and current_user.id == car.owner.id:
        is_owner = True
     else:
        is_owner = False
    
     return render_template("car.html", car = car, is_owner = is_owner )

@app.route ("/car/<token>/edit", methods = ["GET","POST"])
@login_required
def edit(token):
    car = Car.query.filter_by(qr_token=token).first()
    if car is None:
        abort(404)
    if car.owner_id != current_user.id:
        abort(403)
    if request.method == "POST":
        car.show_contact = request.form.get("show_contact") == "on"
        car.for_sale = request.form.get("for_sale") == "on"
        car.description = request.form["description"]
        db.session.commit()
        flash("saved","success")
        return redirect(url_for("edit", token=token))
    return render_template("edit_car.html", car=car)

@app.route("/signup",methods = ["GET","POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].lower().strip()
        if User.query.filter_by(email = email).first():
            flash("This E-mail Is Already Registered","error")
            return redirect(url_for("signup"))
        phone = request.form.get("phone_number")
        password = request.form["password"]
        if len(password) < 8:
            flash("Password must be atleast 8 character","error")
            return redirect(url_for("signup"))
        user = User(email = email, name = name, phone_number = phone)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("intro"))
    return render_template("signup.html")


@app.route("/login", methods = ["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower().strip()
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash("Email or Password is incorrect, Try again")
            return render_template("login.html")
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("intro"))
    return render_template("login.html")


@app.route("/register_car", methods = ["GET","POST"])
@login_required
def reg():
    if request.method == "POST":
        make = request.form["make"]
        model = request.form["model"]
        year = (int(request.form["year"]))
        last_service_date = request.form["last_service_date"]
        last_service_date = datetime.strptime(last_service_date,"%Y-%m-%d").date()
        vin = request.form["vin"]
        access_code = request.form["access_code"]
        if Car.query.filter_by(vin=vin).first():
            flash("This VIN number already exsists","error")
            return render_template("register_car.html")
        car = Car(owner_id=current_user.id, make=make, model=model, year=year, vin=vin, last_service_date=last_service_date)
        car.set_access_code(access_code)
        db.session.add(car)
        db.session.commit()
        return redirect(url_for("show_qr", token=car.qr_token))
    return render_template("register_car.html")



@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("intro"))



if __name__ == "__main__":
    app.run(debug = True)

