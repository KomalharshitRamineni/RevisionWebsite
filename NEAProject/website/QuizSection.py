from flask import Blueprint, render_template, flash, redirect,url_for,request,session
from flask_login import login_required, current_user
import sqlite3
from .models import Quiz
import random
from string import ascii_uppercase

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    return code
    #Random string is generated with a length of 4

quizSection = Blueprint('quizSection',__name__)

userAndQuizObjects = []
allQuizQuestionsSingleplayers = []
allQuizQuestionsMultiplayer = []

rooms = {}
userScores = {}



@quizSection.route('/quizMenu',  methods=['GET', 'POST'])
@login_required
def quizMenu():
    UserID =current_user.get_id()
    session.clear()
    if request.method == 'POST':
        if request.form.get('TakeQuiz') == 'Take Quiz':
            #If user presses the button to take a quiz
            return redirect(url_for("quizSection.quizMenchooseDeckToQuizOn"))
        
        if request.form.get('PreviousQuizzes') == 'Previous Quizzes':
            #If the user presses the button to see previous quizzes
            return redirect(url_for("quizSection.viewPastQuizzes"))

        else:
            #If the user presses button to either host or join a quiz
            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()
            cursor.execute("SELECT Firstname FROM User WHERE UserID=?",(UserID,))
            name = cursor.fetchall()[0][0]
            code = request.form.get("code")
            join = request.form.get("join", False)
            create = request.form.get("create", False)
            quizID = request.form.get("QuizID")
            connection.close()
            #Form data is recieved
            

            if join != False and not code:
                #If user has not entered a code to join the quiz
                flash("You have not entered a code for the Quiz")
                return render_template("quizMenu.html",user=current_user, code=code)

            room = code
            try:
                if rooms[room].get("QuizID") == quizID:
                    #Checks rooms dictionary to see if there is a quiz room currently ongoing
                    flash('There is already a quiz ongoing with the QuizID you have entered',category='error')
                    return render_template("quizMenu.html",user=current_user, code=code)
            except:
                create = True
            if create != False:

                Users = [UserID]
                room = generate_unique_code(4)
                #Random quizroom code is generated
                rooms[room] = {"members": 0, "messages": [],"QuizID":quizID,"Users":Users}

       
            if room in rooms:
                quizID = rooms[room].get("QuizID")
                currentUsers = rooms[room].get("Users")
                if UserID not in currentUsers:
                    currentUsers.append(UserID)
                rooms[room].update({"Users":currentUsers})
                #rooms dictionary is updated with the new user
        
            session["room"] = room
            session["name"] = name
            userScores[UserID] = 0
            #Quiz room and the code are stored in sessions
            
            return redirect(url_for("quizSection.room",QuizID=quizID))
    
    return render_template("quizMenu.html",user=current_user)



@quizSection.route("/room/<QuizID>",  methods=['GET','POST'])
@login_required
def room(QuizID):
    room = session.get("room")
    #session is checked to see if the quiz room exists
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("quizSection.quizMenu"))
        #If quiz room does not exist then user is redirected to the quiz menu
    return render_template("quizRoom.html",user=current_user, code=room, messages=rooms[room]["messages"],QuizID=QuizID)
    #If quiz room matchs quiz in session then they are allowed to join the quiz room



@quizSection.route("/viewPastQuizzes",  methods=['GET','POST'])
@login_required
def viewPastQuizzes():
    if request.method == 'POST':
        if request.form.get("action1") == 'View PastQuizzes':
            #If the user presses the button to view past quizzes
            return redirect(url_for('quizSection.DisplayPastQuizzes'))
        if request.form.get("action2") == 'Retake Quiz':
            #If the user presses the button to retak quiz
            return redirect(url_for('quizSection.chooseQuizID'))
    return render_template('viewPastQuizzes.html',user=current_user)



@quizSection.route("/DisplayPastQuizzes",  methods=['GET','POST'])
@login_required
def DisplayPastQuizzes():

    UserID=current_user.get_id()
    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("""  SELECT Quiz.QuizID,Quiz.DeckName,Quiz.NumberOfQuestions,Quiz.NumberOfQuestionsAnsweredCorrectly
                        FROM PastQuiz,Quiz 
                        WHERE Quiz.QuizID = PastQuiz.QuizID
                        AND UserID=?""",(UserID,))
    
    data = cursor.fetchall()
    #All the data from the quizzes completed by the user is queried
    data = list(dict.fromkeys(data))
    #Duplicates are removed
    return render_template('displayPastQuizzes.html',user=current_user,data=data)
    #The quizzes are displayed to the user through the HTML page



@quizSection.route("/chooseQuizID",  methods=['GET','POST'])
@login_required
def chooseQuizID():
    UserID = current_user.get_id()
    if request.method == 'POST':

        QuizID = request.form.get("QuizID")
        #Form data recieved
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM PastQuiz WHERE QuizID=? AND UserID=?",(QuizID,UserID))
        results = cursor.fetchall()
        #Query checks if the userID has access to the quiz entered
        if len(results) == 0:
            #If query is empty
            flash('You do not have a quiz with the specified ID',category='error')
            return render_template('chooseQuizID.html',user=current_user)
        else:
            #If user does have access to the quiz
            return redirect(url_for('quizSection.retakeQuiz',QuizID=QuizID))
    return render_template('chooseQuizID.html',user=current_user)



@quizSection.route('/Scoreboard',  methods=['GET', 'POST'])
@login_required
def multiplayScoreboarderQuiz():
    room = session.get("room")
    if room!=None:
        #If quiz room exists
        currentUsers = rooms[room].get("Users")
        userNamesAndScores=[]

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        for user in currentUsers:

            cursor.execute("SELECT Firstname FROM User WHERE UserID=?",(user,))
            userName = cursor.fetchall()
            #Query gets the user's name
            userScore = userScores[user]
            #Dictionary is checked for user's score
            userNamesAndScores.append((userName[0][0],userScore))

        connection.close()
        #The names and scores of the users in the quiz room are returned

        return render_template("ScoreBoard.html",UserNamesAndScores=userNamesAndScores)
    return 



@quizSection.route('/retakeQuiz/<QuizID>',  methods=['GET', 'POST'])
@login_required
def retakeQuiz(QuizID):
    UserID=current_user.get_id()
    QuizID = int(QuizID)
    questionIDs = []

    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()

    cursor.execute("SELECT QuestionID FROM QuizQuestions WHERE QuizID=?",(str(QuizID),))
    questionIDsFromQuiz = cursor.fetchall()
    #The question ids associated with the quiz are queried

    for questionID in questionIDsFromQuiz:
        questionIDs.append(questionID[0])

    connection.close()

    if request.method == 'GET':
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("UPDATE Quiz SET NumberOfQuestionsAnsweredCorrectly=? WHERE QuizID=?",(0,QuizID,))
        connection.commit()
        connection.close()

        quizExists = False
        for singlePlayerQuizQuestion in allQuizQuestionsSingleplayers:
            if singlePlayerQuizQuestion[0][1][0] in questionIDs and UserID == singlePlayerQuizQuestion[0][0]:
                quizQuestions = singlePlayerQuizQuestion
                quizExists = True
        #If the user has an incomplete quiz that they are already retaking then the quiz is returned


        if quizExists == True:
            
            question = quizQuestions[0][1]
            question = list(question)
            questionIDOfQuestion = question[0]
            questionType=question[1]
            #when questions are stored in the database they are turned into strings before storing
            #Therefore array or a dictionary that is in a string needs to be converted back into an array or dictionary
            try:
                questions=eval(question[2])
            except:
                questions=question[2]
            try:
                answers=eval(question[3])
            except:
                answers=question[3]
            try:
                correctAnswer=eval(question[4])
            except:
                correctAnswer=question[4]
        else:
            #If the user does not have an ongoing quiz retake
            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()

            cursor.execute("SELECT QuestionID FROM QuizQuestions WHERE QuizID=?",(str(QuizID),))
            questionIDsFromQuiz = cursor.fetchall()

            quizQuestions = []        

            for questionID in questionIDsFromQuiz:
                cursor.execute("SELECT QuestionID,QuestionType,Question,Answer,CorrectAnswer FROM Question WHERE QuestionID=?",(questionID[0],))
                quizQuestions.append((UserID,cursor.fetchall()[0]))
            connection.close()
            #The questions and answers for the quiz are queried

            allQuizQuestionsSingleplayers.append(quizQuestions)
            question = quizQuestions[0][1]
            question = list(question)
            questionIDOfQuestion = question[0]
            questionType=question[1]
            #when questions are stored in the database they are turned into strings before storing
            #Therefore array or a dictionary that is in a string needs to be converted back into an array or dictionary
            try:
                questions=eval(question[2])
            except:
                questions=question[2]
            try:
                answers=eval(question[3])
            except:
                answers=question[3]
            try:
                correctAnswer=eval(question[4])
            except:
                correctAnswer=question[4]
                
    if request.method == 'POST':
        quizQuestions=[]

        for singlePlayerQuizQuestion in allQuizQuestionsSingleplayers:
            if len(singlePlayerQuizQuestion)!=0:    #if quiz hasnt been completed
                if singlePlayerQuizQuestion[0][1][0] in questionIDs and UserID == singlePlayerQuizQuestion[0][0]:
                    #If the quiz question is for the current user then it is retrieved
                    quizQuestions = singlePlayerQuizQuestion
            else:
                quizQuestions = singlePlayerQuizQuestion

        if len(quizQuestions) == 0:
            #If quiz has been completed
            return redirect(url_for("quizSection.viewResults",QuizID=QuizID))
            
        question = quizQuestions[0][1]
        question = list(question)
        questionIDOfQuestion = question[0]
        questionType=question[1]
        #when questions are stored in the database they are turned into strings before storing
        #Therefore array or a dictionary that is in a string needs to be converted back into an array or dictionary
        try:
            questions=eval(question[2])
        except:
            questions=question[2]
        try:
            answers=eval(question[3])
        except:
            answers=question[3]
        try:
            correctAnswer=eval(question[4])
        except:
            correctAnswer=question[4]
        
        if request.form.get('NextQuestion') == 'Next Question':
            #If user presses button to move to next question
            for singlePlayerQuizQuestion in allQuizQuestionsSingleplayers:
                if len(singlePlayerQuizQuestion)!=0:    #If quiz hasn't been completed
                    if singlePlayerQuizQuestion[0][1][0] in questionIDs and UserID == singlePlayerQuizQuestion[0][0]:
                        allQuizQuestionsSingleplayers[allQuizQuestionsSingleplayers.index(singlePlayerQuizQuestion)].pop(0)
                        #The completed question is removed from the quiz
                        quizQuestions = singlePlayerQuizQuestion
                else:
                    quizQuestions = singlePlayerQuizQuestion

            if len(quizQuestions) == 0:
                #If quiz has been completed
                return redirect(url_for("quizSection.viewResults",QuizID=QuizID))

            question = quizQuestions[0][1]
            question = list(question)
            questionIDOfQuestion = question[0]
            questionType=question[1]
            #when questions are stored in the database they are turned into strings before storing
            #Therefore array or a dictionary that is in a string needs to be converted back into an array or dictionary
            try:
                questions=eval(question[2])
            except:
                questions=question[2]
            try:
                answers=eval(question[3])
            except:
                answers=question[3]
            try:
                correctAnswer=eval(question[4])
            except:
                correctAnswer=question[4]

            if questionType == 'MC':
                random.shuffle(answers)
            if questionType == 'QA':
                #The answers and questions are matched and assigned the same id
                #Therefore when validating if they have matching ids they are valid
                questionsAndIDs = []
                answersAndIDs = []

                for x in range(len(questions)):
                    questionID = x
                    question = questions[x]
                    questionsAndIDs.append((questionID,question))

                for x in questionsAndIDs:
                    for key,value in correctAnswer.items():
                        if x[1] == key:
                            answersAndIDs.append((x[0],value))

                random.shuffle(answersAndIDs)

                questions = questionsAndIDs
                answers = answersAndIDs

            return render_template("retakeQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=False,CorrectAnswer=correctAnswer,QuizID=QuizID,user=current_user)

        if questionType == 'MC':
            multipleChoiceAnswer = request.form.get('answer')
            #Answer recieved from the form
        
            if multipleChoiceAnswer == correctAnswer:
                #If the answer is correct
                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()

                cursor.execute("SELECT NumberOfTimesAnswered,NumberOfTimesAnsweredCorrectly FROM Question WHERE QuestionID=?",(questionIDOfQuestion,))
                questionInfo = cursor.fetchall()

                cursor.execute("UPDATE Question SET NumberOfTimesAnswered=?,NumberOfTimesAnsweredCorrectly=? WHERE QuestionID=?",(int(questionInfo[0][0])+1,int(questionInfo[0][1])+1,questionIDOfQuestion,))
                connection.commit()

                cursor.execute("SELECT NumberOfQuestionsAnsweredCorrectly FROM Quiz WHERE QuizID=?",(QuizID,))
                quizInfo = cursor.fetchall()

                cursor.execute("UPDATE Quiz SET NumberOfQuestionsAnsweredCorrectly=? WHERE QuizID=?",(int(quizInfo[0][0])+1,QuizID,))
                connection.commit()

                connection.close()
                #Database is updated with their new score
                flash('Correct',category='success')

                for singlePlayerQuizQuestion in allQuizQuestionsSingleplayers:
                    if len(singlePlayerQuizQuestion)!=0:    #If quiz hasn't been completed
                        if singlePlayerQuizQuestion[0][1][0] in questionIDs and UserID == singlePlayerQuizQuestion[0][0]:
                            allQuizQuestionsSingleplayers[allQuizQuestionsSingleplayers.index(singlePlayerQuizQuestion)].pop(0)
                            #The completed quiz is removed from the quiz
                            quizQuestions = singlePlayerQuizQuestion
                    else:
                        quizQuestions = singlePlayerQuizQuestion
                        
                if len(quizQuestions) == 0:
                    #If quiz has finished
                    return redirect(url_for("quizSection.viewResults",QuizID=QuizID))
                    
                question = quizQuestions[0][1]
                question = list(question)
                questionIDOfQuestion = question[0]
                questionType=question[1]
                #when questions are stored in the database they are turned into strings before storing
                #Therefore array or a dictionary that is in a string needs to be converted back into an array or dictionary
                try:
                    questions=eval(question[2])
                except:
                    questions=question[2]
                try:
                    answers=eval(question[3])
                except:
                    answers=question[3]
                try:
                    correctAnswer=eval(question[4])
                except:
                    correctAnswer=question[4]

                if questionType == 'MC':
                    random.shuffle(answers)
                if questionType == 'QA':
                    #The answers and questions are matched and assigned the same id
                    #Therefore when validating if they have matching ids they are valid
                    questionsAndIDs = []
                    answersAndIDs = []

                    for x in range(len(questions)):
                        questionID = x
                        question = questions[x]
                        questionsAndIDs.append((questionID,question))

                    for x in questionsAndIDs:
                        for key,value in correctAnswer.items():
                            if x[1] == key:
                                answersAndIDs.append((x[0],value))

                    random.shuffle(answersAndIDs)
                    questions = questionsAndIDs
                    answers = answersAndIDs

                return render_template("retakeQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=False,CorrectAnswer=correctAnswer,QuizID=QuizID,user=current_user)
            else:
                flash('Inorrect',category='error')

                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()

                cursor.execute("SELECT NumberOfTimesAnswered FROM Question WHERE QuestionID=?",(questionIDOfQuestion,))
                questionInfo = cursor.fetchall()
                cursor.execute("UPDATE Question SET NumberOfTimesAnswered=? WHERE QuestionID=?",(int(questionInfo[0][0])+1,questionIDOfQuestion,))
                connection.commit()
                connection.close()
                #Database is updated with the user's score
                return render_template("retakeQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=True,CorrectAnswer=correctAnswer,QuizID=QuizID,user=current_user)#if incorrect display correct answer and then go to next question

        if questionType == 'FB':
            answer = request.form.get('Answer')
            #Answer recieved from form
            if answer!=None:
                if answer.lower() == correctAnswer:
                    flash('correct',category='success')
                    
                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()

                    cursor.execute("SELECT NumberOfTimesAnswered,NumberOfTimesAnsweredCorrectly FROM Question WHERE QuestionID=?",(questionIDOfQuestion,))
                    questionInfo = cursor.fetchall()

                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=?,NumberOfTimesAnsweredCorrectly=? WHERE QuestionID=?",(int(questionInfo[0][0])+1,int(questionInfo[0][1])+1,questionIDOfQuestion,))
                    connection.commit()

                    cursor.execute("SELECT NumberOfQuestionsAnsweredCorrectly FROM Quiz WHERE QuizID=?",(QuizID,))
                    quizInfo = cursor.fetchall()

                    cursor.execute("UPDATE Quiz SET NumberOfQuestionsAnsweredCorrectly=? WHERE QuizID=?",(int(quizInfo[0][0])+1,QuizID,))
                    connection.commit()

                    connection.close()
                    #Database is updated with new score

                    for singlePlayerQuizQuestion in allQuizQuestionsSingleplayers:
                        if len(singlePlayerQuizQuestion)!=0:    #If quiz hasn't been completed
                            if singlePlayerQuizQuestion[0][1][0] in questionIDs and UserID == singlePlayerQuizQuestion[0][0]:
                                allQuizQuestionsSingleplayers[allQuizQuestionsSingleplayers.index(singlePlayerQuizQuestion)].pop(0)
                                #The completed question is removed from the quiz
                                quizQuestions = singlePlayerQuizQuestion
                        else:
                            quizQuestions = singlePlayerQuizQuestion
                    if len(quizQuestions) == 0:
                        #If quiz has been completed
                        return redirect(url_for("quizSection.viewResults",QuizID=QuizID))          
                        
                    question = quizQuestions[0][1]
                    question = list(question)
                    questionIDOfQuestion = question[0]
                    questionType=question[1]
                    #when questions are stored in the database they are turned into strings before storing
                    #Therefore array or a dictionary that is in a string needs to be converted back into an array or dictionary
                    try:
                        questions=eval(question[2])
                    except:
                        questions=question[2]
                    try:
                        answers=eval(question[3])
                    except:
                        answers=question[3]
                    try:
                        correctAnswer=eval(question[4])
                    except:
                        correctAnswer=question[4]

                    if questionType == 'MC':
                        random.shuffle(answers)
                    if questionType == 'QA':
                        #The answers and questions are matched and assigned the same id
                        #Therefore when validating if they have matching ids they are valid
                        questionsAndIDs = []
                        answersAndIDs = []

                        for x in range(len(questions)):
                            questionID = x
                            question = questions[x]
                            questionsAndIDs.append((questionID,question))

                        for x in questionsAndIDs:
                            for key,value in correctAnswer.items():
                                if x[1] == key:
                                    answersAndIDs.append((x[0],value))

                        random.shuffle(answersAndIDs)

                        questions = questionsAndIDs
                        answers = answersAndIDs

                    return render_template("retakeQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=False,CorrectAnswer=correctAnswer,QuizID=QuizID,user=current_user)
                else:
                    flash('Inorrect',category='error')

                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()

                    cursor.execute("SELECT NumberOfTimesAnswered FROM Question WHERE QuestionID=?",(questionIDOfQuestion,))
                    questionInfo = cursor.fetchall()
                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=? WHERE QuestionID=?",(int(questionInfo[0][0])+1,questionIDOfQuestion,))
                    connection.commit()
                    connection.close()
                    #Database is updated with new score
                    return render_template("retakeQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=True,CorrectAnswer=correctAnswer,QuizID=QuizID,user=current_user)#if incorrect display correct answer and then go to next question

        if questionType == 'SM':

            mistakeInAnswer=''
            correctAnswerToMistake=''

            for x in range(len(answers.split())):
                if answers.split()[x] != correctAnswer.split()[x]:
                    mistakeInAnswer = answers.split()[x]
                    correctAnswerToMistake = correctAnswer.split()[x]

            answer = request.form.get('incorrectWord')

            if answer != None:
                #If answer si not empty
                if answer.lower() == mistakeInAnswer:          
                    #If answer is corred
                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()

                    cursor.execute("SELECT NumberOfTimesAnswered,NumberOfTimesAnsweredCorrectly FROM Question WHERE QuestionID=?",(questionIDOfQuestion,))
                    questionInfo = cursor.fetchall()

                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=?,NumberOfTimesAnsweredCorrectly=? WHERE QuestionID=?",(int(questionInfo[0][0])+1,int(questionInfo[0][1])+1,questionIDOfQuestion,))
                    connection.commit()

                    cursor.execute("SELECT NumberOfQuestionsAnsweredCorrectly FROM Quiz WHERE QuizID=?",(QuizID,))
                    quizInfo = cursor.fetchall()

                    cursor.execute("UPDATE Quiz SET NumberOfQuestionsAnsweredCorrectly=? WHERE QuizID=?",(int(quizInfo[0][0])+1,QuizID,))
                    connection.commit()

                    connection.close()
                    #Database is updated with new score
                    flash('Correct',category='success')

                    for singlePlayerQuizQuestion in allQuizQuestionsSingleplayers:
                        if len(singlePlayerQuizQuestion)!=0:    #If quiz hasn't been completed
                            if singlePlayerQuizQuestion[0][1][0] in questionIDs and UserID == singlePlayerQuizQuestion[0][0]:
                                allQuizQuestionsSingleplayers[allQuizQuestionsSingleplayers.index(singlePlayerQuizQuestion)].pop(0)
                                #The completed question is removed from the quiz
                                quizQuestions = singlePlayerQuizQuestion
                        else:
                            quizQuestions = singlePlayerQuizQuestion

                    if len(quizQuestions) == 0:
                        #If quiz has been completed
                        return redirect(url_for("quizSection.viewResults",QuizID=QuizID))

                    question = quizQuestions[0][1]
                    question = list(question)
                    questionIDOfQuestion = question[0]
                    questionType=question[1]
                    #when questions are stored in the database they are turned into strings before storing
                    #Therefore array or a dictionary that is in a string needs to be converted back into an array or dictionary
                    try:
                        questions=eval(question[2])
                    except:
                        questions=question[2]
                    try:
                        answers=eval(question[3])
                    except:
                        answers=question[3]
                    try:
                        correctAnswer=eval(question[4])
                    except:
                        correctAnswer=question[4]

                    if questionType == 'MC':
                        random.shuffle(answers)
                    if questionType == 'QA':
                        #The answers and questions are matched and assigned the same id
                        #Therefore when validating if they have matching ids they are valid

                        questionsAndIDs = []
                        answersAndIDs = []

                        for x in range(len(questions)):
                            questionID = x
                            question = questions[x]
                            questionsAndIDs.append((questionID,question))

                        for x in questionsAndIDs:
                            for key,value in correctAnswer.items():
                                if x[1] == key:
                                    answersAndIDs.append((x[0],value))

                        random.shuffle(answersAndIDs)

                        questions = questionsAndIDs
                        answers = answersAndIDs

                    return render_template("retakeQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=False,CorrectAnswer=correctAnswer,QuizID=QuizID,user=current_user)
                else:
                    flash('Inorrect',category='error')
                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()

                    cursor.execute("SELECT NumberOfTimesAnswered FROM Question WHERE QuestionID=?",(questionIDOfQuestion,))
                    questionInfo = cursor.fetchall()

                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=? WHERE QuestionID=?",(int(questionInfo[0][0])+1,questionIDOfQuestion,))
                    connection.commit()
                    connection.close()
                    #Database is updated with new score

                    return render_template("retakeQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=True,CorrectAnswer=correctAnswerToMistake,QuizID=QuizID,user=current_user)#if incorrect display correct answer and then go to next question

        if questionType == 'QA':

            if request.form.get('Box0') == '0' and request.form.get('Box1') == '1' and request.form.get('Box2') == '2':      
                flash('Correct',category='success')
                #If answer is correct

                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()

                cursor.execute("SELECT NumberOfTimesAnswered,NumberOfTimesAnsweredCorrectly FROM Question WHERE QuestionID=?",(questionIDOfQuestion,))
                questionInfo = cursor.fetchall()

                cursor.execute("UPDATE Question SET NumberOfTimesAnswered=?,NumberOfTimesAnsweredCorrectly=? WHERE QuestionID=?",(int(questionInfo[0][0])+1,int(questionInfo[0][1])+1,questionIDOfQuestion,))
                connection.commit()

                cursor.execute("SELECT NumberOfQuestionsAnsweredCorrectly FROM Quiz WHERE QuizID=?",(QuizID,))
                quizInfo = cursor.fetchall()

                cursor.execute("UPDATE Quiz SET NumberOfQuestionsAnsweredCorrectly=? WHERE QuizID=?",(int(quizInfo[0][0])+1,QuizID,))
                connection.commit()

                connection.close()
                #Database is updated with new score

                for singlePlayerQuizQuestion in allQuizQuestionsSingleplayers:
                    if len(singlePlayerQuizQuestion)!=0:    #If quiz hasn't been completed
                        if singlePlayerQuizQuestion[0][1][0] in questionIDs and UserID == singlePlayerQuizQuestion[0][0]:
                            allQuizQuestionsSingleplayers[allQuizQuestionsSingleplayers.index(singlePlayerQuizQuestion)].pop(0)
                            #The completed question is removed from the quiz
                            quizQuestions = singlePlayerQuizQuestion
                    else:
                        quizQuestions = singlePlayerQuizQuestion

                if len(quizQuestions) == 0:
                    #If quiz has been completed
                    return redirect(url_for("quizSection.viewResults",QuizID=QuizID))                  
                    
                question = quizQuestions[0][1]
                question = list(question)
                questionIDOfQuestion = question[0]
                questionType=question[1]
                #when questions are stored in the database they are turned into strings before storing
                #Therefore array or a dictionary that is in a string needs to be converted back into an array or dictionary
                try:
                    questions=eval(question[2])
                except:
                    questions=question[2]
                try:
                    answers=eval(question[3])
                except:
                    answers=question[3]
                try:
                    correctAnswer=eval(question[4])
                except:
                    correctAnswer=question[4]

                if questionType == 'MC':
                    random.shuffle(answers)
                if questionType == 'QA':
                    #The answers and questions are matched and assigned the same id
                    #Therefore when validating if they have matching ids they are valid
                    questionsAndIDs = []
                    answersAndIDs = []

                    for x in range(len(questions)):
                        questionID = x
                        question = questions[x]
                        questionsAndIDs.append((questionID,question))

                    for x in questionsAndIDs:
                        for key,value in correctAnswer.items():
                            if x[1] == key:
                                answersAndIDs.append((x[0],value))

                    random.shuffle(answersAndIDs)

                    questions = questionsAndIDs
                    answers = answersAndIDs

                return render_template("retakeQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=False,CorrectAnswer=correctAnswer,QuizID=QuizID,user=current_user)
            
            else:
                flash("incorrect",category='error')

                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()
                cursor.execute("SELECT NumberOfTimesAnswered FROM Question WHERE QuestionID=?",(questionIDOfQuestion,))
                questionInfo = cursor.fetchall()
                cursor.execute("UPDATE Question SET NumberOfTimesAnswered=? WHERE QuestionID=?",(int(questionInfo[0][0])+1,questionIDOfQuestion,))
                connection.commit()
                connection.close()
                #Database is updated with new score

                return render_template("retakeQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=True,CorrectAnswer=correctAnswer,QuizID=QuizID,user=current_user)#if incorrect display correct answer and then go to next question

    return render_template("retakeQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=False,CorrectAnswer=correctAnswer,QuizID=QuizID,user=current_user)



@quizSection.route('/multiplayerQuiz/<QuizID>',  methods=['GET', 'POST'])
@login_required
def multiplayerQuiz(QuizID):
    UserID=current_user.get_id()

    QuizID = int(QuizID)
    questionIDs = []

    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()

    cursor.execute("SELECT QuestionID FROM QuizQuestions WHERE QuizID=?",(str(QuizID),))

    questionIDsFromQuiz = cursor.fetchall()
    #The question ids associated with the quiz are queried
    for x in questionIDsFromQuiz:
        questionIDs.append(x[0])
    connection.close()
    if request.method == 'GET':
        quizExists = False
        for multiPlayerQuizQuestion in allQuizQuestionsMultiplayer:
            if multiPlayerQuizQuestion[0][1][0] in questionIDs and UserID == multiPlayerQuizQuestion[0][0]:
                #looks for multiplayer quiz associated with current user
                quizQuestions = multiPlayerQuizQuestion
                quizExists = True
                #If user has an incomplete quiz that they are already taking then the quiz is returned

        if quizExists == True:
            question = quizQuestions[0][1]
            question = list(question)
            questionType=question[1]
            #when questions are stored in the database they are turned into strings before storing
            #Therefore array or a dictionary that is in a string needs to be converted back into an array or dictionary
            try:
                questions=eval(question[2])
            except:
                questions=question[2]
            try:
                answers=eval(question[3])
            except:
                answers=question[3]
            try:
                correctAnswer=eval(question[4])
            except:
                correctAnswer=question[4]
        else:

            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()
            cursor.execute("SELECT QuestionID FROM QuizQuestions WHERE QuizID=?",(str(QuizID),))
            questionIDsFromQuiz = cursor.fetchall()
            #Questions are queried

            quizQuestions = []        

            for x in questionIDsFromQuiz:
                cursor.execute("SELECT QuestionID,QuestionType,Question,Answer,CorrectAnswer FROM Question WHERE QuestionID=?",(x[0],))
                quizQuestions.append((UserID,cursor.fetchall()[0]))
            #Questions are queried for each question in the quiz
            connection.close()
            allQuizQuestionsMultiplayer.append(quizQuestions)
            question = quizQuestions[0][1]
            question = list(question)
            questionType=question[1]
            #when questions are stored in the database they are turned into strings before storing
            #Therefore array or a dictionary that is in a string needs to be converted back into an array or dictionary
            try:
                questions=eval(question[2])
            except:
                questions=question[2]
            try:
                answers=eval(question[3])
            except:
                answers=question[3]
            try:
                correctAnswer=eval(question[4])
            except:
                correctAnswer=question[4]
                
    if request.method == 'POST':
        quizQuestions=[]

        for multiPlayerQuizQuestion in allQuizQuestionsMultiplayer:
            if len(multiPlayerQuizQuestion)!=0:#if quiz hasnt been completed
                if multiPlayerQuizQuestion[0][1][0] in questionIDs and UserID == multiPlayerQuizQuestion[0][0]:
                    #looks for multiplayer quiz associated with current user
                    quizQuestions = multiPlayerQuizQuestion
            else:
                quizQuestions = multiPlayerQuizQuestion

        if len(quizQuestions) == 0:
            #If quiz has been completed
            return render_template('quizEnd.html')

        question = quizQuestions[0][1]
        question = list(question)
        questionType=question[1]
        #when questions are stored in the database they are turned into strings before storing
        #Therefore array or a dictionary that is in a string needs to be converted back into an array or dictionary
        try:
            questions=eval(question[2])
        except:
            questions=question[2]
        try:
            answers=eval(question[3])
        except:
            answers=question[3]
        try:
            correctAnswer=eval(question[4])
        except:
            correctAnswer=question[4]
        
        if request.form.get('DisplayAnswer') == 'True':

            for multiPlayerQuizQuestion in allQuizQuestionsMultiplayer:
                if len(multiPlayerQuizQuestion)!=0:
                    if multiPlayerQuizQuestion[0][1][0] in questionIDs and UserID == multiPlayerQuizQuestion[0][0]:
                        #looks for multiplayer quiz associated with current user
                        allQuizQuestionsMultiplayer[allQuizQuestionsMultiplayer.index(multiPlayerQuizQuestion)].pop(0)
                        #completed question is removed from array
                        quizQuestions = multiPlayerQuizQuestion
                else:
                    quizQuestions = multiPlayerQuizQuestion


            if len(quizQuestions) == 0:
                #If quiz has been completed
                userScores.pop(UserID)
                return render_template('quizEnd.html')
                
            question = quizQuestions[0][1]
            question = list(question)
            questionType=question[1]
            #when questions are stored in the database they are turned into strings before storing
            #Therefore array or a dictionary that is in a string needs to be converted back into an array or dictionary
            try:
                questions=eval(question[2])
            except:
                questions=question[2]
            try:
                answers=eval(question[3])
            except:
                answers=question[3]
            try:
                correctAnswer=eval(question[4])
            except:
                correctAnswer=question[4]

            if questionType == 'MC':
                random.shuffle(answers)
            if questionType == 'QA':
                #The answers and questions are matched and assigned the same id
                #Therefore when validating if they have matching ids they are valid

                questionsAndIDs = []
                answersAndIDs = []

                for x in range(len(questions)):
                    questionID = x
                    question = questions[x]
                    questionsAndIDs.append((questionID,question))

                for x in questionsAndIDs:
                    for key,value in correctAnswer.items():
                        if x[1] == key:
                            answersAndIDs.append((x[0],value))

                random.shuffle(answersAndIDs)

                questions = questionsAndIDs
                answers = answersAndIDs

            return render_template("multiplayerQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=False,CorrectAnswer=correctAnswer,QuizID=QuizID)

        if questionType == 'MC': 
            multipleChoiceAnswer = request.form.get('answer')
        
            if multipleChoiceAnswer == correctAnswer:
                #If answer is correct
                flash('Correct',category='success')
                currentScore = userScores.get(UserID)
                if currentScore != None:
                    newScore = currentScore+1
                    userScores.update({UserID:newScore})

                for multiPlayerQuizQuestion in allQuizQuestionsMultiplayer:
                    if len(multiPlayerQuizQuestion)!=0:
                        if multiPlayerQuizQuestion[0][1][0] in questionIDs and UserID == multiPlayerQuizQuestion[0][0]:
                            #looks for multiplayer quiz associated with current user
                            allQuizQuestionsMultiplayer[allQuizQuestionsMultiplayer.index(multiPlayerQuizQuestion)].pop(0)
                            #completed question is removed from array
                            
                            quizQuestions = multiPlayerQuizQuestion
                    else:
                        quizQuestions = multiPlayerQuizQuestion
                        
                if len(quizQuestions) == 0:
                    #If quiz has been completed
                    userScores.pop(UserID)
                    return render_template('quizEnd.html')#clear scores    
                    
                question = quizQuestions[0][1]
                question = list(question)
                questionType=question[1]
                #when questions are stored in the database they are turned into strings before storing
                #Therefore array or a dictionary that is in a string needs to be converted back into an array or dictionary
                try:
                    questions=eval(question[2])
                except:
                    questions=question[2]
                try:
                    answers=eval(question[3])
                except:
                    answers=question[3]
                try:
                    correctAnswer=eval(question[4])
                except:
                    correctAnswer=question[4]

                if questionType == 'MC':
                    random.shuffle(answers)
                if questionType == 'QA':
                    #The answers and questions are matched and assigned the same id
                    #Therefore when validating if they have matching ids they are valid

                    questionsAndIDs = []
                    answersAndIDs = []
                    for x in range(len(questions)):
                        questionID = x
                        question = questions[x]
                        questionsAndIDs.append((questionID,question))

                    for x in questionsAndIDs:
                        for key,value in correctAnswer.items():
                            if x[1] == key:
                                answersAndIDs.append((x[0],value))

                    random.shuffle(answersAndIDs)

                    questions = questionsAndIDs
                    answers = answersAndIDs

                return render_template("multiplayerQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=False,CorrectAnswer=correctAnswer,QuizID=QuizID)
            else:
                flash('Inorrect',category='error')
                return render_template("multiplayerQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=True,CorrectAnswer=correctAnswer,QuizID=QuizID)#if incorrect display correct answer and then go to next question

        if questionType == 'FB':
            answer = request.form.get('Answer')
            if answer!=None:
                #If answer is not empty
                if answer.lower() == correctAnswer:
                    #If answer is correct
                    flash('correct',category='success')
                    
                    currentScore = userScores.get(UserID)
                    if currentScore != None:
                        newScore = currentScore+1
                        userScores.update({UserID:newScore})

                    for multiPlayerQuizQuestion in allQuizQuestionsMultiplayer:
                        if len(multiPlayerQuizQuestion)!=0:
                            if multiPlayerQuizQuestion[0][1][0] in questionIDs and UserID == multiPlayerQuizQuestion[0][0]:
                                #looks for multiplayer quiz associated with current user
                                allQuizQuestionsMultiplayer[allQuizQuestionsMultiplayer.index(multiPlayerQuizQuestion)].pop(0)
                                #completed question is removed from array
                                
                                quizQuestions = multiPlayerQuizQuestion
                        else:
                            quizQuestions = multiPlayerQuizQuestion
                    if len(quizQuestions) == 0:
                        #If quiz has been completed
                        userScores.pop(UserID)
                        return render_template('quizEnd.html')          
 
                    question = quizQuestions[0][1]
                    question = list(question)
                    questionType=question[1]
                    #when questions are stored in the database they are turned into strings before storing
                    #Therefore array or a dictionary that is in a string needs to be converted back into an array or dictionary
                    try:
                        questions=eval(question[2])
                    except:
                        questions=question[2]
                    try:
                        answers=eval(question[3])
                    except:
                        answers=question[3]
                    try:
                        correctAnswer=eval(question[4])
                    except:
                        correctAnswer=question[4]
                    if questionType == 'MC':
                        random.shuffle(answers)
                    if questionType == 'QA':
                        #The answers and questions are matched and assigned the same id
                        #Therefore when validating if they have matching ids they are valid
                        questionsAndIDs = []
                        answersAndIDs = []

                        for x in range(len(questions)):
                            questionID = x
                            question = questions[x]
                            questionsAndIDs.append((questionID,question))

                        for x in questionsAndIDs:
                            for key,value in correctAnswer.items():
                                if x[1] == key:
                                    answersAndIDs.append((x[0],value))

                        random.shuffle(answersAndIDs)

                        questions = questionsAndIDs
                        answers = answersAndIDs

                    return render_template("multiplayerQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=False,CorrectAnswer=correctAnswer,QuizID=QuizID)
                else:
                    flash('Inorrect',category='error')

                    return render_template("multiplayerQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=True,CorrectAnswer=correctAnswer,QuizID=QuizID)#if incorrect display correct answer and then go to next question

        if questionType == 'SM':

            mistakeInAnswer=''
            correctAnswerToMistake=''

            for x in range(len(answers.split())):
                if answers.split()[x] != correctAnswer.split()[x]:
                    mistakeInAnswer = answers.split()[x]
                    correctAnswerToMistake = correctAnswer.split()[x]

            answer = request.form.get('incorrectWord')

            if answer != None:
                #If answer is not empty
                if answer.lower() == mistakeInAnswer:
                    #If answer is correct   
                    flash('Correct',category='success')
                    currentScore = userScores.get(UserID)
                    
                    if currentScore != None:
                        newScore = currentScore+1
                        userScores.update({UserID:newScore})

                    for multiPlayerQuizQuestion in allQuizQuestionsMultiplayer:
                        if len(multiPlayerQuizQuestion)!=0:
                            if multiPlayerQuizQuestion[0][1][0] in questionIDs and UserID == multiPlayerQuizQuestion[0][0]:
                                #looks for multiplayer quiz associated with current user
                                allQuizQuestionsMultiplayer[allQuizQuestionsMultiplayer.index(multiPlayerQuizQuestion)].pop(0)
                                #completed question is removed from array
                                quizQuestions = multiPlayerQuizQuestion
                        else:
                            quizQuestions = multiPlayerQuizQuestion

                    if len(quizQuestions) == 0:
                        #If quiz has been completed
                        userScores.pop(UserID)
                        return render_template('quizEnd.html')

                    question = quizQuestions[0][1]
                    question = list(question)
                    questionType=question[1]
                    #when questions are stored in the database they are turned into strings before storing
                    #Therefore array or a dictionary that is in a string needs to be converted back into an array or dictionary
                    try:
                        questions=eval(question[2])
                    except:
                        questions=question[2]
                    try:
                        answers=eval(question[3])
                    except:
                        answers=question[3]
                    try:
                        correctAnswer=eval(question[4])
                    except:
                        correctAnswer=question[4]

                    if questionType == 'MC':
                        random.shuffle(answers)
                    if questionType == 'QA':
                        #The answers and questions are matched and assigned the same id
                        #Therefore when validating if they have matching ids they are valid

                        questionsAndIDs = []
                        answersAndIDs = []

                        for x in range(len(questions)):
                            questionID = x
                            question = questions[x]
                            questionsAndIDs.append((questionID,question))

                        for x in questionsAndIDs:
                            for key,value in correctAnswer.items():
                                if x[1] == key:
                                    answersAndIDs.append((x[0],value))

                        random.shuffle(answersAndIDs)

                        questions = questionsAndIDs
                        answers = answersAndIDs

                    return render_template("multiplayerQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=False,CorrectAnswer=correctAnswer,QuizID=QuizID)
                else:
                    flash('Inorrect',category='error')
                    return render_template("multiplayerQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=True,CorrectAnswer=correctAnswerToMistake,QuizID=QuizID)#if incorrect display correct answer and then go to next question

        if questionType == 'QA':

            if request.form.get('Box0') == '0' and request.form.get('Box1') == '1' and request.form.get('Box2') == '2':      
                flash('Correct',category='success')
                #If answer is correct
                currentScore = userScores.get(UserID)
                
                if currentScore != None:
                    newScore = currentScore+1
                    userScores.update({UserID:newScore})

                for multiPlayerQuizQuestion in allQuizQuestionsMultiplayer:
                    if len(multiPlayerQuizQuestion)!=0:
                        if multiPlayerQuizQuestion[0][1][0] in questionIDs and UserID == multiPlayerQuizQuestion[0][0]:
                            #looks for multiplayer quiz associated with current user
                            allQuizQuestionsMultiplayer[allQuizQuestionsMultiplayer.index(multiPlayerQuizQuestion)].pop(0)
                            #completed question is removed from array
                            quizQuestions = multiPlayerQuizQuestion
                    else:
                        quizQuestions = multiPlayerQuizQuestion

                if len(quizQuestions) == 0:
                    #If quiz has been completed
                    userScores.pop(UserID)
                    return render_template('quizEnd.html')                    
                    
                question = quizQuestions[0][1]
                question = list(question)
                questionType=question[1]
                #when questions are stored in the database they are turned into strings before storing
                #Therefore array or a dictionary that is in a string needs to be converted back into an array or dictionary
                try:
                    questions=eval(question[2])
                except:
                    questions=question[2]

                try:
                    answers=eval(question[3])
                except:
                    answers=question[3]

                try:
                    correctAnswer=eval(question[4])
                except:
                    correctAnswer=question[4]

                if questionType == 'MC':
                    random.shuffle(answers)
                if questionType == 'QA':
                    #The answers and questions are matched and assigned the same id
                    #Therefore when validating if they have matching ids they are valid
                    questionsAndIDs = []
                    answersAndIDs = []

                    for x in range(len(questions)):
                        questionID = x
                        question = questions[x]
                        questionsAndIDs.append((questionID,question))

                    for x in questionsAndIDs:
                        for key,value in correctAnswer.items():
                            if x[1] == key:
                                answersAndIDs.append((x[0],value))

                    random.shuffle(answersAndIDs)

                    questions = questionsAndIDs
                    answers = answersAndIDs

                return render_template("multiplayerQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=False,CorrectAnswer=correctAnswer,QuizID=QuizID)
            else:

                return render_template("multiplayerQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=True,CorrectAnswer=correctAnswer,QuizID=QuizID)#if incorrect display correct answer and then go to next question

    return render_template("multiplayerQuiz.html",QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=False,CorrectAnswer=correctAnswer,QuizID=QuizID)



@quizSection.route('/chooseDeckToQuizOn',  methods=['GET', 'POST'])
@login_required
def quizMenchooseDeckToQuizOn():
    #Redirects to page which allow the user to choose the flashcard deck to take the quiz on
    return redirect(url_for("flashcardsSection.chooseFlashcardDeckToManage",pageToDisplay='TakeQuiz'))



@quizSection.route('/TakeQuiz/<DeckName>',  methods=['GET', 'POST'])
@login_required
def TakeQuiz(DeckName):
    UserID=current_user.get_id()

    if request.method == "POST":
        numberOfQuestions = request.form.get('number')

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("""  SELECT COUNT(Flashcard.FlashcardID)
                            FROM Flashcard,FlashcardsDecksAndUserIDs,ParentFlashcardDeck
                            WHERE FlashcardsDecksAndUserIDs.UserID=?
                            AND FlashcardsDecksAndUserIDs.FlashcardID=Flashcard.FlashcardID
                            AND ParentFlashcardDeck.FlashcardDeckName=?
                            AND ParentFlashcardDeck.ParentFlashcardDeckID=FlashcardsDecksAndUserIDs.ParentFlashcardDeckID
        
        """,(UserID,DeckName,))

        numerOfFlashcards = cursor.fetchall()
        #Number of flashcards are queried assuming deck name is a parent deck

        if numerOfFlashcards[0][0] == 0:
            #If deck name is not a parent deck
            cursor.execute("""  SELECT COUNT(Flashcard.FlashcardID)
                    FROM Flashcard,FlashcardsDecksAndUserIDs,FlashcardDeck
                    WHERE FlashcardsDecksAndUserIDs.UserID=?
                    AND FlashcardsDecksAndUserIDs.FlashcardID=Flashcard.FlashcardID
                    AND FlashcardDeck.FlashcardDeckName=?
                    AND FlashcardDeck.FlashcardDeckID=FlashcardsDecksAndUserIDs.FlashcardDeckID""",(UserID,DeckName,))
            numerOfFlashcards = cursor.fetchall()
            #Number of flashcards in the deck are queried
        connection.close()

        if int(numberOfQuestions) > int(numerOfFlashcards[0][0]):
            flash(f'The Maximum number of questions for the deck you have chosen is {numerOfFlashcards[0][0]}',category='error')
            return render_template("chooseQuizSize.html",user=current_user)
        
        return redirect(url_for("quizSection.quiz",DeckName=DeckName,numberOfQuestions=numberOfQuestions))

    return render_template("chooseQuizSize.html",user=current_user)



@quizSection.route('/quiz/<DeckName>/<numberOfQuestions>',  methods=['GET', 'POST'])
@login_required
def quiz(DeckName,numberOfQuestions):
    UserQuiz = ''
    UserID= current_user.get_id()
    if request.method == 'GET':
        #If the page is loaded

        for x in range(len(userAndQuizObjects)):
            IdOfUser = userAndQuizObjects[x][0]
            if IdOfUser == UserID:
                userAndQuizObjects.pop(x)
                #If the user has a quiz on going then it is overridden with new quiz
        UserQuiz = Quiz(UserID,DeckName,numberOfQuestions)
        #Quiz object is created
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("INSERT INTO Quiz(QuizID,NumberOfQuestions,NumberOfQuestionsAnsweredCorrectly,DeckName) values(?,?,?,?)",(UserQuiz.getQuizID(),numberOfQuestions,0,DeckName))
        connection.commit()
        connection.close()
        #Database is updated with the details of the new quiz
        currentQuestion = UserQuiz.nextQuestion()
        questionType = currentQuestion.getQuestionType()
        correctAnswer = currentQuestion.getCorrectAnswer()
        questions = currentQuestion.getQuestion()
        answers = currentQuestion.getAnswer()
        #Next question and answer is returned

        if questionType == 'QA':
            #The answers and questions are matched and assigned the same id
            #Therefore when validating if they have matching ids they are valid
            questionsAndIDs = []
            answersAndIDs = []

            for x in range(len(questions)):
                questionID = x
                question = questions[x]
                questionsAndIDs.append((questionID,question))

            for x in range(len(answers)):
                AnswerID = x
                answer = answers[x]
                answersAndIDs.append((AnswerID,answer))

            questions = questionsAndIDs
            answers = answersAndIDs

        UserAndQuizObject = (UserID,UserQuiz)
        userAndQuizObjects.append(UserAndQuizObject)

    if request.method == 'POST':

        for UserAndQuizObject in userAndQuizObjects:
            if UserAndQuizObject[0]==UserID:    #If the quiz object that belongs to the use is returned
                UserQuiz = UserAndQuizObject[1]

        if UserQuiz.getCompletedQuestions().size() == 0:
            currentQuestion = UserQuiz.getQuestions().peek()
        else:
            currentQuestion = UserQuiz.getCompletedQuestions().peek()

        questionType = currentQuestion.getQuestionType()
        questions = currentQuestion.getQuestion()
        answers = currentQuestion.getAnswer()
        correctAnswer = currentQuestion.getCorrectAnswer()
        #Next question and answer is returned
        
        if request.form.get('NextQuestion') == 'Next Question':
            if UserQuiz.getQuestions().size() == 0:   #If all questions have been used (Quiz finished)
                count=0
                QuizID = None
                for UserAndQuizObject in userAndQuizObjects:
                    if UserAndQuizObject[0]==UserID:    #If the quiz object that belongs to the use is returned
                        QuizID = UserAndQuizObject[1].getQuizID()
                        userAndQuizObjects.pop(count)   #Quiz object is removed as quiz has been completed
                    count+=1
                return redirect(url_for("quizSection.viewResults",QuizID=QuizID))
                #Display results to the user

            currentQuestion = UserQuiz.nextQuestion()
            questionType = currentQuestion.getQuestionType()
            questions = currentQuestion.getQuestion()
            answers = currentQuestion.getAnswer()
            correctAnswer = currentQuestion.getCorrectAnswer()
            #Next question and answer is returned
            if questionType == 'MC':
                random.shuffle(answers)
            if questionType == 'QA':
                #The answers and questions are matched and assigned the same id
                #Therefore when validating if they have matching ids they are valid
                questionsAndIDs = []
                answersAndIDs = []

                for x in range(len(questions)):
                    questionID = x
                    question = questions[x]
                    questionsAndIDs.append((questionID,question))

                for x in questionsAndIDs:
                    for key,value in correctAnswer.items():
                        if x[1] == key:
                            answersAndIDs.append((x[0],value))

                random.shuffle(answersAndIDs)

                questions = questionsAndIDs
                answers = answersAndIDs

            return render_template("singlePlayerQuiz.html",user=current_user,QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=False,CorrectAnswer=correctAnswer)

        if questionType == 'MC':
            multipleChoiceAnswer = request.form.get('answer')
            if request.form.get('Choose') == 'Submit':
                if multipleChoiceAnswer == correctAnswer:
                    flash('Correct',category='success')

                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()

                    cursor.execute("SELECT NumberOfTimesAnswered,NumberOfTimesAnsweredCorrectly FROM Question WHERE QuestionID=?",(str(currentQuestion.getQuestionID()),))
                    questionInfo = cursor.fetchall()

                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=?,NumberOfTimesAnsweredCorrectly=? WHERE QuestionID=?",(int(questionInfo[0][0])+1,int(questionInfo[0][1])+1,str(currentQuestion.getQuestionID()),))
                    connection.commit()
                    
                    cursor.execute("SELECT NumberOfQuestionsAnsweredCorrectly FROM Quiz WHERE QuizID=?",(str(UserQuiz.getQuizID()),))
                    quizInfo = cursor.fetchall()

                    cursor.execute("UPDATE Quiz SET NumberOfQuestionsAnsweredCorrectly=? WHERE QuizID=?",(int(quizInfo[0][0])+1,str(UserQuiz.getQuizID()),))
                    connection.commit()

                    connection.close()

                    if UserQuiz.getQuestions().size() == 0:   #If all questions have been used (Quiz finished)
                        count=0
                        QuizID = None
                        for UserAndQuizObject in userAndQuizObjects:
                            if UserAndQuizObject[0]==UserID:    #If the quiz object that belongs to the use is returned
                                QuizID = UserAndQuizObject[1].getQuizID()
                                userAndQuizObjects.pop(count)   #Quiz object is removed as quiz has been completed
                            count+=1
                        return redirect(url_for("quizSection.viewResults",QuizID=QuizID))
                        #Display results to the user

                    currentQuestion = UserQuiz.nextQuestion()
                    questionType = currentQuestion.getQuestionType()
                    questions = currentQuestion.getQuestion()
                    answers = currentQuestion.getAnswer()
                    correctAnswer = currentQuestion.getCorrectAnswer()
                    #Next question and answer is returned

                    if questionType == 'MC':
                        random.shuffle(answers)
                    if questionType == 'QA':
                    #The answers and questions are matched and assigned the same id
                    #Therefore when validating if they have matching ids they are valid
                        questionsAndIDs = []
                        answersAndIDs = []

                        for x in range(len(questions)):
                            questionID = x
                            question = questions[x]
                            questionsAndIDs.append((questionID,question))

                        for x in questionsAndIDs:
                            for key,value in correctAnswer.items():
                                if x[1] == key:
                                    answersAndIDs.append((x[0],value))

                        random.shuffle(answersAndIDs)

                        questions = questionsAndIDs
                        answers = answersAndIDs

                    return render_template("singlePlayerQuiz.html",user=current_user,QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=False,CorrectAnswer=correctAnswer)
                else:
                    flash('Inorrect',category='error')

                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()

                    cursor.execute("SELECT NumberOfTimesAnswered FROM Question WHERE QuestionID=?",(str(currentQuestion.getQuestionID()),))
                    questionInfo = cursor.fetchall()

                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=? WHERE QuestionID=?",(int(questionInfo[0][0])+1,str(currentQuestion.getQuestionID()),))
                    connection.commit()
                    connection.close()

                    return render_template("singlePlayerQuiz.html",user=current_user,QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=True,CorrectAnswer=correctAnswer)#if incorrect display correct answer and then go to next question

        if questionType == 'FB':
            answer = request.form.get('Answer')
            if answer!=None:
                if answer.lower() == correctAnswer:
                    flash('Correct',category='success')

                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()

                    cursor.execute("SELECT NumberOfTimesAnswered,NumberOfTimesAnsweredCorrectly FROM Question WHERE QuestionID=?",(str(currentQuestion.getQuestionID()),))
                    questionInfo = cursor.fetchall()

                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=?,NumberOfTimesAnsweredCorrectly=? WHERE QuestionID=?",(int(questionInfo[0][0])+1,int(questionInfo[0][1])+1,str(currentQuestion.getQuestionID()),))
                    connection.commit()

                    cursor.execute("SELECT NumberOfQuestionsAnsweredCorrectly FROM Quiz WHERE QuizID=?",(str(UserQuiz.getQuizID()),))
                    quizInfo = cursor.fetchall()

                    cursor.execute("UPDATE Quiz SET NumberOfQuestionsAnsweredCorrectly=? WHERE QuizID=?",(int(quizInfo[0][0])+1,str(UserQuiz.getQuizID()),))
                    connection.commit()

                    connection.close()

                    if UserQuiz.getQuestions().size() == 0:   #If all questions have been used (Quiz finished)
                        count=0
                        QuizID = None
                        for UserAndQuizObject in userAndQuizObjects:
                            if UserAndQuizObject[0]==UserID:    #If the quiz object that belongs to the use is returned
                                QuizID = UserAndQuizObject[1].getQuizID()
                                userAndQuizObjects.pop(count)   #Quiz object is removed as quiz has been completed
                            count+=1
                        return redirect(url_for("quizSection.viewResults",QuizID=QuizID))
                        #Display results to the user

                    currentQuestion = UserQuiz.nextQuestion()
                    questionType = currentQuestion.getQuestionType()
                    questions = currentQuestion.getQuestion()
                    answers = currentQuestion.getAnswer()
                    correctAnswer = currentQuestion.getCorrectAnswer()
                    #Next question and answer is returned

                    if questionType == 'MC':
                        random.shuffle(answers)
                    if questionType == 'QA':
                    #The answers and questions are matched and assigned the same id
                    #Therefore when validating if they have matching ids they are valid
                        questionsAndIDs = []
                        answersAndIDs = []

                        for x in range(len(questions)):
                            questionID = x
                            question = questions[x]
                            questionsAndIDs.append((questionID,question))

                        for x in questionsAndIDs:
                            for key,value in correctAnswer.items():
                                if x[1] == key:
                                    answersAndIDs.append((x[0],value))

                        random.shuffle(answersAndIDs)

                        questions = questionsAndIDs
                        answers = answersAndIDs

                    return render_template("singlePlayerQuiz.html",user=current_user,QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=False,CorrectAnswer=correctAnswer)
                else:
                    flash('Inorrect',category='error')

                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()

                    cursor.execute("SELECT NumberOfTimesAnswered FROM Question WHERE QuestionID=?",(str(currentQuestion.getQuestionID()),))
                    questionInfo = cursor.fetchall()

                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=? WHERE QuestionID=?",(int(questionInfo[0][0])+1,str(currentQuestion.getQuestionID()),))
                    connection.commit()
                    connection.close()

                    return render_template("singlePlayerQuiz.html",user=current_user,QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=True,CorrectAnswer=correctAnswer)#if incorrect display correct answer and then go to next question

        if questionType == 'SM':

            mistakeInAnswer=''
            correctAnswerToMistake=''

            for x in range(len(answers.split())):
                if answers.split()[x] != correctAnswer.split()[x]:
                    mistakeInAnswer = answers.split()[x]
                    correctAnswerToMistake = correctAnswer.split()[x]

            answer = request.form.get('incorrectWord')
            #Form data recieved
            if answer != None:
                #If answer is not empty
                if answer.lower() == mistakeInAnswer:         
                    flash('Correct',category='success')

                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()

                    cursor.execute("SELECT NumberOfTimesAnswered,NumberOfTimesAnsweredCorrectly FROM Question WHERE QuestionID=?",(str(currentQuestion.getQuestionID()),))
                    questionInfo = cursor.fetchall()

                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=?,NumberOfTimesAnsweredCorrectly=? WHERE QuestionID=?",(int(questionInfo[0][0])+1,int(questionInfo[0][1])+1,str(currentQuestion.getQuestionID()),))
                    connection.commit()

                    cursor.execute("SELECT NumberOfQuestionsAnsweredCorrectly FROM Quiz WHERE QuizID=?",(str(UserQuiz.getQuizID()),))
                    quizInfo = cursor.fetchall()

                    cursor.execute("UPDATE Quiz SET NumberOfQuestionsAnsweredCorrectly=? WHERE QuizID=?",(int(quizInfo[0][0])+1,str(UserQuiz.getQuizID()),))
                    connection.commit()

                    connection.close()

                    if UserQuiz.getQuestions().size() == 0:   #If all questions have been used (Quiz finished)
                        count=0
                        QuizID = None
                        for UserAndQuizObject in userAndQuizObjects:
                            if UserAndQuizObject[0]==UserID:    #If the quiz object that belongs to the use is returned
                                QuizID = UserAndQuizObject[1].getQuizID()
                                userAndQuizObjects.pop(count)   #Quiz object is removed as quiz has been completed
                            count+=1
                        return redirect(url_for("quizSection.viewResults",QuizID=QuizID))
                        #Display results to the user

                    currentQuestion = UserQuiz.nextQuestion()
                    questionType = currentQuestion.getQuestionType()
                    questions = currentQuestion.getQuestion()
                    answers = currentQuestion.getAnswer()
                    correctAnswer = currentQuestion.getCorrectAnswer()
                    #Next question and answer is returned

                    if questionType == 'MC':
                        random.shuffle(answers)
                    if questionType == 'QA':
                    #The answers and questions are matched and assigned the same id
                    #Therefore when validating if they have matching ids they are valid
                        questionsAndIDs = []
                        answersAndIDs = []

                        for x in range(len(questions)):
                            questionID = x
                            question = questions[x]
                            questionsAndIDs.append((questionID,question))

                        for x in questionsAndIDs:
                            for key,value in correctAnswer.items():
                                if x[1] == key:
                                    answersAndIDs.append((x[0],value))

                        random.shuffle(answersAndIDs)

                        questions = questionsAndIDs
                        answers = answersAndIDs

                    return render_template("singlePlayerQuiz.html",user=current_user,QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=False,CorrectAnswer=correctAnswer)
                else:
                    flash('Inorrect',category='error')

                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()

                    cursor.execute("SELECT NumberOfTimesAnswered FROM Question WHERE QuestionID=?",(str(currentQuestion.getQuestionID()),))
                    questionInfo = cursor.fetchall()

                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=? WHERE QuestionID=?",(int(questionInfo[0][0])+1,str(currentQuestion.getQuestionID()),))
                    connection.commit()
                    connection.close()
                    return render_template("singlePlayerQuiz.html",user=current_user,QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=True,CorrectAnswer=correctAnswerToMistake)#if incorrect display correct answer and then go to next question

        if questionType == 'QA':

            if request.form.get('Box0') == '0' and request.form.get('Box1') == '1' and request.form.get('Box2') == '2':      
                flash('Correct',category='success')

                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()

                cursor.execute("SELECT NumberOfTimesAnswered,NumberOfTimesAnsweredCorrectly FROM Question WHERE QuestionID=?",(str(currentQuestion.getQuestionID()),))
                questionInfo = cursor.fetchall()

                cursor.execute("UPDATE Question SET NumberOfTimesAnswered=?,NumberOfTimesAnsweredCorrectly=? WHERE QuestionID=?",(int(questionInfo[0][0])+1,int(questionInfo[0][1])+1,str(currentQuestion.getQuestionID()),))
                connection.commit()

                cursor.execute("SELECT NumberOfQuestionsAnsweredCorrectly FROM Quiz WHERE QuizID=?",(str(UserQuiz.getQuizID()),))
                quizInfo = cursor.fetchall()

                cursor.execute("UPDATE Quiz SET NumberOfQuestionsAnsweredCorrectly=? WHERE QuizID=?",(int(quizInfo[0][0])+1,str(UserQuiz.getQuizID()),))
                connection.commit()

                connection.close()

                if UserQuiz.getQuestions().size() == 0:   #If all questions have been used (Quiz finished)
                    count=0
                    QuizID = None
                    for UserAndQuizObject in userAndQuizObjects:
                        if UserAndQuizObject[0]==UserID:    #If the quiz object that belongs to the use is returned
                            QuizID = UserAndQuizObject[1].getQuizID()
                            userAndQuizObjects.pop(count)   #Quiz object is removed as quiz has been completed
                        count+=1
                    return redirect(url_for("quizSection.viewResults",QuizID=QuizID))
                    #Display results to the user

                currentQuestion = UserQuiz.nextQuestion()
                questionType = currentQuestion.getQuestionType()
                questions = currentQuestion.getQuestion()
                answers = currentQuestion.getAnswer()
                correctAnswer = currentQuestion.getCorrectAnswer()
                #Next question and answer is returned

                if questionType == 'MC':
                    random.shuffle(answers)
                if questionType == 'QA':
                    #The answers and questions are matched and assigned the same id
                    #Therefore when validating if they have matching ids they are valid
                    questionsAndIDs = []
                    answersAndIDs = []

                    for x in range(len(questions)):
                        questionID = x
                        question = questions[x]
                        questionsAndIDs.append((questionID,question))

                    for x in questionsAndIDs:
                        for key,value in correctAnswer.items():
                            if x[1] == key:
                                answersAndIDs.append((x[0],value))

                    random.shuffle(answersAndIDs)

                    questions = questionsAndIDs
                    answers = answersAndIDs

                return render_template("singlePlayerQuiz.html",user=current_user,QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=False,CorrectAnswer=correctAnswer)
            
            else:
                flash('Inorrect',category='error')

                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()

                cursor.execute("SELECT NumberOfTimesAnswered FROM Question WHERE QuestionID=?",(str(currentQuestion.getQuestionID()),))
                questionInfo = cursor.fetchall()
                cursor.execute("UPDATE Question SET NumberOfTimesAnswered=? WHERE QuestionID=?",(int(questionInfo[0][0])+1,str(currentQuestion.getQuestionID()),))
                
                connection.commit()
                connection.close()

                return render_template("singlePlayerQuiz.html",user=current_user,QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=True,CorrectAnswer=correctAnswer)#if incorrect display correct answer and then go to next question

    return render_template("singlePlayerQuiz.html",user=current_user,QuestionType=questionType,Questions=questions,Answers=answers,DisplayCorrectAnswer=False,CorrectAnswer=correctAnswer)



@quizSection.route('/viewResults/<QuizID>',  methods=['GET', 'POST'])
@login_required
def viewResults(QuizID):

    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()
    
    cursor.execute("SELECT NumberOfQuestions,NumberOfQuestionsAnsweredCorrectly FROM Quiz WHERE QuizID=?",(QuizID,))
    Results = cursor.fetchall()
    connection.close()
    #The scores for the quiz are queried
    if request.method == 'POST':
        if request.form.get('Finish') == 'Finish':
            #If user is finished viewing their results
            return redirect(url_for('homePage.home'))

    return render_template("viewResults.html",user=current_user,Results=Results,)

