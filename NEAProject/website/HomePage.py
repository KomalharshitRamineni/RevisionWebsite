from flask import Blueprint, render_template, flash, redirect,url_for,request,jsonify,session
from flask_login import login_required, current_user
from .AnkiOperations import extractFlashcards, returnDecksAvailable, checkIfAnkiOpen, returnChildDecks
import sqlite3
from .models import Flashcard, FlashcardDeck

HomePage = Blueprint('HomePage',__name__)

@HomePage.route('/home')
@login_required
def home():
    return render_template("home.html", user=current_user)

