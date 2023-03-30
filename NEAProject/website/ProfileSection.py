from flask import Blueprint, render_template, flash, redirect,url_for,request,current_app
from flask_login import login_required, current_user,logout_user
import sqlite3
from flask_mail import Mail,Message
from itsdangerous import URLSafeTimedSerializer
from .functions import returnBestAndWorstScores
from werkzeug.security import generate_password_hash

s=URLSafeTimedSerializer('aysidgkjhasdf')
profileSection = Blueprint('profileSection',__name__)



@profileSection.route('/profile',methods=['GET', 'POST'])
@login_required
def Profile():
    UserID = current_user.get_id()
    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("""  SELECT Email,FirstName 
                        FROM User
                        WHERE UserID=?
                        """,(UserID,))
    userDetails = cursor.fetchall()#The details of the current user are queried
    connection.close()

    if request.method == 'POST':
        if request.form.get('ChangeName') == 'Change Name':
            return redirect(url_for('profileSection.changeName'))
            #If the button to change name is pressed the user is redirected to the corresponding page
        
        # if request.form.get('ViewFeedback') == 'View Feedback':
        #     return redirect(url_for('profileSection.ViewFeedback'))
        #     #If the button to change name is pressed the user is redirected to the corresponding page

        if request.form.get('ChangeEmail') == 'Change Email':
            #If the button to change email is pressed the user is sent an email
            token = s.dumps(userDetails[0][0],salt='email-confirm')

            with current_app.app_context():
                mail = Mail(current_app)
                msg = Message('Change Email Link', recipients=[userDetails[0][0]])
                link = url_for('profileSection.confirm_change_email',token=token,_external=True)
                msg.body = 'Your link is {}'.format(link)
                mail.send(msg)
                #The link to change email is emailed to the user
                flash('Link to change eamil sent to email',category='success')

        if request.form.get('ChangePassword') == 'Change Password':
            #If the button to change password is pressed the user is sent an email
            token = s.dumps(userDetails[0][0],salt='email-confirm')

            with current_app.app_context():
                mail = Mail(current_app)
                msg = Message('Change Password Link', recipients=[userDetails[0][0]])
                link = url_for('profileSection.confirm_change_password',token=token,_external=True)
                msg.body = 'Your link is {}'.format(link)
                mail.send(msg)
                #The link to change password is emailed to the user
                flash('Link to change password sent to email',category='success')

    return render_template("userProfile.html", user=current_user,UserDetails=userDetails)
    #profile page is displayed unless an post requests are made


@profileSection.route('/confirm_change_password/<token>', methods=['GET', 'POST'])
@login_required
def confirm_change_password(token):
    #This page is redirected to when the user accessed the link to change password
    try:
        email = s.loads(token, salt='email-confirm', max_age=300)
        return redirect(url_for("profileSection.changePassword"))
        #If the link was accessed within the time frame then the user is redirected to the page to change password

    except:
        flash('token has expired',category='error')
        return redirect(url_for('profileSection.Profile'))
        #If the link has expired then the user is redirected back to the profile page


@profileSection.route('/confirm_change_email/<token>', methods=['GET', 'POST'])
@login_required
def confirm_change_email(token):
    #This page is redirected to when the user accessed the link to change email
    try:
        email = s.loads(token, salt='email-confirm', max_age=300)
        return redirect(url_for("profileSection.changeEmail"))
    #If the link was accessed within the time frame then the user is redirected to the page to change email

    except:
        flash('token has expired',category='error')
        return redirect(url_for('profileSection.Profile'))
        #If the link has expired then the user is redirected back to the profile page



@profileSection.route('/changePassword',methods=['GET', 'POST'])
@login_required
def changePassword():
    UserID = current_user.get_id()
    if request.method == 'POST':

        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        #Data from form is recieved

        if password1 != password2:
            flash('Passwords don\'t match.', category='error')
            return render_template('changePassword.html',user=current_user)
            #If passwords recieved from the form don't match then an error is displayed
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
            return render_template('changePassword.html',user=current_user)
            #If password recieved from the form don't meet the requirements then an error is displayed
        else:
            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()
            cursor.execute("UPDATE User SET Password=? WHERE UserId=?",(generate_password_hash(password2, method='sha256'),UserID,))
            connection.commit()
            connection.close()
            flash('Password changed successfully',category='success')
            #Given valid form data, the database is updated with the new password
            return redirect(url_for("profileSection.Profile"))

    return render_template('changePassword.html',user=current_user)
    #Form is displayed on the get request


@profileSection.route('/changeName',methods=['GET', 'POST'])
@login_required
def changeName():
    UserID = current_user.get_id()
    if request.method == 'POST':
        newName = request.form.get('name')
        #Data is recieved from the form

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("""  SELECT FirstName 
                            FROM User
                            WHERE UserID=?
                            """,(UserID,))
        userFirstName = cursor.fetchall()
        #The user's current name is queried
        connection.close()
        if userFirstName[0][0] == newName:
            flash('Choose a name different from the one you already have',category='error')
            return render_template('changeUserName.html',user=current_user)
            #If the new name entered is the same as their current then an error is displayed

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("UPDATE User SET FirstName=? WHERE UserId=?",(newName,UserID,))
        connection.commit()
        flash('Name changed!',category='success')
        connection.close()
        #If their name is different then the database is updated and the user is redirected to the profile page
        return redirect(url_for('profileSection.Profile'))

    return render_template('changeUserName.html',user=current_user)
    #Displays the form to change user name on the get request



@profileSection.route('/ViewFeedback',methods=['GET', 'POST'])
@login_required
def ViewFeedback():
    UserID = current_user.get_id()
    feedback=[]
    parentDeckNamesOwnedByUser = {}
    quizzes = []

    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()

    cursor.execute("""  SELECT ParentFlashcardDeck.FlashcardDeckName
                        FROM ParentFlashcardDeck,FlashcardsDecksAndUserIDs
                        WHERE FlashcardsDecksAndUserIDs.UserID=?
                        AND FlashcardsDecksAndUserIDs.ParentFlashcardDeckID=ParentFlashcardDeck.ParentFlashcardDeckID""",(UserID,))
    
    parentDecksOwnedByUser = cursor.fetchall()
    #Queries the for all the parent decks that the user owns
    parentDecksOwnedByUser = list(dict.fromkeys(parentDecksOwnedByUser))
    #Any duplicates are removed
    for x in parentDecksOwnedByUser:
        parentDeckNamesOwnedByUser[x[0]] = []

    for key in parentDeckNamesOwnedByUser.keys(): 

        cursor.execute("""SELECT FlashcardDeck.FlashcardDeckName
                        FROM ParentFlashcardDeck
                        JOIN FlashcardsDecksAndUserIDs ON ParentFlashcardDeck.ParentFlashcardDeckID = FlashcardsDecksAndUserIDs.ParentFlashcardDeckID
                        JOIN FlashcardDeck ON FlashcardsDecksAndUserIDs.FlashcardDeckID = FlashcardDeck.FlashcardDeckID
                        WHERE ParentFlashcardDeck.FlashcardDeckName = ?""",
                    (key,))
        #Queries for the subdecks of a parent deck
        subdecksOfParentDeck = []
        subdecks = cursor.fetchall()
        subdecks = list(dict.fromkeys(subdecks))
        #Any duplicates are removed
        for x in subdecks:
            subdecksOfParentDeck.append(x[0])
        parentDeckNamesOwnedByUser.update({key:subdecksOfParentDeck})
        #Dictionary is updated where the key is the parent deck and the value is an array of sub decks which belong to the parent deck

    cursor.execute("SELECT QuizID FROM PastQuiz WHERE UserID=?",(UserID,))
    quizIDsDoneByUser = cursor.fetchall()
    quizIDsDoneByUser = list(dict.fromkeys(quizIDsDoneByUser))


    for x in quizIDsDoneByUser:
        QuizID = x[0]
        cursor.execute("SELECT * FROM Quiz WHERE QuizID=?",(QuizID,))
        QuizDetails = cursor.fetchall()
        for key,value in parentDeckNamesOwnedByUser.items():
            if QuizDetails[0][3] in value:
                #If the deck the quiz was made on is part of a subdeck, then the user's score is calculated
                score = int(QuizDetails[0][2])/int(QuizDetails[0][1])
                quizzes.append((key,QuizDetails[0],score))
                #the user's score is stored and added to the quizzes array


    for key,value in parentDeckNamesOwnedByUser.items():
        feedback.append(returnBestAndWorstScores(quizzes,key,value))
        #The user's best and worst quizzes are returnd out of the quizzes they have done
        #The best and worst quizzes are taken for each parent deck the user has

    return render_template('viewFeedback.html',user=current_user,feedback=feedback)



@profileSection.route('/changeEmail',methods=['GET', 'POST'])
@login_required
def changeEmail():
    UserID = current_user.get_id()
    if request.method == 'POST':

        email = request.form.get('email')
        #Form data recieved

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("""  SELECT email 
                            FROM User
                            WHERE UserID=?
                            """,(UserID,))
        UserEmail = cursor.fetchall()
        #User's current email is queried
        
        if UserEmail[0][0] == email:
            flash('Choose an email different from the one you already have',category='error')
            return render_template('changeUserEmail.html',user=current_user)
            #If the email entered is the same as the one that already exists then an error is displayed
        
        cursor.execute("SELECT email FROM User")
        allUserEmails = cursor.fetchall()
        #All emails with an account are queried
        for UserEmail in allUserEmails:
            if UserEmail[0] == email:
                flash('An account already exists with the email you have entered!',category='error')
                return render_template('changeUserEmail.html',user=current_user)
                #If email entered is already associated with an account then an error is displayed
        connection.close()

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("UPDATE User SET email=?,EmailConfirmed=? WHERE UserId=?",(email,0,UserID,))
        connection.commit()
        #If a valid email is entered then database is updated with email confirmed is set as false
        flash('Email changed! Please verify',category='success')

        token = s.dumps(email,salt='email-confirm')

        with current_app.app_context():
            mail = Mail(current_app)
            msg = Message('Confirm Email', recipients=[email])
            link = url_for('auth.confirm_email',token=token,_external=True)
            msg.body = 'Your link is {}'.format(link)
            mail.send(msg)
            #Link to verify email is sent to the user's new email

            logout_user()
        
        return redirect(url_for('auth.login'))

    return render_template('changeUserEmail.html',user=current_user)