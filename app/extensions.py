from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

csrf: CSRFProtect = CSRFProtect()
db: SQLAlchemy = SQLAlchemy()
login_manager: LoginManager = LoginManager()
bcrypt: Bcrypt = Bcrypt()
migrate: Migrate = Migrate()