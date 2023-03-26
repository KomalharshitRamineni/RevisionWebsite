from flask import Blueprint, render_template, flash, redirect,url_for,request,jsonify,session
from flask_login import login_required, current_user

HomePage = Blueprint('HomePage',__name__)

@HomePage.route('/home')
@login_required
def home():
    return render_template("home.html", user=current_user)

