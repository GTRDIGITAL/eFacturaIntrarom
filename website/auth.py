from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import Users
from . import db 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import random
import smtplib
import ssl
import datetime
import pyotp
import smtplib, ssl
import base64
from .trimitereCodOTP import trimitereOTPMail
from . import refreshToken
import json
from datetime import timedelta

auth = Blueprint('auth', __name__)
def trimitereMail():
    smtp_server = "smtp.office365.com"
    port = 587  # Pentru starttls
    sender_email = "cristian.iordache@ro.gt.com"
    password = "Bucuresti_123321+"
    context = ssl.create_default_context()
    message_text = "Yaaaaay\n\nThank you,\nGTRDigital"
    
    date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    subj = "Cod OTP " + str(date)
    mailTo = "cristian.iordache@ro.gt.com"

    
    boundary = "MY_BOUNDARY"

    msg = f"""\
From: {sender_email}
To: {mailTo}
Subject: {subj}
Date: {date}
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary={boundary}

--{boundary}
Content-Type: text/plain; charset="utf-8"

{message_text}

--{boundary}
Content-Type: application/octet-stream


--{boundary}--
"""

    # Încercați să vă conectați la server și să trimiteți e-mailul
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo() # Poate fi omis
        server.starttls(context=context) # Asigură conexiunea
        server.ehlo() # Poate fi omis
        server.login(sender_email, password)
        server.sendmail(sender_email, mailTo, msg)
    except Exception as e:
        print(e)
    finally:
        server.quit()
        
        
SESSION_TIMEOUT = 60  # 1 minute in seconds

# Helper function to reset session timeout
def reset_session_timeout():
    session['last_activity'] = datetime.datetime.now()

@auth.before_request
def before_request():
    if current_user.is_authenticated:
        # Reset session timeout on every request
        reset_session_timeout()

        # Check if session has expired
        last_activity = session.get('last_activity')
        if last_activity is not None:
            elapsed_time = datetime.datetime.now() - last_activity
            if elapsed_time.total_seconds() > SESSION_TIMEOUT:
                logout_user()
                flash('Session expired. Please log in again.', category='error')
                return redirect(url_for('auth.login'))

@auth.route('/', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')
        print("trece pe aici")
        
        def citeste_configurare(file_path):
            with open(file_path, 'r') as file:
                config = json.load(file)
            return config

        config = citeste_configurare('config.json')
        appData = config['dateFirma']
        
        user = Users.query.filter_by(username=email).first()
        
        if user:
            if check_password_hash(user.password, password):
                session['email'] = email
                login_user(user, remember=True)
                print(user)
                key = pyotp.random_base32()
                totp = pyotp.TOTP(key)
                cod = totp.now()
                trimitereOTPMail(cod, email)
                print("ACESTA ESTE CODUL: ", cod)
                session['cod'] = cod
                data_acum = datetime.datetime.now()
                data_acum_formatata = data_acum.strftime("%Y-%m-%d")
                
                token_time = config["dateFirma"]["data_token"]
                token_time_obiect = datetime.datetime.strptime(token_time, "%Y-%m-%d %H:%M:%S")

                token_time_formatata = token_time_obiect.strftime("%Y-%m-%d")
                
                data_acum_obiect = datetime.datetime.strptime(data_acum_formatata, "%Y-%m-%d")
                token_time_obiect = datetime.datetime.strptime(token_time_formatata, "%Y-%m-%d")

                # Calcularea diferenței de timp
                diferenta = data_acum_obiect - token_time_obiect
                print('diferenta ', diferenta)

                # Verificarea dacă diferența este mai mare de 70 de zile. pentru test punem -1
                if diferenta > timedelta(days=70):  
                    refreshToken.refreshToken()   
                
                return redirect(url_for('views.verify'))
            
            else:
                flash('incorrect password', category='error')
        else:
            flash('email does not exist', category='error')
        
    return render_template("auth.html", user = current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
# @login_required
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        user = Users.query.filter_by(username=email).first()
        if user:
            flash('user already exist', category='error')
        if len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 2:
            flash('Password must be at least 2 characters.', category='error')
        else:
            new_user = Users(username=email, password=generate_password_hash(
                password1, method='sha256'), token='12321321321')
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("account created", category='success')
            return redirect(url_for('views.main'))
            
    return render_template("signup.html", user=current_user)