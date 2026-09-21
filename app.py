from flask import Flask, render_template, abort 
from flask_login import LoginManager
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


if __name__ == "__main__":
    app.run(debug = True)

