from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt   ## hash password
from flask_login import LoginManager
from flask_wtf import CSRFProtect
import os

import secrets
from flask_wtf import CSRFProtect

app = Flask(__name__)
csrf = CSRFProtect(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))

os.makedirs(app.instance_path, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'aristan.db')

# Uploads
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
UPLOAD_DIR_ABS = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
app.config['UPLOAD_DIR_ABS'] = UPLOAD_DIR_ABS
os.makedirs(UPLOAD_DIR_ABS, exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access the page."
login_manager.login_message_category = "warning" 

from main.models import Employee
@login_manager.user_loader
def load_user(user_id):
    return Employee.query.get(int(user_id))

with app.app_context():
    db.create_all()

from main import routes