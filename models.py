from flask_login import UserMixin
from database import db
from werkzeug.security import generate_password_hash, check_password_hash 


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(120), unique = True , nullable = False)
    phone_number = db.Column(db.String(20))
    password_hash = db.Column(db.String(200),nullable = False)

    def set_password(self,pin):
        self.password_hash = generate_password_hash(pin)

    def check_password(self,pin):
        return check_password_hash(self.password_hash, pin)


