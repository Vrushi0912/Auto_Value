from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager 
import secrets 
import hashlib 
import os 
from os import path 

db = SQLAlchemy() 
DB_NAME = "AutoValue.db" 

def generate_secret_key(length=32): 
    return secrets.token_hex(length // 2) 

def hash_secret_key(secret_key): 
    sha256 = hashlib.sha256() 
    sha256.update(secret_key.encode('utf-8')) 
    return sha256.hexdigest() 

from dotenv import load_dotenv
load_dotenv()

def create_app(): 
    app = Flask(__name__) 
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-do-not-use-in-production") 

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}" 
    db.init_app(app) 

    from .Views import views 
    from .Authentication import auth 

    app.register_blueprint(views,url_prefix="/") 
    app.register_blueprint(auth,url_prefix="/") 

    from .models import Users 

    create_database(app) 

    login_manager = LoginManager() 
    login_manager.login_view = 'auth.login' 
    login_manager.init_app(app) 

    @login_manager.user_loader 
    def load_user(id): 
        return Users.query.get(int(id)) 

    return app 

def create_database(my_app): 
    if not path.exists("website/"+DB_NAME): 
        with my_app.app_context():
            db.create_all() 
        print("Database Created!")
