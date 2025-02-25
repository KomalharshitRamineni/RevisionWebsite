from flask import Blueprint, render_template
from flask_login import login_required, current_user

homePage = Blueprint('homePage',__name__)

@homePage.route('/home')
@login_required
def home():
    #Displays the homepage
    return render_template("home.html", user=current_user)

