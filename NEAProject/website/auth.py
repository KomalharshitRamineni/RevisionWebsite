from flask import Blueprint, render_template, request, flash, redirect, url_for,current_app
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Mail,Message
from itsdangerous import URLSafeTimedSerializer
import sqlite3
from .models import User

auth = Blueprint('auth', __name__)

s=URLSafeTimedSerializer('asilrgkjhsdf')


@auth.route('/')
def welcome():  
    if current_user == None:
        return render_template("welcomePage.html",user=None)
    else:
        #If the user lands on this page and is logged in then they are logged out
        logout_user()
        return render_template("welcomePage.html",user=None)



@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('ResetPassword') == 'Reset Password':
            #If the user requests to reset password
            email = request.form.get('email')
            #form data is recieved
            if email == '':
                flash('Please enter an email',category='error')
                return render_template("login.html", user=None)
                #If form data is invalid then error message is displayed
            else:     
                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()

                cursor.execute("SELECT * from User WHERE Email = ?",(email,))
                
                results = cursor.fetchall()
                connection.close()
                #Information associated with email entered is checked
                if len(results) == 0:
                    #If there are no results from the query then error message is displayed
                    flash('Account does not exist with email given!',category='error')
                    return render_template("login.html", user=None)

                else:

                    with current_app.app_context():
                        token = s.dumps(email,salt='email-confirm')
                        mail = Mail(current_app)
                        msg = Message('Change Password Link', recipients=[email])
                        link = url_for('profileSection.confirm_change_password',token=token,_external=True)
                        msg.body = 'Your link is {}'.format(link)
                        mail.send(msg)
                        #If an account does exist with the email entered then a link to reset password is sent to their email
                        flash('Link to reset password sent to email',category='success')
                        return redirect(url_for('auth.login'))

        if request.form.get('Login') == 'Login':
            #If the user attempts to login
            email = request.form.get('email')
            password = request.form.get('password')
            #form data is recieved
            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()

            cursor.execute("SELECT * from User WHERE Email = ?",(email,))
            results = cursor.fetchall()
            connection.close()
            #Information associated with email entered is checked

            if len(results) != 0:
                #If the account does exist
                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()

                cursor.execute("SELECT Password,UserID,FirstName,EmailConfirmed,PasswordAttempts FROM User WHERE Email=?",(email,))
                userDetails = cursor.fetchall()
                actualPassword = userDetails[0][0]
                UserID = userDetails[0][1]
                firstName = userDetails[0][2]
                emailConfirmed = userDetails[0][3]
                passwordAttempts = userDetails[0][4]

                connection.close()

                if check_password_hash(actualPassword,password):
                    #The password in the database is unhashed and compared with password entered
                    if emailConfirmed == 1:
                        #If the email has been confirmed
                        connection = sqlite3.connect("database.db",check_same_thread=False)
                        cursor = connection.cursor()
                        cursor.execute("UPDATE User SET PasswordAttempts=? WHERE Email=?",(0,email,))
                        #Reset password attempts to 0 if user successfully logs in
                        connection.commit()
                        connection.close()

                        flash('Logged in successfully!', category='success')
                        user = User(UserID,firstName,actualPassword,email)
                        login_user(user, remember=True)
                        #Redirect user to homepage after logging in
                        return redirect(url_for('homePage.home'))
                    else:
                        #If the email has not been confirmed
                        flash('Email not verified',category='error')
                else:
                    if passwordAttempts <= 3:
                        #If the user has had less than 3 attempts at the password
                        passwordAttempts = passwordAttempts + 1
                        #IF the password entered is wrong then it is incremented by 1
                        connection = sqlite3.connect("database.db",check_same_thread=False)
                        cursor = connection.cursor()
                        cursor.execute("UPDATE User SET PasswordAttempts=? WHERE Email=?",(passwordAttempts,email,))
                        #Number of password attempts are updated in the database
                        connection.commit()
                        connection.close()
                        flash('Password incorrect, please try again!',category='error')

                    else:
                        #If the password attempts are greater than 3
                        connection = sqlite3.connect("database.db",check_same_thread=False)
                        cursor = connection.cursor()
                        cursor.execute("UPDATE User SET EmailConfirmed=? WHERE Email=?",(0,email,))
                        #Database is updated so email is unverified
                        connection.commit()
                        connection.close()
                        flash('Your account has been unverified please verify again', category='error')

                        token = s.dumps(email,salt='email-confirm')

                        with current_app.app_context():
                            mail = Mail(current_app)
                            msg = Message('Confirm Email', recipients=[email])
                            link = url_for('auth.confirm_email',token=token,_external=True)
                            msg.body = 'Your link is {}'.format(link)
                            mail.send(msg)
                            #Link to verify user's email is sent to their email

            else:
                flash('Email does not exist.', category='error')

        if request.form.get('ResendVerificationLink') == 'Resend Verification Link':
            #If user requests to resend verification link
            email = request.form.get('email')
            password = request.form.get('password')
            #Form data recieved
            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()

            cursor.execute("SELECT * from User WHERE Email = ?",(email,))
            results = cursor.fetchall()
            connection.close()
            #Information associated with email entered is checked
            if len(results) != 0:
                #If account does exist
                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()
                
                cursor.execute("SELECT Password,UserID,FirstName,EmailConfirmed FROM User WHERE Email=?",(email,))
                userDetails = cursor.fetchall()
                actualPassword = userDetails[0][0]
                UserID = userDetails[0][1]
                firstName = userDetails[0][2]
                emailConfirmed = userDetails[0][3]

                connection.close()

                if check_password_hash(actualPassword[0][0],password):
                    #Unhash password from database and compare with password entered
                    if emailConfirmed[0][0] == 1:
                        #If email is already verified then an error message is displayed
                        flash('This email is already verified', category='error')
                    else:

                        token = s.dumps(email,salt='email-confirm')

                        with current_app.app_context():
                            mail = Mail(current_app)
                            msg = Message('Confirm Email', recipients=[email])
                            link = url_for('auth.confirm_email',token=token,_external=True)
                            msg.body = 'Your link is {}'.format(link)
                            mail.send(msg)
                            #Email verification link is sent to the user's email
                            flash('Verification link sent',category='success')

                        return render_template("login.html", user=None)
                else:
                    flash('Incorrect password, try again.', category='error')
            else:
                flash('Email does not exist.', category='error')

    return render_template("login.html", user=None)


@auth.route('/logout')
@login_required
def logout():
    #User is logged out
    logout_user()
    return redirect(url_for('auth.login'))



@auth.route('/confirm_email/<token>', methods=['GET', 'POST'])
def confirm_email(token):
    try:
        #If verification link is accessed within the time limit
        email = s.loads(token, salt='email-confirm', max_age=300)
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("UPDATE User SET EmailConfirmed=? WHERE Email=?",(1,email,))
        connection.commit()
        #Database is updated so email is verified
        flash('Account confirmed!', category='success')

        cursor.execute("SELECT UserID,FirstName,Password from User WHERE Email =?",(email,))
        userDetails = cursor.fetchall()
        connection.close()
        new_user = User(userDetails[0][0],userDetails[0][1],userDetails[0][2],email)
        login_user(new_user, remember=True)
        #After verification, user is logged in
        return redirect(url_for('homePage.home'))

    except:
        #If verification link is accessed outside the time limit
        #Error message is displayed
        flash('token has expired',category='error')
        return redirect(url_for('auth.sign_up'))

    

@auth.route('/confirm_change_password/<token>', methods=['GET', 'POST'])
def confirm_change_password(token):
    try:
        #If link is accessed within the time limit
        email = s.loads(token, salt='email-confirm', max_age=300)
        return redirect(url_for("auth.changePassword",email=email))
        #User is redirected to page to change their password
    except:
        #If link is accessed outside the time limit
        #Error message is displayed
        flash('token has expired',category='error')
        return redirect(url_for('auth.login'))
    


@auth.route('/changePassword/<email>',methods=['GET', 'POST'])
def changePassword(email):

    if request.method == 'POST':

        Password1 = request.form.get('password1')
        Password2 = request.form.get('password2')
        #Form data recieved
        if Password1 != Password2:
            flash('Passwords don\'t match.', category='error')
            return render_template('changePassword.html',user=current_user)
        elif len(Password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
            return render_template('changePassword.html',user=current_user)
        else:
            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()
            cursor.execute("UPDATE User SET Password=? WHERE Email=?",(generate_password_hash(Password2, method='sha256'),email,))
            #Password is hashed before being stored in the database
            connection.commit()
            connection.close()
            flash('Password changed successfully',category='success')
            return redirect(url_for("auth.login"))
            #Database is updated with new password and user is redirected to the login page to login

    return render_template('changePassword.html',user=None)



@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        Email = request.form.get('email')
        FirstName = request.form.get('firstName')
        Password1 = request.form.get('password1')
        Password2 = request.form.get('password2')
        #Form data recieved
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("SELECT * from User WHERE Email = ?",(Email,))
        results = cursor.fetchall()
        #Information associated with email entered is checked
        connection.close()

        if len(results) != 0:
            flash('Email already exists.', category='error')
            return render_template("sign_up.html", user=None)
        elif len(Email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(FirstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif Password1 != Password2:
            flash('Passwords don\'t match.', category='error')
        elif len(Password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:

            token = s.dumps(Email,salt='email-confirm')

            with current_app.app_context():
                mail = Mail(current_app)
                msg = Message('Confirm Email', recipients=[Email])
                link = url_for('auth.confirm_email',token=token,_external=True)
                msg.body = 'Your link is {}'.format(link)
                mail.send(msg)
                #Verification link is emailed to user

                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()

                cursor.execute("INSERT INTO User (Email,Password,FirstName,EmailConfirmed,PasswordAttempts) values(?,?,?,?,?)", (Email,generate_password_hash(Password1, method='sha256'),FirstName,0,0))
                connection.commit()
                connection.close()
                #Password is hashed before storing in database
                #Database is updated with new user details

            flash('Account created! Please verify email', category='success')
            return redirect(url_for('auth.login'))

    return render_template("sign_up.html", user=None)
