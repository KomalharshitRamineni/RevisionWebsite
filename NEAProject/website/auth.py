from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

import sqlite3
from .models import User











auth = Blueprint('auth', __name__)



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

            connection.close()

            if ActualPassword[0][0] == password:
                flash('Logged in successfully!', category='success')

                user = User(UserID[0][0],firstName[0][0],ActualPassword[0][0],email)
                 
                  
                login_user(user, remember=True)
                return redirect(url_for('HomePage.home'))

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
        elif len(Email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(FirstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif Password1 != Password2:
            flash('Passwords don\'t match.', category='error')
        elif len(Password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:

            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()


            cursor.execute("INSERT INTO User (Email,Password,FirstName) values(?,?,?)", (Email,Password1,FirstName,))
            connection.commit()


            cursor.execute("SELECT UserID from User WHERE Email =?",(Email,))
            UserID = cursor.fetchall()

            connection.close()

            new_user = User(UserID[0][0],FirstName,Password1,Email)


            login_user(new_user, remember=True)

            
            flash('Account created!', category='success')
            return redirect(url_for('HomePage.home'))

    return render_template("sign_up.html", user=None)




