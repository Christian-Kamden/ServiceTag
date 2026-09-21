from flask import Flask, render_template, abort 
from database import db 
from models import User,Car,ServiceRecord


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cars.db"
db.init_app(app)

with app.app_context():
    db.create_all()




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