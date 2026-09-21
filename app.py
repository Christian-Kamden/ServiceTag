from flask import Flask, render_template
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




if __name__ == "__main__":
        app.run(debug = True)