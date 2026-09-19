from flask import Flask 
from database import db 
from models import User,Car
from datetime import date 

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cars.db"
db.init_app(app)

with app.app_context():
    db.create_all()

    kamden = User(name = "Kamden" ,email = "kamdenexample@gmail.com")
    kamden.set_password("testpassword")
    db.session.add(kamden)
    db.session.commit()

    print(kamden.password_hash)
    print(kamden.check_password("kamden"))
    print(kamden.is_authenticated)

    car = Car(owner_id = kamden.id, last_service_date = date(2024, 5, 1),make = "hyundai", model = "accent", year = 2019, vin = "02H25K36L25DGK45I")
    car.set_access_code("test")
    db.session.add(car)
    db.session.commit()
   
    print(car.qr_token)
    print(car.failed_attempts)
    print(car.owner.name)
