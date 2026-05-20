from . import db 
from flask_login import UserMixin 
from sqlalchemy import ForeignKey 
from datetime import datetime, timedelta 
import secrets 

class Users(db.Model,UserMixin): 
    id = db.Column(db.Integer,primary_key=True) 
    full_name = db.Column(db.String(), nullable=False)  
    email = db.Column(db.String(),unique=True, nullable=False) 
    password = db.Column(db.String(), nullable=False) 
    reset_token = db.Column(db.String(120), unique=True, nullable=True) 
    reset_token_expiration = db.Column(db.DateTime, nullable= True) 

    def generate_reset_token(self): 
        # Generate a secure random token with 32 bytes 
        self.reset_token = secrets.token_urlsafe(32) 
        self.reset_token_expiration = datetime.utcnow() + timedelta(minutes= 5) 

class UserLogin(db.Model,UserMixin): 
    id = db.Column(db.Integer,primary_key=True) 
    email = db.Column(db.String(), ForeignKey('users.email'), unique=True, nullable=False) 
    password = db.Column(db.String(), nullable=False) 

class Subscribers(db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.String(120), ForeignKey('users.email'), unique=True, nullable=False) 

class ContactUs(db.Model, UserMixin): 
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(), nullable=False) 
    email = db.Column(db.String(), ForeignKey('users.email'), nullable=False) 
    message = db.Column(db.String, nullable=False)
