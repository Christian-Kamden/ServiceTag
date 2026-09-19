from flask_login import UserMixin
from database import db
from werkzeug.security import generate_password_hash, check_password_hash 
import secrets

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(120), unique = True , nullable = False)
    phone_number = db.Column(db.String(20))
    password_hash = db.Column(db.String(200),nullable = False)
    cars = db.relationship("Car", backref = "owner")
    
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

class Car(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    make = db.Column(db.String(100),nullable = False)
    model = db.Column(db.String(100), nullable = False)
    year = db.Column(db.Integer,nullable = False)
    vin = db.Column(db.String(17), unique =True ,nullable = False)
    last_service_date = db.Column(db.Date(),nullable = False)
    qr_token = db.Column(db.String(32),unique =True, nullable =False,default = lambda: secrets.token_urlsafe(16))
    failed_attempts = db.Column(db.Integer,nullable = False, default = 0 )
    locked_until = db.Column(db.DateTime)
    access_code_hash = db.Column(db.String(200), nullable = False)

    def set_access_code(self,access_code):
        self.access_code_hash = generate_password_hash(access_code)

    def check_access_code(self,access_code):
        return check_password_hash(self.access_code_hash,access_code)