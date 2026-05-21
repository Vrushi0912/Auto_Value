import random 
import time 
from flask import Blueprint, flash,render_template,request,jsonify,redirect,url_for, make_response, session 
from werkzeug.security import generate_password_hash, check_password_hash 
from .models import Users, UserLogin 
from .models import Subscribers, ContactUs 

from . import db 
from flask_login import login_user,login_required,logout_user, current_user 
from email.message import EmailMessage 
import ssl 
import smtplib 

from datetime import datetime, timedelta 
import os
auth = Blueprint("auth",__name__) 

@auth.route("/login",methods=["GET","POST"]) 
def login(): 
    if request.method == "POST": 
        email = request.form.get("email") 
        password = request.form.get("password") 
         
        # query UserLogin model 
        user = UserLogin.query.filter_by(email=email).first() 
        if not user: 
            flash("Email Address is not Registered.",category="error") 
        elif not check_password_hash(user.password, password):  
            flash("Incorrect Password, try again.",category="error") 
        else: 
            login_user(user, remember=True) 
            session['user_id'] = user.id 
            return redirect(url_for("views.landing_page")) 
    return render_template("login.html") 

@auth.route("/update-profile", methods=["POST"]) 
def update_profile(): 
    if request.method == "POST": 
        data = request.json  # Retrieve JSON data from the request 
        new_full_name = data.get('full_name')  
        user_id = session.get("user_id") 
        current_user = Users.query.filter_by(id=user_id).first() 
        current_user.full_name = new_full_name 
        db.session.commit() 
        return jsonify({"message":"Profile Updated!"}) 

@auth.route("/logout",methods=["POST","GET"]) 
@login_required 
def logout(): 
    logout_user() 
    # Create a response object 
    response = make_response(redirect(url_for('auth.login'))) 
    # Set Cache-Control headers to prevent caching 
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate' 
    response.headers['Pragma'] = 'no-cache' 
    response.headers['Expires'] = '0' 
    return response  



@auth.route("/sign-up",methods=["GET","POST"]) 
def sign_up(): 
    if request.method == "POST": 
        full_name = request.form.get("fullName") 
        email = request.form.get("email") 
        user = Users.query.filter_by(email=email).first() 
        if user: 
            flash("Email Address is already Registered.",category="error") 
        elif len(full_name) <= 5: 
            flash("Full Name should be more than 5 characters.",category="error") 
        elif len(email) <= 5: 
            flash("Invalid email address",category="error") 
        else: 
            email_sender = os.environ.get('EMAIL_USER', 'autovaluesup@gmail.com') 
            email_password = os.environ.get('EMAIL_PASS', '') 
            email_receiver = email 
             
            subject = 'OTP FOR EMAIL VERIFICATION' 
            otp = str(random.randint(100000, 999999)) 
            session['otp'] = otp
            session['otp_timestamp'] = time.time()
          
            body = f"<b>OTP: {otp}</b>. <b>Your OTP expires in 5 minutes.</b>" 
            email_message = EmailMessage() 
            email_message['From'] = 'AutoValue Support'
            email_message['To'] = email_receiver 
            email_message['Subject'] = subject 
            email_message.set_content(body, subtype="html") 

            context = ssl.create_default_context() 

            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context, timeout=10) as smtp: 
                    smtp.login(email_sender, email_password) 
                    smtp.sendmail(email_sender, email_receiver, email_message.as_string())  
            except Exception as e:
                print(f"Failed to send email: {e}")
                print(f"--- DEMO MODE OTP ---")
                print(f"OTP for {email}: {otp}")
                print(f"---------------------")

            session['email'] = email 
            session['fullName'] = full_name 
             
            flash("Enter the OTP provided in the Email (or check the console). OTP expires in 5 minutes." , category="success") 
            return redirect(url_for("auth.verify_email_otp")) 
    return render_template("signup.html") 

@auth.route("/verify-email",methods=['GET','POST']) 
def verify_email_otp(): 
    email = session.get('email') 
    if request.method == 'POST': 
        entered_otp = request.form.get('otp') 
        stored_otp = session.get('otp')
        stored_timestamp = session.get('otp_timestamp')
        if stored_otp and stored_otp == entered_otp: 
            if time.time() - stored_timestamp <= 300: 
                session['email'] = email 
                session.pop('otp', None)
                session.pop('otp_timestamp', None)
                flash("Email has been verified! Set your Password.", category="success") 
                return redirect('/set-password') 
            else: 
                session.pop('otp', None)
                session.pop('otp_timestamp', None)
                session.pop('email',None) 
                flash("OTP has expired!", category="expire-error") 
                return render_template('verify_email.html') 
        else: 
            flash("OTP entered is Invalid! Enter correct OTP.", category="invalid-error") 
            return render_template('verify_email.html') 
    return render_template('verify_email.html', email=email) 

@auth.route("/set-password",methods=['GET','POST']) 
def set_password(): 
    if request.method == "POST": 
        full_name = session.get("fullName") 
        email = session.get("email") 
        password = request.form.get("password") 
        cpassword = request.form.get("cpassword") 

        if password != cpassword: 
            flash("Passwords do not match.",category="error") 
        else: 
            hashed_password = generate_password_hash(password) 
            new_user = Users(full_name=full_name,email=email,password=hashed_password)  
            db.session.add(new_user) 
            new_user_login = UserLogin(email=email, password=hashed_password)  
            db.session.add(new_user_login) 
            db.session.commit() 
            session.pop('email',None) 
            flash("Successfully Signed Up! You can now Log in.", category="success") 
            return redirect(url_for("auth.login")) 
    return render_template("set_password.html") 

@auth.route("/forgot-password",methods=['GET','POST']) 
def forgot_password(): 
    email_sender = os.environ.get('EMAIL_USER', 'autovaluesup@gmail.com') 
    email_password = os.environ.get('EMAIL_PASS', '')
    if request.method == "POST": 
        email = request.form.get("email") 
        user = Users.query.filter_by(email=email).first() 
        if not user: 
            flash("Email Address is not Registered.",category="error") 
        else: 
            user.generate_reset_token() 
            db.session.commit() 
            email_receiver = email 
            subject = 'Password Reset Request' 
            reset_link = url_for('auth.reset_password', token=user.reset_token, _external=True) 
            body = f"<b>Click on the link to reset your password. Link is valid for 5 minutes.</b><br><br><b>Password reset link:</b> {reset_link}" 
            email_message = EmailMessage() 
            email_message['From'] = 'AutoValue Support'
            email_message['To'] = email_receiver 
            email_message['Subject'] = subject 
            email_message.set_content(body, subtype='HTML') 

            context = ssl.create_default_context() 
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context, timeout=10) as smtp: 
                    smtp.login(email_sender, email_password) 
                    smtp.sendmail(email_sender, email_receiver, email_message.as_string())  
            except Exception as e:
                print(f"Failed to send email: {e}")
                print(f"--- DEMO MODE PASSWORD RESET ---")
                print(f"Reset Link: {reset_link}")
                print(f"--------------------------------")
            flash('Email sent successfully! Check your inbox (or console).', category="success") 
    return render_template("forgot_password.html") 

@auth.route('/reset-password',methods=['GET','POST']) 
def reset_password(): 
    if request.method == "POST": 
        token = request.args.get('token') 
        new_password = request.form.get('password') 
        confirm_password = request.form.get("cpassword") 
        user = Users.query.filter_by(reset_token=token).first() 
        if (user and user.reset_token_expiration and 
user.reset_token_expiration > datetime.utcnow() and new_password == confirm_password): 
            user_login = UserLogin.query.filter_by(email=user.email).first() 
            hashed_new_password = generate_password_hash(new_password) 
            user.reset_token = None 
            user.reset_token_expiration = None 
            user.password = hashed_new_password 
            user_login.password = hashed_new_password 
            db.session.commit() 
            flash("Password reset successfully!", category="reset-success") 
        else: 
            user.reset_token = None 
            user.reset_token_expiration = None 
            flash('Token has been expired.', category='reset-error') 
    return render_template("reset_password.html") 

@auth.route('/subscribe', methods=['POST']) 
def subscribe(): 
    email = request.form['email-input'] 
    user = Users.query.filter_by(email=email).first() 
    user_id = "" 
    if user: 
        user_id = user.id 
    if user and session.get('user_id') == user.id: 
        existing_subscriber = Subscribers.query.filter_by(email=email).first()  
        if existing_subscriber: 
            return jsonify({'message': 'You have already subscribed!'}) 
        else: 
            subscriber = Subscribers(email=email) 
            db.session.add(subscriber) 
            db.session.commit() 
            return jsonify({'message': 'You have successfully subscribed!'}) 
    else: 
        return jsonify({'message': 'Invalid Email Address!'}) 

@auth.route('/contact', methods=['POST']) 
def contact(): 
    client_name = request.form['client-name'] 
    client_email = request.form['client-email'] 
    client_message = request.form['client-message'] 
    user = Users.query.filter_by(email=client_email).first() 
    user_id = "" 
    if user: 
        user_id = user.id 
    if user and session.get("user_id") == user_id: 
        try: 
            contact_msg = ContactUs(name=client_name, email=client_email, message=client_message) 
            db.session.add(contact_msg) 
            db.session.commit() 
            return jsonify({'message': 'Message sent successfully!'}) 
        except Exception as e: 
            return jsonify({'message': 'Error occurred!'}) 
    else: 
        return jsonify({'message': 'Invalid Email Address!'}) 
