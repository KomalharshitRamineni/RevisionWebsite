from flask import Flask
from os import path
from flask_login import LoginManager
import sqlite3

DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'FASHDGASKDJF'
    app.config.from_pyfile('config.cfg')
    
    from .flashcardsSection import flashcardsSection
    from .auth import auth
    from .homePage import homePage
    from .quizSection import quizSection
    from .profileSection import profileSection
    from .models import User    

    app.register_blueprint(flashcardsSection, url_prefix='/')
    app.register_blueprint(homePage, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(quizSection,url_prefix='/')
    app.register_blueprint(profileSection,url_prefix='/')   #Registering all blueprints

    create_database(app)    #Initialises database

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id): #Loads user given their ID

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("SELECT FirstName,Password,Email FROM User WHERE UserID=?",(id,))
        UserDetails = cursor.fetchall()

        user = User(id,UserDetails[0][0],UserDetails[0][1],UserDetails[0][2])
        connection.close()
        return user
    
    return app



def create_database(app): #Creates database by running sqlCode.py
    if not path.exists('NEAProject/website/' + DB_NAME):
        with app.app_context():
            with open("website/sqlCode.py", 'r') as file:
                exec(file.read())



