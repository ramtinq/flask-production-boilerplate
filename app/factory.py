from flask import Flask, request, jsonify
import os
import jwt
from urllib.parse import quote_plus

if os.getenv("FLASK_ENV") != "production":
    from dotenv import load_dotenv
    if os.getenv("FLASK_ENV") == 'local':
        load_dotenv('.env.local', override=True)
    else:
        load_dotenv()

from .extensions import db, migrate, login_manager, bcrypt, csrf
from .utils import extract_app_token

def create_app(is_worker:bool = False):

    print("\n\nCreating new Flask app instance...\n\n")
    
    app = Flask(__name__, template_folder='templates')

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql://{os.getenv('MYSQL_USER')}:"
        f"{quote_plus(os.getenv('MYSQL_PASSWORD'))}"
        f"@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/"
        f"{os.getenv('MYSQL_DB')}"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    #celery.conf.update(app.config)

    db.init_app(app)
    migrate.init_app(app, db)

    if(is_worker):
        return app

    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.user_login_get'

    from app.blueprints.auth.models import User

    @login_manager.user_loader
    def load_user(uid):
        return db.session.get(User, int(uid))
    
    bcrypt.init_app(app)


    @app.before_request
    def verify_is_our_app():
        # ! Not secure. People can read the specific key from the frontend.
        # Just a guard making it harder for thid-parties to consume the API.
        if not request.path.startswith('/api'):
            return

        client_token = extract_app_token(request.headers.get("X-Auth", ""))

        if not client_token:
            return jsonify({"error": "Unauthorized action."}), 401
        
        try:
            jwt.decode(client_token, app.config["APP_VERIFICATION_SECRET"], algorithms=["HS256"])
        except jwt.PyJWTError:
            return jsonify({"error": "Unauthorized action."}), 401
    
    from app.blueprints.core import core_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.calculations import calculations_bp

    app.register_blueprint(core_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(calculations_bp)


    return app