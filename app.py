from flask import Flask 
from database import db 
from models import User,Car

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cars.db"
db.init_app(app)

with app.app_context():
    db.create_all()