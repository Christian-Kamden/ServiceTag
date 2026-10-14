from flask import Flask, render_template, abort, redirect, url_for,request,flash,Response,session
from flask_login import LoginManager,login_user,logout_user,login_required,current_user
from database import db 
import os 
from dotenv import load_dotenv
from models import User,Car,ServiceRecord
from datetime import datetime,timedelta
import qrcode
import io


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


@app.context_processor
def inject_has_cars():
    if current_user.is_authenticated:
        has_cars = Car.query.filter_by(owner_id=current_user.id).first() is not None
    else:
        has_cars = False
    return dict(has_cars=has_cars)


@app.route("/car/<token>", methods=["GET","POST"])
def show_qr(token):
    car = Car.query.filter_by(qr_token=token).first()
    if car is None:
        abort(404)
    latest_service_record = ServiceRecord.query.filter_by(car_id=car.id).order_by(ServiceRecord.visit_date.desc()).first()
    service_history = ServiceRecord.query.filter_by(car_id=car.id).order_by(ServiceRecord.visit_date.desc()).all()

    is_owner = current_user.is_authenticated and current_user.id == car.owner.id

    if car.locked_until and car.locked_until > datetime.now():
        flash("This car is temporarily locked due to too many incorrect attempts","Error")
        mechanic_unlocked = False
    else:
        unlocked_cars = session.get("unlocked_cars",[])
        mechanic_unlocked = car.id in unlocked_cars
        if request.method == "POST":
            submitted_code = request.form.get("access_code")

            if car.check_access_code(submitted_code):
                if car.id  not in unlocked_cars:
                    unlocked_cars.append(car.id)
                    session["unlocked_cars"] = unlocked_cars
                mechanic_unlocked = True
                car.failed_attempts = 0
                db.session.add(car)
                db.session.commit()
            else:
                car.failed_attempts += 1
                if car.failed_attempts >= 3:
                    car.locked_until = datetime.now() + timedelta(minutes=5)
                    flash("Too many failed attempts. Please try again later","Error")
                else:
                    flash("Incorrect Access Code", "error")

                db.session.add(car)
                db.session.commit()
            return redirect(url_for("show_qr",token=token))
    return render_template("car.html",
                            car=car,
                            is_owner=is_owner,
                            latest_service_record=latest_service_record,
                            service_history=service_history,
                            mechanic_unlocked=mechanic_unlocked)


@app.route ("/car/<token>/edit", methods = ["GET","POST"])
@login_required
def edit(token):
    car = Car.query.filter_by(qr_token=token).first()
    if car is None:
        abort(404)
    if car.owner_id != current_user.id:
        abort(403)
    if request.method == "POST":
        car.show_contact = "show_contact" in request.form
        car.for_sale =  "for_sale" in request.form
        car.mechanic_full_access = "mechanic_full_access" in request.form
        car.description = request.form["description"]
        db.session.commit()
        flash("saved","success")
        return redirect(url_for("show_qr", token=token))
    return render_template("edit_car.html", car=car)


@app.route("/car/<token>/add_record", methods= ["GET", "POST"])
def add_record(token):
    car = Car.query.filter_by(qr_token=token).first()
    if car is None:
        abort(404)
    is_owner = current_user.is_authenticated and current_user.id == car.owner.id
    mechanic_access = car.id in session.get("unlocked_cars",[])
    if not is_owner and not mechanic_access:
        abort(403)
    if request.method == "POST":
        mechanic = request.form["mechanic"]
        description = request.form.get("description")
        odo_reading = int(request.form["odo_reading"])
        visit_date = datetime.strptime(request.form["visit_date"], "%Y-%m-%d").date()
        store = request.form["store"]
        record = ServiceRecord(car_id=car.id,
                               mechanic=mechanic,
                               description=description,
                               odo_reading=odo_reading,
                               visit_date=visit_date,
                               store=store)
        db.session.add(record)
        db.session.commit()
        flash("service Record Added","success")
        return redirect(url_for("show_qr", token=token))
    return render_template("add_record.html", car=car)

@app.route("/car/<token>/delete" ,methods=["POST","GET"])
@login_required
def delete(token):
    car = Car.query.filter_by(qr_token=token).first()
    if car is None:
        abort(404)
    if car.owner_id != current_user.id:
        abort(403)

    if request.method == "POST":
        db.session.delete(car)
        db.session.commit()
        flash("Car deleted","success")
        remaining_car = Car.query.filter_by(owner_id=current_user.id).first()
        if remaining_car is None:
            return redirect(url_for("intro"))
        else:
            return redirect(url_for("my_cars"))
    return render_template("delete_car.html", car=car)
    

@app.route("/car/<token>/qr", methods = ["GET"])
def generate_qr(token):
    car = Car.query.filter_by(qr_token=token).first()
    if car is None:
        abort(404)
    else:
        qr_url = f"{request.host_url}car/{token}"
        img = qrcode.make(qr_url)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return Response(buffer.getvalue(), mimetype="image/png")
        

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
            return redirect(url_for("login"))
        login_user(user)
        return redirect(url_for("intro"))
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("intro"))


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
        car = Car(owner_id=current_user.id, 
                  make=make, 
                  model=model, 
                  year=year, 
                  vin=vin, 
                  last_service_date=last_service_date)
        
        car.set_access_code(access_code)
        db.session.add(car)
        db.session.commit()
        return redirect(url_for("show_qr", token=car.qr_token))
    return render_template("register_car.html")

@app.route("/my_cars")
@login_required
def my_cars():
    user_cars = Car.query.filter_by(owner_id=current_user.id).all()
    return render_template("my_cars.html", cars=user_cars)


if __name__ == "__main__":
    app.run(debug = True)

