from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf import CSRFProtect
import os

app = Flask(__name__)

# SECRET KEY + DB (adjust to your paths as needed)
app.config['SECRET_KEY'] = 'replace-with-a-strong-secret'
os.makedirs(app.instance_path, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'aristan.db')

# Uploads
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['UPLOAD_DIR_ABS'] = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
os.makedirs(app.config['UPLOAD_DIR_ABS'], exist_ok=True)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access the page."
csrf = CSRFProtect(app)   # ✅ Global CSRF

from main.models import Employee  # after db
@login_manager.user_loader
def load_user(user_id):
    return Employee.query.get(int(user_id))

with app.app_context():
    db.create_all()

from main import routes  # import routes last
