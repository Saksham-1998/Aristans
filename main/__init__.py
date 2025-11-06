from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt   ## hash password
from flask_login import LoginManager
import os

app = Flask(__name__)


os.makedirs(app.instance_path, exist_ok=True)   ## instance folder exist
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'aristan.db')  ## db in instance
app.config['SECRET_KEY'] = '1d11684039c257cb8d2f9b69'


db = SQLAlchemy(app)
bcrypt= Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'        ## without access it will lead to login page
login_manager.login_message = "Please log in to access the page."



from main.models import Employee

@login_manager.user_loader
def load_user(user_id):
    return Employee.query.get(int(user_id))

with app.app_context():
    db.create_all()
    print("DB path:", app.config['SQLALCHEMY_DATABASE_URI']) ##path of db


from main import routes