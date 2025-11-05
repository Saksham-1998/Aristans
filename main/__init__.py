from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)


os.makedirs(app.instance_path, exist_ok=True)   ## instance folder exist
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'aristan.db')  ## db in instance
app.config['SECRET_KEY'] = '1d11684039c257cb8d2f9b69'


db = SQLAlchemy(app)

from main.models import Employee
with app.app_context():
    db.create_all()
    print("DB path:", app.config['SQLALCHEMY_DATABASE_URI']) ##path of db


from main import routes