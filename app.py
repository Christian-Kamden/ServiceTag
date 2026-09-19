from flask import Flask 
from database import db 
from models import User

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cars.db"
db.init_app(app)

with app.app_context():
    db.create_all()

    kamden = User(name = "Kamden" ,email = "kamdenexample@gmail.com")
    kamden.set_password("testpassword")
    print(kamden.password_hash)
    print(kamden.check_password("kamden"))
    print(kamden.is_authenticated)