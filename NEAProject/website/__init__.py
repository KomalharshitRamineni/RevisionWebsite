from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import sqlite3
import subprocess
import os
#db = SQLAlchemy()

#import sqlcode and execute



DB_NAME = "database.db"




def create_app():
    app = Flask(__name__)


    app.config['SECRET_KEY'] = 'FASHDGASKDJF'
    #app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'


    #db.init_app(app)

    from .FlashcardsSection import FlashcardsSection
    from .auth import auth
    from .HomePage import HomePage

    app.register_blueprint(FlashcardsSection, url_prefix='/')
    app.register_blueprint(HomePage, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User            


    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("SELECT FirstName from User WHERE UserID =?",(id,))
        firstname = cursor.fetchall()
        cursor.execute("SELECT Password from User WHERE UserID =?",(id,))
        password = cursor.fetchall()
        cursor.execute("SELECT Email from User WHERE UserID =?",(id,))
        email = cursor.fetchall()

        user = User(id,firstname,password,email)
        connection.close()
        return user


    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):

        with app.app_context():


            # execute sqlcode
            # cmd = 'sqlCode.py'
            # p = subprocess.Popen(cmd, shell=True)





            # os.getcwd()
            # print(os.listdir())
            with open("website/sqlCode.py", 'r') as file:
                exec(file.read())


            #b.create_all()

        print('Created Database!')