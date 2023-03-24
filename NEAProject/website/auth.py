from flask import Blueprint, render_template, request, flash, redirect, url_for,current_app
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Mail,Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired


import sqlite3
from .models import User



auth = Blueprint('auth', __name__)


s=URLSafeTimedSerializer('SECRET KEY')


@auth.route('/')
def welcome():  
    if current_user == None:
        return render_template("welcomePage.html",user=None)
    else:
        logout_user()#So that if the user is logged out before being redirected back to the page, need to do the same for all other pages that don't require login
        return render_template("welcomePage.html",user=None)




@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('ResetPassword') == 'Reset Password':
            

        

            email = request.form.get('email')
            
            if email == '':
                flash('Please enter an email',category='error')
                return render_template("login.html", user=None)
            else:
                    
                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()

                cursor.execute("SELECT * from User WHERE Email = ?",(email,))
                connection.close()
                results = cursor.fetchall()
                if len(results) == 0:
                    flash('Account does not exist with email given!',category='error')
                    return render_template("login.html", user=None)

                else:

                    with current_app.app_context():
                        token = s.dumps(email,salt='email-confirm')
                        mail = Mail(current_app)
                        msg = Message('Change Password Link', recipients=[email])
                        link = url_for('ProfileSection.confirm_change_password',token=token,_external=True)
                        msg.body = 'Your link is {}'.format(link)
                        mail.send(msg)
                        flash('Link to reset password sent to email',category='success')

                        return redirect(url_for('auth.login'))
            


        if request.form.get('Login') == 'Login':


            email = request.form.get('email')
            password = request.form.get('password')

            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()

            cursor.execute("SELECT * from User WHERE Email = ?",(email,))
            results = cursor.fetchall()
            connection.close()
            

            if len(results) != 0:

                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()

                cursor.execute("SELECT Password from User WHERE Email =?",(email,))
                ActualPassword = cursor.fetchall()
                cursor.execute("SELECT UserID from User WHERE Email =?",(email,))
                UserID = cursor.fetchall()
                cursor.execute("SELECT FirstName from User WHERE Email =?",(email,))
                firstName = cursor.fetchall()
                cursor.execute("SELECT EmailConfirmed from User WHERE Email =?",(email,))
                EmailConfirmed = cursor.fetchall()
                cursor.execute("SELECT PasswordAttempts from User WHERE Email =?",(email,))
                PasswordAttempts = cursor.fetchall()

                connection.close()

                if ActualPassword[0][0] == password:
                    if EmailConfirmed[0][0] == 1:

                        connection = sqlite3.connect("database.db",check_same_thread=False)
                        cursor = connection.cursor()
                        cursor.execute("UPDATE User SET PasswordAttempts=? WHERE Email=?",(0,email,))
                        connection.commit()
                        connection.close()


                        flash('Logged in successfully!', category='success')

                        user = User(UserID[0][0],firstName[0][0],ActualPassword[0][0],email)
                        
                        
                        login_user(user, remember=True)
                        return redirect(url_for('HomePage.home'))
                    else:
                        flash('Email not verified',category='error')
                else:
                    print(PasswordAttempts[0][0])
                    if PasswordAttempts[0][0] <= 3:
                        PasswordAttempts = PasswordAttempts[0][0] + 1
                        connection = sqlite3.connect("database.db",check_same_thread=False)
                        cursor = connection.cursor()
                        cursor.execute("UPDATE User SET PasswordAttempts=? WHERE Email=?",(PasswordAttempts,email,))
                        connection.commit()
                        connection.close()
                        flash('Password incorrect, please try again!',category='error')

                    else:
                        connection = sqlite3.connect("database.db",check_same_thread=False)
                        cursor = connection.cursor()
                        cursor.execute("UPDATE User SET EmailConfirmed=? WHERE Email=?",(0,email,))
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

            else:
                flash('Email does not exist.', category='error')



        if request.form.get('ResendVerificationLink') == 'Resend Verification Link':


            email = request.form.get('email')
            password = request.form.get('password')

            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()

            cursor.execute("SELECT * from User WHERE Email = ?",(email,))
            results = cursor.fetchall()
            

            if len(results) != 0:

                cursor.execute("SELECT Password from User WHERE Email =?",(email,))
                ActualPassword = cursor.fetchall()
                cursor.execute("SELECT UserID from User WHERE Email =?",(email,))
                UserID = cursor.fetchall()
                cursor.execute("SELECT FirstName from User WHERE Email =?",(email,))
                firstName = cursor.fetchall()
                cursor.execute("SELECT EmailConfirmed from User WHERE Email =?",(email,))
                EmailConfirmed = cursor.fetchall()

                connection.close()

                if ActualPassword[0][0] == password:
                    if EmailConfirmed[0][0] == 1:
                        flash('This email is already verified', category='error')
                    else:

                        token = s.dumps(email,salt='email-confirm')

                        with current_app.app_context():
                            mail = Mail(current_app)
                            msg = Message('Confirm Email', recipients=[email])
                            link = url_for('auth.confirm_email',token=token,_external=True)
                            msg.body = 'Your link is {}'.format(link)
                            mail.send(msg)
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
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/confirm_email/<token>', methods=['GET', 'POST'])
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=300)
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("UPDATE User SET EmailConfirmed=? WHERE Email=?",(1,email,))
        connection.commit()
        
        flash('Account confirmed!', category='success')

        cursor.execute("SELECT UserID,FirstName,Password from User WHERE Email =?",(email,))
        UserDetails = cursor.fetchall()
        connection.close()

        new_user = User(UserDetails[0][0],UserDetails[0][1],UserDetails[0][2],email)

        login_user(new_user, remember=True)

        return redirect(url_for('HomePage.home'))

    except:
        flash('token has expired',category='error')
        return redirect(url_for('auth.sign_up'))

    

@auth.route('/confirm_change_password/<token>', methods=['GET', 'POST'])
def confirm_change_password(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=300)
        return redirect(url_for("auth.changePassword",email=email))

    except:
        flash('token has expired',category='error')
        return redirect(url_for('auth.login'))
    

@auth.route('/changePassword/<email>',methods=['GET', 'POST'])
def changePassword(email):

    if request.method == 'POST':

        Password1 = request.form.get('password1')
        Password2 = request.form.get('password2')

        if Password1 != Password2:
            flash('Passwords don\'t match.', category='error')
            return render_template('changePassword.html',user=current_user)
        elif len(Password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
            return render_template('changePassword.html',user=current_user)
        else:
            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()
            cursor.execute("UPDATE User SET Password=? WHERE Email=?",(Password2,email,))
            connection.commit()
            connection.close()
            flash('Password changed successfully',category='success')
            return redirect(url_for("auth.login"))


    return render_template('changePassword.html',user=None)







@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        Email = request.form.get('email')
        FirstName = request.form.get('firstName')
        Password1 = request.form.get('password1')
        Password2 = request.form.get('password2')



        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("SELECT * from User WHERE Email = ?",(Email,))
        results = cursor.fetchall()

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

                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()

                cursor.execute("INSERT INTO User (Email,Password,FirstName,EmailConfirmed,PasswordAttempts) values(?,?,?,?,?)", (Email,Password1,FirstName,0,0))
                connection.commit()

                connection.close()

            
            flash('Account created! Please verify email', category='success')
            return redirect(url_for('auth.login'))

    return render_template("sign_up.html", user=None)




