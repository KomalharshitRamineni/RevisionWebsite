from flask import Blueprint, render_template, flash, redirect,url_for,request,current_app
from flask_login import login_required, current_user,logout_user
import sqlite3
from flask_mail import Mail,Message
from itsdangerous import URLSafeTimedSerializer
from .functions import returnBestAndWorstScores

s=URLSafeTimedSerializer('SECRET KEY')
ProfileSection = Blueprint('ProfileSection',__name__)








@ProfileSection.route('/profile',methods=['GET', 'POST'])
@login_required
def Profile():
    UserID = current_user.get_id()
    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("""  SELECT Email,FirstName 
                        FROM User
                        WHERE UserID=?
                        """,(UserID,))
    UserDetails = cursor.fetchall()
    connection.close()

    if request.method == 'POST':
        if request.form.get('ChangeName') == 'Change Name':
            return redirect(url_for('ProfileSection.changeName'))
        
        if request.form.get('ViewFeedback') == 'View Feedback':
            return redirect(url_for('ProfileSection.ViewFeedback'))


        if request.form.get('ChangeEmail') == 'Change Email':

    
            token = s.dumps(UserDetails[0][0],salt='email-confirm')

            with current_app.app_context():
                mail = Mail(current_app)
                msg = Message('Change Password Link', recipients=[UserDetails[0][0]])
                link = url_for('ProfileSection.confirm_change_email',token=token,_external=True)
                msg.body = 'Your link is {}'.format(link)
                mail.send(msg)
                flash('Link to change eamil sent to email',category='success')




        if request.form.get('ChangePassword') == 'Change Password':

            token = s.dumps(UserDetails[0][0],salt='email-confirm')

            with current_app.app_context():
                mail = Mail(current_app)
                msg = Message('Change Password Link', recipients=[UserDetails[0][0]])
                link = url_for('ProfileSection.confirm_change_password',token=token,_external=True)
                msg.body = 'Your link is {}'.format(link)
                mail.send(msg)
                flash('Link to change password sent to email',category='success')


    return render_template("userProfile.html", user=current_user,UserDetails=UserDetails)






@ProfileSection.route('/confirm_change_password/<token>', methods=['GET', 'POST'])
@login_required
def confirm_change_password(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=300)
        return redirect(url_for("ProfileSection.changePassword"))

    except:
        flash('token has expired',category='error')
        return redirect(url_for('ProfileSection.Profile'))
    


@ProfileSection.route('/confirm_change_email/<token>', methods=['GET', 'POST'])
@login_required
def confirm_change_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=300)
        return redirect(url_for("ProfileSection.changeEmail"))

    except:
        flash('token has expired',category='error')
        return redirect(url_for('ProfileSection.Profile'))




@ProfileSection.route('/changePassword',methods=['GET', 'POST'])
@login_required
def changePassword():
    UserID = current_user.get_id()
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
            cursor.execute("UPDATE User SET Password=? WHERE UserId=?",(Password2,UserID,))
            connection.commit()
            connection.close()
            flash('Password changed successfully',category='success')
            return redirect(url_for("ProfileSection.Profile"))


    return render_template('changePassword.html',user=current_user)





@ProfileSection.route('/changeName',methods=['GET', 'POST'])
@login_required
def changeName():
    UserID = current_user.get_id()
    if request.method == 'POST':
        newName = request.form.get('name')

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("""  SELECT FirstName 
                            FROM User
                            WHERE UserID=?
                            """,(UserID,))
        UserFirstName = cursor.fetchall()
        connection.close()
        if UserFirstName[0][0] == newName:
            flash('Choose a name different from the one you already have',category='error')
            return render_template('changeUserName.html',user=current_user)


        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("UPDATE User SET FirstName=? WHERE UserId=?",(newName,UserID,))
        connection.commit()
        flash('Name changed!',category='success')
        connection.close()
        return redirect(url_for('ProfileSection.Profile'))

    return render_template('changeUserName.html',user=current_user)





@ProfileSection.route('/ViewFeedback',methods=['GET', 'POST'])
@login_required
def ViewFeedback():
    UserID = current_user.get_id()
    feedback=[]
    ParentDeckNamesOwnedByUser = {}
    Quizzes = []

    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()

    cursor.execute("""  SELECT ParentFlashcardDeck.FlashcardDeckName
                        FROM ParentFlashcardDeck,FlashcardsDecksAndUserIDs
                        WHERE FlashcardsDecksAndUserIDs.UserID=?
                        AND FlashcardsDecksAndUserIDs.ParentFlashcardDeckID=ParentFlashcardDeck.ParentFlashcardDeckID""",(UserID,))
    ParentDecksOwnedByUser = cursor.fetchall()
    ParentDecksOwnedByUser = list(dict.fromkeys(ParentDecksOwnedByUser))
    for x in ParentDecksOwnedByUser:
        ParentDeckNamesOwnedByUser[x[0]] = []


    for key in ParentDeckNamesOwnedByUser.keys():   
        cursor.execute("""  SELECT FlashcardDeck.FlashcardDeckName 
                            FROM FlashcardDeck,ParentFlashcardDeck,FlashcardsDecksAndUserIDs 
                            WHERE ParentFlashcardDeck.FlashcardDeckName = ?
                            AND ParentFlashcardDeck.ParentFlashcardDeckID=FlashcardsDecksAndUserIDs.ParentFlashcardDeckID
                            AND FlashcardDeck.FlashcardDeckID=FlashcardsDecksAndUserIDs.FlashcardDeckID
                            
                            """,(key,))
        subdecksOfParentDeck = []
        subdecks = cursor.fetchall()
        subdecks = list(dict.fromkeys(subdecks))
        for x in subdecks:
            subdecksOfParentDeck.append(x[0])
        ParentDeckNamesOwnedByUser.update({key:subdecksOfParentDeck})




    cursor.execute("SELECT QuizID FROM PastQuiz WHERE UserID=?",(UserID,))
    QuizIDsDoneByUser = cursor.fetchall()
    QuizIDsDoneByUser = list(dict.fromkeys(QuizIDsDoneByUser))


    for x in QuizIDsDoneByUser:
        QuizID = x[0]
        cursor.execute("SELECT * FROM Quiz WHERE QuizID=?",(QuizID,))
        QuizDetails = cursor.fetchall()
        for key,value in ParentDeckNamesOwnedByUser.items():
            if QuizDetails[0][3] in value:
                score = int(QuizDetails[0][2])/int(QuizDetails[0][1])
                Quizzes.append((key,QuizDetails[0],score))


    for key,value in ParentDeckNamesOwnedByUser.items():
        feedback.append(returnBestAndWorstScores(Quizzes,key,value))
        


    return render_template('ViewFeedback.html',user=current_user,feedback=feedback)


















@ProfileSection.route('/changeEmail',methods=['GET', 'POST'])
@login_required
def changeEmail():
    UserID = current_user.get_id()
    if request.method == 'POST':

        email = request.form.get('email')

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("""  SELECT email 
                            FROM User
                            WHERE UserID=?
                            """,(UserID,))
        UserEmail = cursor.fetchall()
        
        if UserEmail[0][0] == email:
            flash('Choose an email different from the one you already have',category='error')
            return render_template('changeUserEmail.html',user=current_user)
        
        cursor.execute("SELECT email FROM User")
        
        allUserEmails = cursor.fetchall()
        for UserEmail in allUserEmails:
            if UserEmail[0] == email:
                flash('An account already exists with the email you have entered!',category='error')
                return render_template('changeUserEmail.html',user=current_user)
        connection.close()

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("UPDATE User SET email=?,EmailConfirmed=? WHERE UserId=?",(email,0,UserID,))#send verification then redirect to logout
        connection.commit()
        flash('Email changed! Please verify',category='success')

        token = s.dumps(email,salt='email-confirm')

        with current_app.app_context():
            mail = Mail(current_app)
            msg = Message('Confirm Email', recipients=[email])
            link = url_for('auth.confirm_email',token=token,_external=True)
            msg.body = 'Your link is {}'.format(link)
            mail.send(msg)

            logout_user()
        
        

        return redirect(url_for('auth.login'))

    return render_template('changeUserEmail.html',user=current_user)