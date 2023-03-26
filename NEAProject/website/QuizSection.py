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


QuizSection = Blueprint('QuizSection',__name__)

UserAndQuizObjects = []
AllQuizQuestions = []

rooms = {}
UserScores = {}






@QuizSection.route('/quizMenu',  methods=['GET', 'POST'])
@login_required
def quizMenu():
    UserID =current_user.get_id()
    session.clear()#remove from dict UserScores where Userid=?
    if request.method == 'POST':
        if request.form.get('TakeQuiz') == 'Take Quiz':
            return redirect(url_for("QuizSection.quizMenchooseDeckToQuizOnu"))
        
        if request.form.get('PreviousQuizzes') == 'Previous Quizzes':
            return redirect(url_for("QuizSection.viewPastQuizzes"))


        else:

            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()
            cursor.execute("SELECT Firstname FROM User WHERE UserID=?",(UserID,))
            connection.close()

            name = cursor.fetchall()[0][0]
            code = request.form.get("code")
            join = request.form.get("join", False)
            create = request.form.get("create", False)
            quizID = request.form.get("QuizID")


            if join != False and not code:
                flash("You have not entered a code for the Quiz")
                return render_template("quizMenu.html",user=current_user, code=code)

            room = code

            if rooms[room].get("QuizID") == quizID:
                flash('There is already a quiz ongoing with the QuizID you have entered',category='error')
                return render_template("quizMenu.html",user=current_user, code=code)

            if create != False:
                Users = [UserID]
                room = generate_unique_code(4)
                rooms[room] = {"members": 0, "messages": [],"QuizID":quizID,"Users":Users}
            elif code not in rooms:
                flash("Quiz room with code dosen't exist",category='error')
                return render_template("quizMenu.html",user=current_user, code=code)
            



            if room in rooms:
                quizID = rooms[room].get("QuizID")
                currentUsers = rooms[room].get("Users")
                if UserID not in currentUsers:
                    currentUsers.append(UserID)
                rooms[room].update({"Users":currentUsers})
        
            session["room"] = room
            session["name"] = name
            UserScores[UserID] = 0

            
            return redirect(url_for("QuizSection.room",QuizID=quizID))
    
    return render_template("quizMenu.html",user=current_user)


@QuizSection.route("/room/<QuizID>",  methods=['GET','POST'])
@login_required
def room(QuizID):
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("QuizSection.quizMenu"))
    return render_template("room.html",user=current_user, code=room, messages=rooms[room]["messages"],QuizID=QuizID)



@QuizSection.route("/viewPastQuizzes",  methods=['GET','POST'])
@login_required
def viewPastQuizzes():
    if request.method == 'POST':
        if request.form.get("action1") == 'View PastQuizzes':
            return redirect(url_for('QuizSection.DisplayPastQuizzes'))
        if request.form.get("action2") == 'Retake Quiz':
            return redirect(url_for('QuizSection.chooseQuizID'))


    return render_template('viewPastQuizzes.html',user=current_user)

@QuizSection.route("/DisplayPastQuizzes",  methods=['GET','POST'])
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
    
    data = list(dict.fromkeys(data))

    return render_template('DisplayPastQuizzes.html',user=current_user,data=data)





@QuizSection.route("/chooseQuizID",  methods=['GET','POST'])
@login_required
def chooseQuizID():
    UserID = current_user.get_id()
    if request.method == 'POST':
        QuizID = request.form.get("QuizID")
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM PastQuiz WHERE QuizID=? AND UserID=?",(QuizID,UserID))
        results = cursor.fetchall()
        if len(results) == 0:
            flash('You do not have a quiz with the specified ID',category='error')
            return render_template('chooseQuizID.html',user=current_user)
        else:
            return redirect(url_for('QuizSection.TakeQuizSinglePlayer',QuizID=QuizID))

        #check if user has access to this quiz and check if quiz exists

    return render_template('chooseQuizID.html',user=current_user)




@QuizSection.route('/Scoreboard',  methods=['GET', 'POST'])
@login_required
def multiplayScoreboarderQuiz():
    room = session.get("room")
    if room!=None:
        currentUsers = rooms[room].get("Users")
        UserNamesAndScores=[]
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        for x in currentUsers:
            cursor.execute("SELECT Firstname FROM User WHERE UserID=?",(x,))
            UserName = cursor.fetchall()
            UserScore = UserScores[x]
            UserNamesAndScores.append((UserName[0][0],UserScore))
        connection.close()

        return render_template("ScoreBoard.html",UserNamesAndScores=UserNamesAndScores)
    return 
#clear user scores after quiz is complete


@QuizSection.route('/TakeQuizSinglePlayer/<QuizID>',  methods=['GET', 'POST'])
@login_required
def TakeQuizSinglePlayer(QuizID):


    UserID=current_user.get_id()

    QuizID = int(QuizID)
    QuestionIds = []

    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT QuestionID FROM QuizQuestions WHERE QuizID=?",(str(QuizID),))
    QuestionIdsFromQuiz = cursor.fetchall()
    for x in QuestionIdsFromQuiz:
        QuestionIds.append(x[0])
    connection.close()
    if request.method == 'GET':
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("UPDATE Quiz SET NumberOfQuestionsAnsweredCorrectly=? WHERE QuizID=?",(0,QuizID,))
        connection.commit()
        connection.close()


        QuizExists = False
        for x in AllQuizQuestions:
            if x[0][1][0] in QuestionIds and UserID == x[0][0]:
                
                QuizQuestions = x
                QuizExists = True

        if QuizExists == True:
            
            Question = QuizQuestions[0][1]
            Question = list(Question)
            QuestionIDOfQuestion = Question[0]
            QuestionType=Question[1]

            try:
                Questions=eval(Question[2])
            except:
                Questions=Question[2]

            try:
                Answers=eval(Question[3])
            except:
                Answers=Question[3]

            try:
                CorrectAnswer=eval(Question[4])
            except:
                CorrectAnswer=Question[4]
        else:

            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()
            cursor.execute("SELECT QuestionID FROM QuizQuestions WHERE QuizID=?",(str(QuizID),))
            QuestionIdsFromQuiz = cursor.fetchall()

            QuizQuestions = []        

            for x in QuestionIdsFromQuiz:
                cursor.execute("SELECT QuestionID,QuestionType,Question,Answer,CorrectAnswer FROM Question WHERE QuestionID=?",(x[0],))
                QuizQuestions.append((UserID,cursor.fetchall()[0]))
            connection.close()
            AllQuizQuestions.append(QuizQuestions)
            Question = QuizQuestions[0][1]
            Question = list(Question)
            QuestionIDOfQuestion = Question[0]
            QuestionType=Question[1]

            try:
                Questions=eval(Question[2])
            except:
                Questions=Question[2]

            try:
                Answers=eval(Question[3])
            except:
                Answers=Question[3]

            try:
                CorrectAnswer=eval(Question[4])
            except:
                CorrectAnswer=Question[4]
                
    if request.method == 'POST':
        QuizQuestions=[]

        for x in AllQuizQuestions:
            if len(x)!=0:#if quiz hasnt been completed
                if x[0][1][0] in QuestionIds and UserID == x[0][0]:
                    
                    QuizQuestions = x
            else:
                QuizQuestions = x

        if len(QuizQuestions) == 0:
            return redirect(url_for("QuizSection.viewResults",QuizID=QuizID))
            



        Question = QuizQuestions[0][1]
        Question = list(Question)
        QuestionIDOfQuestion = Question[0]
        QuestionType=Question[1]

        try:
            Questions=eval(Question[2])
        except:
            Questions=Question[2]

        try:
            Answers=eval(Question[3])
        except:
            Answers=Question[3]

        try:
            CorrectAnswer=eval(Question[4])
        except:
            CorrectAnswer=Question[4]
        
        if request.form.get('NextQuestion') == 'Next Question':

            for x in AllQuizQuestions:
                if len(x)!=0:
                    if x[0][1][0] in QuestionIds and UserID == x[0][0]:
                        AllQuizQuestions[AllQuizQuestions.index(x)].pop(0)
                        
                        QuizQuestions = x
                else:
                    QuizQuestions = x


            if len(QuizQuestions) == 0:
                return redirect(url_for("QuizSection.viewResults",QuizID=QuizID))

                
            Question = QuizQuestions[0][1]
            Question = list(Question)
            QuestionIDOfQuestion = Question[0]
            QuestionType=Question[1]

            try:
                Questions=eval(Question[2])
            except:
                Questions=Question[2]

            try:
                Answers=eval(Question[3])
            except:
                Answers=Question[3]

            try:
                CorrectAnswer=eval(Question[4])
            except:
                CorrectAnswer=Question[4]



            if QuestionType == 'MC':
                random.shuffle(Answers)
            if QuestionType == 'QA':

                QuestionsAndIds = []
                AnswersAndIds = []

                for x in range(len(Questions)):
                    QuestionID = x
                    Question = Questions[x]
                    QuestionsAndIds.append((QuestionID,Question))

                for x in QuestionsAndIds:
                    for key,value in CorrectAnswer.items():
                        if x[1] == key:
                            AnswersAndIds.append((x[0],value))

                random.shuffle(AnswersAndIds)

                Questions = QuestionsAndIds
                Answers = AnswersAndIds

            return render_template("SinglePlayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer,QuizID=QuizID,user=current_user)

        if QuestionType == 'MC':
            multipleChoiceAnswer = request.form.get('answer')
        
            if multipleChoiceAnswer == CorrectAnswer:



                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()

                cursor.execute("SELECT NumberOfTimesAnswered,NumberOfTimesAnsweredCorrectly FROM Question WHERE QuestionID=?",(QuestionIDOfQuestion,))
                QuestionInfo = cursor.fetchall()


                cursor.execute("UPDATE Question SET NumberOfTimesAnswered=?,NumberOfTimesAnsweredCorrectly=? WHERE QuestionID=?",(int(QuestionInfo[0][0])+1,int(QuestionInfo[0][1])+1,QuestionIDOfQuestion,))
                connection.commit()

                cursor.execute("SELECT NumberOfQuestionsAnsweredCorrectly FROM Quiz WHERE QuizID=?",(QuizID,))
                QuizInfo = cursor.fetchall()

                cursor.execute("UPDATE Quiz SET NumberOfQuestionsAnsweredCorrectly=? WHERE QuizID=?",(int(QuizInfo[0][0])+1,QuizID,))
                connection.commit()

                connection.close()


                flash('Correct',category='success')


                for x in AllQuizQuestions:
                    if len(x)!=0:
                        if x[0][1][0] in QuestionIds and UserID == x[0][0]:
                            AllQuizQuestions[AllQuizQuestions.index(x)].pop(0)
                            
                            QuizQuestions = x
                    else:
                        QuizQuestions = x
                        
                if len(QuizQuestions) == 0:
                    return redirect(url_for("QuizSection.viewResults",QuizID=QuizID))#clear scores    
                    
                Question = QuizQuestions[0][1]
                Question = list(Question)
                QuestionIDOfQuestion = Question[0]
                QuestionType=Question[1]

                try:
                    Questions=eval(Question[2])
                except:
                    Questions=Question[2]

                try:
                    Answers=eval(Question[3])
                except:
                    Answers=Question[3]

                try:
                    CorrectAnswer=eval(Question[4])
                except:
                    CorrectAnswer=Question[4]


                if QuestionType == 'MC':
                    random.shuffle(Answers)
                if QuestionType == 'QA':

                    QuestionsAndIds = []
                    AnswersAndIds = []

                    for x in range(len(Questions)):
                        QuestionID = x
                        Question = Questions[x]
                        QuestionsAndIds.append((QuestionID,Question))

                    for x in QuestionsAndIds:
                        for key,value in CorrectAnswer.items():
                            if x[1] == key:
                                AnswersAndIds.append((x[0],value))

                    random.shuffle(AnswersAndIds)

                    Questions = QuestionsAndIds
                    Answers = AnswersAndIds


                return render_template("SinglePlayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer,QuizID=QuizID,user=current_user)
            else:
                flash('Inorrect',category='error')


                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()

                cursor.execute("SELECT NumberOfTimesAnswered FROM Question WHERE QuestionID=?",(QuestionIDOfQuestion,))
                QuestionInfo = cursor.fetchall()
                cursor.execute("UPDATE Question SET NumberOfTimesAnswered=? WHERE QuestionID=?",(int(QuestionInfo[0][0])+1,QuestionIDOfQuestion,))
                connection.commit()
                connection.close()


                return render_template("SinglePlayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=True,CorrectAnswer=CorrectAnswer,QuizID=QuizID,user=current_user)#if incorrect display correct answer and then go to next question


        if QuestionType == 'FB':
            Answer = request.form.get('Answer')
            if Answer!=None:
                if Answer.lower() == CorrectAnswer:
                    flash('correct',category='success')
                    


                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()

                    cursor.execute("SELECT NumberOfTimesAnswered,NumberOfTimesAnsweredCorrectly FROM Question WHERE QuestionID=?",(QuestionIDOfQuestion,))
                    QuestionInfo = cursor.fetchall()


                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=?,NumberOfTimesAnsweredCorrectly=? WHERE QuestionID=?",(int(QuestionInfo[0][0])+1,int(QuestionInfo[0][1])+1,QuestionIDOfQuestion,))
                    connection.commit()

                    cursor.execute("SELECT NumberOfQuestionsAnsweredCorrectly FROM Quiz WHERE QuizID=?",(QuizID,))
                    QuizInfo = cursor.fetchall()

                    cursor.execute("UPDATE Quiz SET NumberOfQuestionsAnsweredCorrectly=? WHERE QuizID=?",(int(QuizInfo[0][0])+1,QuizID,))
                    connection.commit()

                    connection.close()


                    for x in AllQuizQuestions:
                        if len(x)!=0:
                            if x[0][1][0] in QuestionIds and UserID == x[0][0]:
                                AllQuizQuestions[AllQuizQuestions.index(x)].pop(0)
                                
                                QuizQuestions = x
                        else:
                            QuizQuestions = x
                    if len(QuizQuestions) == 0:
                        return redirect(url_for("QuizSection.viewResults",QuizID=QuizID))          

                        
                    Question = QuizQuestions[0][1]
                    Question = list(Question)
                    QuestionIDOfQuestion = Question[0]
                    QuestionType=Question[1]

                    try:
                        Questions=eval(Question[2])
                    except:
                        Questions=Question[2]

                    try:
                        Answers=eval(Question[3])
                    except:
                        Answers=Question[3]

                    try:
                        CorrectAnswer=eval(Question[4])
                    except:
                        CorrectAnswer=Question[4]

                    if QuestionType == 'MC':
                        random.shuffle(Answers)
                    if QuestionType == 'QA':

                        QuestionsAndIds = []
                        AnswersAndIds = []

                        for x in range(len(Questions)):
                            QuestionID = x
                            Question = Questions[x]
                            QuestionsAndIds.append((QuestionID,Question))

                        for x in QuestionsAndIds:
                            for key,value in CorrectAnswer.items():
                                if x[1] == key:
                                    AnswersAndIds.append((x[0],value))

                        random.shuffle(AnswersAndIds)

                        Questions = QuestionsAndIds
                        Answers = AnswersAndIds

                    return render_template("SinglePlayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer,QuizID=QuizID,user=current_user)
                else:
                    flash('Inorrect',category='error')

                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()

                    cursor.execute("SELECT NumberOfTimesAnswered FROM Question WHERE QuestionID=?",(QuestionIDOfQuestion,))
                    QuestionInfo = cursor.fetchall()
                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=? WHERE QuestionID=?",(int(QuestionInfo[0][0])+1,QuestionIDOfQuestion,))
                    connection.commit()
                    connection.close()


                    return render_template("SinglePlayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=True,CorrectAnswer=CorrectAnswer,QuizID=QuizID,user=current_user)#if incorrect display correct answer and then go to next question

        if QuestionType == 'SM':

            MistakeInAnswer=''
            CorrectAnswerToMistake=''


            for x in range(len(Answers.split())):
                if Answers.split()[x] != CorrectAnswer.split()[x]:
                    MistakeInAnswer = Answers.split()[x]
                    CorrectAnswerToMistake = CorrectAnswer.split()[x]



            Answer = request.form.get('incorrectWord')

            if Answer != None:

                if Answer.lower() == MistakeInAnswer:
                                

                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()

                    cursor.execute("SELECT NumberOfTimesAnswered,NumberOfTimesAnsweredCorrectly FROM Question WHERE QuestionID=?",(QuestionIDOfQuestion,))
                    QuestionInfo = cursor.fetchall()


                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=?,NumberOfTimesAnsweredCorrectly=? WHERE QuestionID=?",(int(QuestionInfo[0][0])+1,int(QuestionInfo[0][1])+1,QuestionIDOfQuestion,))
                    connection.commit()

                    cursor.execute("SELECT NumberOfQuestionsAnsweredCorrectly FROM Quiz WHERE QuizID=?",(QuizID,))
                    QuizInfo = cursor.fetchall()

                    cursor.execute("UPDATE Quiz SET NumberOfQuestionsAnsweredCorrectly=? WHERE QuizID=?",(int(QuizInfo[0][0])+1,QuizID,))
                    connection.commit()

                    connection.close()


                    flash('Correct',category='success')


                    for x in AllQuizQuestions:
                        if len(x)!=0:
                            if x[0][1][0] in QuestionIds and UserID == x[0][0]:
                                AllQuizQuestions[AllQuizQuestions.index(x)].pop(0)
                                
                                QuizQuestions = x
                        else:
                            QuizQuestions = x

                    if len(QuizQuestions) == 0:
                        return redirect(url_for("QuizSection.viewResults",QuizID=QuizID))


                        
                    Question = QuizQuestions[0][1]
                    Question = list(Question)
                    QuestionIDOfQuestion = Question[0]
                    QuestionType=Question[1]

                    try:
                        Questions=eval(Question[2])
                    except:
                        Questions=Question[2]

                    try:
                        Answers=eval(Question[3])
                    except:
                        Answers=Question[3]

                    try:
                        CorrectAnswer=eval(Question[4])
                    except:
                        CorrectAnswer=Question[4]

                    if QuestionType == 'MC':
                        random.shuffle(Answers)
                    if QuestionType == 'QA':

                        QuestionsAndIds = []
                        AnswersAndIds = []

                        for x in range(len(Questions)):
                            QuestionID = x
                            Question = Questions[x]
                            QuestionsAndIds.append((QuestionID,Question))

                        for x in QuestionsAndIds:
                            for key,value in CorrectAnswer.items():
                                if x[1] == key:
                                    AnswersAndIds.append((x[0],value))

                        random.shuffle(AnswersAndIds)

                        Questions = QuestionsAndIds
                        Answers = AnswersAndIds

                    return render_template("SinglePlayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer,QuizID=QuizID,user=current_user)
                else:
                    flash('Inorrect',category='error')



                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()

                    cursor.execute("SELECT NumberOfTimesAnswered FROM Question WHERE QuestionID=?",(QuestionIDOfQuestion,))
                    QuestionInfo = cursor.fetchall()
                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=? WHERE QuestionID=?",(int(QuestionInfo[0][0])+1,QuestionIDOfQuestion,))
                    connection.commit()
                    connection.close()



                    return render_template("SinglePlayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=True,CorrectAnswer=CorrectAnswerToMistake,QuizID=QuizID,user=current_user)#if incorrect display correct answer and then go to next question


#answer as question and correct mistake as answer


        if QuestionType == 'QA':

            if request.form.get('Box0') == '0' and request.form.get('Box1') == '1' and request.form.get('Box2') == '2':      
                flash('Correct',category='success')

                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()

                cursor.execute("SELECT NumberOfTimesAnswered,NumberOfTimesAnsweredCorrectly FROM Question WHERE QuestionID=?",(QuestionIDOfQuestion,))
                QuestionInfo = cursor.fetchall()


                cursor.execute("UPDATE Question SET NumberOfTimesAnswered=?,NumberOfTimesAnsweredCorrectly=? WHERE QuestionID=?",(int(QuestionInfo[0][0])+1,int(QuestionInfo[0][1])+1,QuestionIDOfQuestion,))
                connection.commit()

                cursor.execute("SELECT NumberOfQuestionsAnsweredCorrectly FROM Quiz WHERE QuizID=?",(QuizID,))
                QuizInfo = cursor.fetchall()

                cursor.execute("UPDATE Quiz SET NumberOfQuestionsAnsweredCorrectly=? WHERE QuizID=?",(int(QuizInfo[0][0])+1,QuizID,))
                connection.commit()

                connection.close()

                for x in AllQuizQuestions:
                    if len(x)!=0:
                        if x[0][1][0] in QuestionIds and UserID == x[0][0]:
                            AllQuizQuestions[AllQuizQuestions.index(x)].pop(0)
                            
                            QuizQuestions = x
                    else:
                        QuizQuestions = x

                if len(QuizQuestions) == 0:
                    return redirect(url_for("QuizSection.viewResults",QuizID=QuizID))                  
                    
                Question = QuizQuestions[0][1]
                Question = list(Question)
                QuestionIDOfQuestion = Question[0]
                QuestionType=Question[1]

                try:
                    Questions=eval(Question[2])
                except:
                    Questions=Question[2]

                try:
                    Answers=eval(Question[3])
                except:
                    Answers=Question[3]

                try:
                    CorrectAnswer=eval(Question[4])
                except:
                    CorrectAnswer=Question[4]

                if QuestionType == 'MC':
                    random.shuffle(Answers)
                if QuestionType == 'QA':

                    QuestionsAndIds = []
                    AnswersAndIds = []

                    for x in range(len(Questions)):
                        QuestionID = x
                        Question = Questions[x]
                        QuestionsAndIds.append((QuestionID,Question))

                    for x in QuestionsAndIds:
                        for key,value in CorrectAnswer.items():
                            if x[1] == key:
                                AnswersAndIds.append((x[0],value))

                    random.shuffle(AnswersAndIds)

                    Questions = QuestionsAndIds
                    Answers = AnswersAndIds

                return render_template("SinglePlayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer,QuizID=QuizID,user=current_user)

            
            else:
                flash("incorrect",category='error')

                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()


                cursor.execute("SELECT NumberOfTimesAnswered FROM Question WHERE QuestionID=?",(QuestionIDOfQuestion,))
                QuestionInfo = cursor.fetchall()
                cursor.execute("UPDATE Question SET NumberOfTimesAnswered=? WHERE QuestionID=?",(int(QuestionInfo[0][0])+1,QuestionIDOfQuestion,))
                connection.commit()
                connection.close()


                return render_template("SinglePlayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=True,CorrectAnswer=CorrectAnswer,QuizID=QuizID,user=current_user)#if incorrect display correct answer and then go to next question

    return render_template("SinglePlayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer,QuizID=QuizID,user=current_user)






@QuizSection.route('/multiplayerQuiz/<QuizID>',  methods=['GET', 'POST'])
@login_required
def multiplayerQuiz(QuizID):

    UserID=current_user.get_id()


    QuizID = int(QuizID)
    QuestionIds = []

    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT QuestionID FROM QuizQuestions WHERE QuizID=?",(str(QuizID),))
    QuestionIdsFromQuiz = cursor.fetchall()
    for x in QuestionIdsFromQuiz:
        QuestionIds.append(x[0])
    connection.close()
    if request.method == 'GET':
        QuizExists = False
        for x in AllQuizQuestions:
            if x[0][1][0] in QuestionIds and UserID == x[0][0]:
                
                QuizQuestions = x
                QuizExists = True

        if QuizExists == True:
            
            Question = QuizQuestions[0][1]
            Question = list(Question)
            QuestionType=Question[1]

            try:
                Questions=eval(Question[2])
            except:
                Questions=Question[2]

            try:
                Answers=eval(Question[3])
            except:
                Answers=Question[3]

            try:
                CorrectAnswer=eval(Question[4])
            except:
                CorrectAnswer=Question[4]
        else:

            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()
            cursor.execute("SELECT QuestionID FROM QuizQuestions WHERE QuizID=?",(str(QuizID),))
            QuestionIdsFromQuiz = cursor.fetchall()

            QuizQuestions = []        

            for x in QuestionIdsFromQuiz:
                cursor.execute("SELECT QuestionID,QuestionType,Question,Answer,CorrectAnswer FROM Question WHERE QuestionID=?",(x[0],))
                QuizQuestions.append((UserID,cursor.fetchall()[0]))
            connection.close()
            AllQuizQuestions.append(QuizQuestions)
            Question = QuizQuestions[0][1]
            Question = list(Question)

            QuestionType=Question[1]

            try:
                Questions=eval(Question[2])
            except:
                Questions=Question[2]

            try:
                Answers=eval(Question[3])
            except:
                Answers=Question[3]

            try:
                CorrectAnswer=eval(Question[4])
            except:
                CorrectAnswer=Question[4]
                
    if request.method == 'POST':
        QuizQuestions=[]

        for x in AllQuizQuestions:
            if len(x)!=0:#if quiz hasnt been completed
                if x[0][1][0] in QuestionIds and UserID == x[0][0]:
                    
                    QuizQuestions = x
            else:
                QuizQuestions = x

        if len(QuizQuestions) == 0:
            return render_template('quizEnd.html')



        Question = QuizQuestions[0][1]
        Question = list(Question)
        
        QuestionType=Question[1]

        try:
            Questions=eval(Question[2])
        except:
            Questions=Question[2]

        try:
            Answers=eval(Question[3])
        except:
            Answers=Question[3]

        try:
            CorrectAnswer=eval(Question[4])
        except:
            CorrectAnswer=Question[4]
        
        if request.form.get('DisplayAnswer') == 'True':

            for x in AllQuizQuestions:
                if len(x)!=0:
                    if x[0][1][0] in QuestionIds and UserID == x[0][0]:
                        AllQuizQuestions[AllQuizQuestions.index(x)].pop(0)
                        
                        QuizQuestions = x
                else:
                    QuizQuestions = x


            if len(QuizQuestions) == 0:
                UserScores.pop(UserID)
                return render_template('quizEnd.html')

                
            Question = QuizQuestions[0][1]
            Question = list(Question)
            QuestionType=Question[1]

            try:
                Questions=eval(Question[2])
            except:
                Questions=Question[2]

            try:
                Answers=eval(Question[3])
            except:
                Answers=Question[3]

            try:
                CorrectAnswer=eval(Question[4])
            except:
                CorrectAnswer=Question[4]



            if QuestionType == 'MC':
                random.shuffle(Answers)
            if QuestionType == 'QA':

                QuestionsAndIds = []
                AnswersAndIds = []

                for x in range(len(Questions)):
                    QuestionID = x
                    Question = Questions[x]
                    QuestionsAndIds.append((QuestionID,Question))

                for x in QuestionsAndIds:
                    for key,value in CorrectAnswer.items():
                        if x[1] == key:
                            AnswersAndIds.append((x[0],value))

                random.shuffle(AnswersAndIds)

                Questions = QuestionsAndIds
                Answers = AnswersAndIds

            return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer,QuizID=QuizID)

        if QuestionType == 'MC':
            multipleChoiceAnswer = request.form.get('answer')
        
            if multipleChoiceAnswer == CorrectAnswer:

                flash('Correct',category='success')
                currentScore = UserScores.get(UserID)
                if currentScore != None:
                    newScore = currentScore+1
                    UserScores.update({UserID:newScore})


                for x in AllQuizQuestions:
                    if len(x)!=0:
                        if x[0][1][0] in QuestionIds and UserID == x[0][0]:
                            AllQuizQuestions[AllQuizQuestions.index(x)].pop(0)
                            
                            QuizQuestions = x
                    else:
                        QuizQuestions = x
                        
                if len(QuizQuestions) == 0:
                    UserScores.pop(UserID)
                    return render_template('quizEnd.html')#clear scores    
                    
                Question = QuizQuestions[0][1]
                Question = list(Question)
                QuestionType=Question[1]

                try:
                    Questions=eval(Question[2])
                except:
                    Questions=Question[2]

                try:
                    Answers=eval(Question[3])
                except:
                    Answers=Question[3]

                try:
                    CorrectAnswer=eval(Question[4])
                except:
                    CorrectAnswer=Question[4]


                if QuestionType == 'MC':
                    random.shuffle(Answers)
                if QuestionType == 'QA':

                    QuestionsAndIds = []
                    AnswersAndIds = []

                    for x in range(len(Questions)):
                        QuestionID = x
                        Question = Questions[x]
                        QuestionsAndIds.append((QuestionID,Question))

                    for x in QuestionsAndIds:
                        for key,value in CorrectAnswer.items():
                            if x[1] == key:
                                AnswersAndIds.append((x[0],value))

                    random.shuffle(AnswersAndIds)

                    Questions = QuestionsAndIds
                    Answers = AnswersAndIds


                return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer,QuizID=QuizID)
            else:
                flash('Inorrect',category='error')

                return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=True,CorrectAnswer=CorrectAnswer,QuizID=QuizID)#if incorrect display correct answer and then go to next question


        if QuestionType == 'FB':
            Answer = request.form.get('Answer')
            if Answer!=None:
                if Answer.lower() == CorrectAnswer:
                    flash('correct',category='success')
                    
                    currentScore = UserScores.get(UserID)
                    if currentScore != None:
                        newScore = currentScore+1
                        UserScores.update({UserID:newScore})

                    for x in AllQuizQuestions:
                        if len(x)!=0:
                            if x[0][1][0] in QuestionIds and UserID == x[0][0]:
                                AllQuizQuestions[AllQuizQuestions.index(x)].pop(0)
                                
                                QuizQuestions = x
                        else:
                            QuizQuestions = x
                    if len(QuizQuestions) == 0:
                        UserScores.pop(UserID)
                        return render_template('quizEnd.html')          

                        
                    Question = QuizQuestions[0][1]
                    Question = list(Question)
                    QuestionType=Question[1]

                    try:
                        Questions=eval(Question[2])
                    except:
                        Questions=Question[2]

                    try:
                        Answers=eval(Question[3])
                    except:
                        Answers=Question[3]

                    try:
                        CorrectAnswer=eval(Question[4])
                    except:
                        CorrectAnswer=Question[4]

                    if QuestionType == 'MC':
                        random.shuffle(Answers)
                    if QuestionType == 'QA':

                        QuestionsAndIds = []
                        AnswersAndIds = []

                        for x in range(len(Questions)):
                            QuestionID = x
                            Question = Questions[x]
                            QuestionsAndIds.append((QuestionID,Question))

                        for x in QuestionsAndIds:
                            for key,value in CorrectAnswer.items():
                                if x[1] == key:
                                    AnswersAndIds.append((x[0],value))

                        random.shuffle(AnswersAndIds)

                        Questions = QuestionsAndIds
                        Answers = AnswersAndIds

                    return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer,QuizID=QuizID)
                else:
                    flash('Inorrect',category='error')

                    return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=True,CorrectAnswer=CorrectAnswer,QuizID=QuizID)#if incorrect display correct answer and then go to next question

        if QuestionType == 'SM':

            MistakeInAnswer=''
            CorrectAnswerToMistake=''


            for x in range(len(Answers.split())):
                if Answers.split()[x] != CorrectAnswer.split()[x]:
                    MistakeInAnswer = Answers.split()[x]
                    CorrectAnswerToMistake = CorrectAnswer.split()[x]



            Answer = request.form.get('incorrectWord')

            if Answer != None:

                if Answer.lower() == MistakeInAnswer:
                                
                    flash('Correct',category='success')


                    currentScore = UserScores.get(UserID)
                    
                    if currentScore != None:
                        newScore = currentScore+1
                        UserScores.update({UserID:newScore})

                    for x in AllQuizQuestions:
                        if len(x)!=0:
                            if x[0][1][0] in QuestionIds and UserID == x[0][0]:
                                AllQuizQuestions[AllQuizQuestions.index(x)].pop(0)
                                
                                QuizQuestions = x
                        else:
                            QuizQuestions = x

                    if len(QuizQuestions) == 0:
                        UserScores.pop(UserID)
                        return render_template('quizEnd.html')


                        
                    Question = QuizQuestions[0][1]
                    Question = list(Question)
                    QuestionType=Question[1]

                    try:
                        Questions=eval(Question[2])
                    except:
                        Questions=Question[2]

                    try:
                        Answers=eval(Question[3])
                    except:
                        Answers=Question[3]

                    try:
                        CorrectAnswer=eval(Question[4])
                    except:
                        CorrectAnswer=Question[4]

                    if QuestionType == 'MC':
                        random.shuffle(Answers)
                    if QuestionType == 'QA':

                        QuestionsAndIds = []
                        AnswersAndIds = []

                        for x in range(len(Questions)):
                            QuestionID = x
                            Question = Questions[x]
                            QuestionsAndIds.append((QuestionID,Question))

                        for x in QuestionsAndIds:
                            for key,value in CorrectAnswer.items():
                                if x[1] == key:
                                    AnswersAndIds.append((x[0],value))

                        random.shuffle(AnswersAndIds)

                        Questions = QuestionsAndIds
                        Answers = AnswersAndIds

                    return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer,QuizID=QuizID)
                else:
                    flash('Inorrect',category='error')


                    return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=True,CorrectAnswer=CorrectAnswerToMistake,QuizID=QuizID)#if incorrect display correct answer and then go to next question


#answer as question and correct mistake as answer


        if QuestionType == 'QA':

            if request.form.get('Box0') == '0' and request.form.get('Box1') == '1' and request.form.get('Box2') == '2':      
                flash('Correct',category='success')


                currentScore = UserScores.get(UserID)
                
                if currentScore != None:
                    newScore = currentScore+1
                    UserScores.update({UserID:newScore})


                for x in AllQuizQuestions:
                    if len(x)!=0:
                        if x[0][1][0] in QuestionIds and UserID == x[0][0]:
                            AllQuizQuestions[AllQuizQuestions.index(x)].pop(0)
                            
                            QuizQuestions = x
                    else:
                        QuizQuestions = x

                if len(QuizQuestions) == 0:
                    UserScores.pop(UserID)
                    return render_template('quizEnd.html')                    
                    
                Question = QuizQuestions[0][1]
                Question = list(Question)
                QuestionType=Question[1]

                try:
                    Questions=eval(Question[2])
                except:
                    Questions=Question[2]

                try:
                    Answers=eval(Question[3])
                except:
                    Answers=Question[3]

                try:
                    CorrectAnswer=eval(Question[4])
                except:
                    CorrectAnswer=Question[4]

                if QuestionType == 'MC':
                    random.shuffle(Answers)
                if QuestionType == 'QA':

                    QuestionsAndIds = []
                    AnswersAndIds = []

                    for x in range(len(Questions)):
                        QuestionID = x
                        Question = Questions[x]
                        QuestionsAndIds.append((QuestionID,Question))

                    for x in QuestionsAndIds:
                        for key,value in CorrectAnswer.items():
                            if x[1] == key:
                                AnswersAndIds.append((x[0],value))

                    random.shuffle(AnswersAndIds)

                    Questions = QuestionsAndIds
                    Answers = AnswersAndIds

                return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer,QuizID=QuizID)

            
            else:

                return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=True,CorrectAnswer=CorrectAnswer,QuizID=QuizID)#if incorrect display correct answer and then go to next question

    return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer,QuizID=QuizID)























    #return render_template('multiplayerQuiz.html',QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer)









@QuizSection.route('/chooseDeckToQuizOn',  methods=['GET', 'POST'])
@login_required
def quizMenchooseDeckToQuizOnu():
    return redirect(url_for("FlashcardsSection.chooseFlashcardDeckToManage",PageToDisplay='TakeQuiz'))


@QuizSection.route('/TakeQuiz/<DeckName>',  methods=['GET', 'POST'])
@login_required
def TakeQuiz(DeckName):
    UserID=current_user.get_id()

    if request.method == "POST":
        NumberOfQuestions = request.form.get('number')

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

# cursor.execute("SELECT COUNT(FlashcardID) FROM Flashcard")
        cursor.execute("""  SELECT COUNT(Flashcard.FlashcardID)
                            FROM Flashcard,FlashcardsDecksAndUserIDs,ParentFlashcardDeck
                            WHERE FlashcardsDecksAndUserIDs.UserID=?
                            AND FlashcardsDecksAndUserIDs.FlashcardID=Flashcard.FlashcardID
                            AND ParentFlashcardDeck.FlashcardDeckName=?
                            AND ParentFlashcardDeck.ParentFlashcardDeckID=FlashcardsDecksAndUserIDs.ParentFlashcardDeckID
        
        """,(UserID,DeckName,))

        NumerOfFlashcards = cursor.fetchall()

        if NumerOfFlashcards[0][0] == 0:
            cursor.execute("""  SELECT COUNT(Flashcard.FlashcardID)
                    FROM Flashcard,FlashcardsDecksAndUserIDs,FlashcardDeck
                    WHERE FlashcardsDecksAndUserIDs.UserID=?
                    AND FlashcardsDecksAndUserIDs.FlashcardID=Flashcard.FlashcardID
                    AND FlashcardDeck.FlashcardDeckName=?
                    AND FlashcardDeck.FlashcardDeckID=FlashcardsDecksAndUserIDs.FlashcardDeckID""",(UserID,DeckName,))#Checks if parent deck
            NumerOfFlashcards = cursor.fetchall()
        connection.close()

        if int(NumberOfQuestions) > int(NumerOfFlashcards[0][0]):
            flash(f'The Maximum number of questions for the deck you have chosen is {NumerOfFlashcards[0][0]}',category='error')
            return render_template("chooseQuizSize.html",user=current_user)




#choose flashcard id where deckname=deckname if Number of questions is greater than query then re render template
        

        return redirect(url_for("QuizSection.quiz",DeckName=DeckName,NumberOfQuestions=NumberOfQuestions))

    return render_template("chooseQuizSize.html",user=current_user)






@QuizSection.route('/quiz/<DeckName>/<NumberOfQuestions>',  methods=['GET', 'POST'])
@login_required
def quiz(DeckName,NumberOfQuestions):
    UserQuiz = ''
    UserID= current_user.get_id()
    if request.method == 'GET':

        for x in range(len(UserAndQuizObjects)):
            IdOfUser = UserAndQuizObjects[x][0]
            if IdOfUser == UserID:
                UserAndQuizObjects.pop(x)

        UserQuiz = Quiz(UserID,DeckName,NumberOfQuestions)


        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("INSERT INTO Quiz(QuizID,NumberOfQuestions,NumberOfQuestionsAnsweredCorrectly,DeckName) values(?,?,?,?)",(UserQuiz.getQuizID(),NumberOfQuestions,0,DeckName))
        connection.commit()
        connection.close()

        CurrentQuestion = UserQuiz.NextQuestion()
        QuestionType = CurrentQuestion.getQuestionType()
        CorrectAnswer = CurrentQuestion.getCorrectAnswer()

        Questions = CurrentQuestion.getQuestion()
        Answers = CurrentQuestion.getAnswer()

        if QuestionType == 'QA':

            QuestionsAndIds = []
            AnswersAndIds = []

            for x in range(len(Questions)):
                QuestionID = x
                Question = Questions[x]
                QuestionsAndIds.append((QuestionID,Question))

            for x in range(len(Answers)):
                AnswerID = x
                Answer = Answers[x]
                AnswersAndIds.append((AnswerID,Answer))

            Questions = QuestionsAndIds
            Answers = AnswersAndIds

        UserAndQuizObject = (UserID,UserQuiz)
        UserAndQuizObjects.append(UserAndQuizObject)


    if request.method == 'POST':

        for UserAndQuizObject in UserAndQuizObjects:
            if UserAndQuizObject[0]==UserID:
                UserQuiz = UserAndQuizObject[1]

        if UserQuiz.getCompletedQuestions().size() == 0:
            CurrentQuestion = UserQuiz.getQuestions().peek()
        else:
            CurrentQuestion = UserQuiz.getCompletedQuestions().peek()
        QuestionType = CurrentQuestion.getQuestionType()
        Questions = CurrentQuestion.getQuestion()
        Answers = CurrentQuestion.getAnswer()
        CorrectAnswer = CurrentQuestion.getCorrectAnswer()
        

        if request.form.get('NextQuestion') == 'Next Question':
            if UserQuiz.getQuestions().size() == 0:
                count=0
                QuizID = None
                for UserAndQuizObject in UserAndQuizObjects:
                    if UserAndQuizObject[0]==UserID:
                        QuizID = UserAndQuizObject[1].getQuizID()
                        UserAndQuizObjects.pop(count)
                    count+=1
                return redirect(url_for("QuizSection.viewResults",QuizID=QuizID))


            CurrentQuestion = UserQuiz.NextQuestion()
            QuestionType = CurrentQuestion.getQuestionType()
            Questions = CurrentQuestion.getQuestion()
            Answers = CurrentQuestion.getAnswer()
            CorrectAnswer = CurrentQuestion.getCorrectAnswer()

            if QuestionType == 'MC':
                random.shuffle(Answers)
            if QuestionType == 'QA':

                QuestionsAndIds = []
                AnswersAndIds = []

                for x in range(len(Questions)):
                    QuestionID = x
                    Question = Questions[x]
                    QuestionsAndIds.append((QuestionID,Question))

                for x in QuestionsAndIds:
                    for key,value in CorrectAnswer.items():
                        if x[1] == key:
                            AnswersAndIds.append((x[0],value))

                random.shuffle(AnswersAndIds)

                Questions = QuestionsAndIds
                Answers = AnswersAndIds

            return render_template("QuizPreview.html",user=current_user,QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer)

        if QuestionType == 'MC':
            multipleChoiceAnswer = request.form.get('answer')
            if request.form.get('Choose') == 'Submit':
                if multipleChoiceAnswer == CorrectAnswer:

                    flash('Correct',category='success')

                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()

                    cursor.execute("SELECT NumberOfTimesAnswered,NumberOfTimesAnsweredCorrectly FROM Question WHERE QuestionID=?",(str(CurrentQuestion.getQuestionID()),))
                    QuestionInfo = cursor.fetchall()

                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=?,NumberOfTimesAnsweredCorrectly=? WHERE QuestionID=?",(int(QuestionInfo[0][0])+1,int(QuestionInfo[0][1])+1,str(CurrentQuestion.getQuestionID()),))
                    connection.commit()
                    
                    cursor.execute("SELECT NumberOfQuestionsAnsweredCorrectly FROM Quiz WHERE QuizID=?",(str(UserQuiz.getQuizID()),))
                    QuizInfo = cursor.fetchall()

                    cursor.execute("UPDATE Quiz SET NumberOfQuestionsAnsweredCorrectly=? WHERE QuizID=?",(int(QuizInfo[0][0])+1,str(UserQuiz.getQuizID()),))
                    connection.commit()

                    connection.close()

                    if UserQuiz.getQuestions().size() == 0:#end of quiz
                        count=0
                        QuizID = None
                        for UserAndQuizObject in UserAndQuizObjects:
                            if UserAndQuizObject[0]==UserID:
                                QuizID = UserAndQuizObject[1].getQuizID()
                                UserAndQuizObjects.pop(count)
                            count+=1
                        return redirect(url_for("QuizSection.viewResults",QuizID=QuizID))

                    CurrentQuestion = UserQuiz.NextQuestion()
                    QuestionType = CurrentQuestion.getQuestionType()
                    Questions = CurrentQuestion.getQuestion()
                    Answers = CurrentQuestion.getAnswer()
                    CorrectAnswer = CurrentQuestion.getCorrectAnswer()

                    if QuestionType == 'MC':
                        random.shuffle(Answers)
                    if QuestionType == 'QA':

                        QuestionsAndIds = []
                        AnswersAndIds = []

                        for x in range(len(Questions)):
                            QuestionID = x
                            Question = Questions[x]
                            QuestionsAndIds.append((QuestionID,Question))

                        for x in QuestionsAndIds:
                            for key,value in CorrectAnswer.items():
                                if x[1] == key:
                                    AnswersAndIds.append((x[0],value))

                        random.shuffle(AnswersAndIds)

                        Questions = QuestionsAndIds
                        Answers = AnswersAndIds


                    return render_template("QuizPreview.html",user=current_user,QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer)
                else:
                    flash('Inorrect',category='error')

                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()

                    cursor.execute("SELECT NumberOfTimesAnswered FROM Question WHERE QuestionID=?",(str(CurrentQuestion.getQuestionID()),))
                    QuestionInfo = cursor.fetchall()

                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=? WHERE QuestionID=?",(int(QuestionInfo[0][0])+1,str(CurrentQuestion.getQuestionID()),))
                    connection.commit()
                    connection.close()

                    return render_template("QuizPreview.html",user=current_user,QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=True,CorrectAnswer=CorrectAnswer)#if incorrect display correct answer and then go to next question


        if QuestionType == 'FB':
            Answer = request.form.get('Answer')
            if Answer!=None:
                if Answer.lower() == CorrectAnswer:
                        
                    flash('Correct',category='success')

                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()


                    cursor.execute("SELECT NumberOfTimesAnswered,NumberOfTimesAnsweredCorrectly FROM Question WHERE QuestionID=?",(str(CurrentQuestion.getQuestionID()),))
                    QuestionInfo = cursor.fetchall()

                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=?,NumberOfTimesAnsweredCorrectly=? WHERE QuestionID=?",(int(QuestionInfo[0][0])+1,int(QuestionInfo[0][1])+1,str(CurrentQuestion.getQuestionID()),))
                    connection.commit()

                    cursor.execute("SELECT NumberOfQuestionsAnsweredCorrectly FROM Quiz WHERE QuizID=?",(str(UserQuiz.getQuizID()),))
                    QuizInfo = cursor.fetchall()

                    cursor.execute("UPDATE Quiz SET NumberOfQuestionsAnsweredCorrectly=? WHERE QuizID=?",(int(QuizInfo[0][0])+1,str(UserQuiz.getQuizID()),))
                    connection.commit()

                    connection.close()



                    if UserQuiz.getQuestions().size() == 0:
                        count=0
                        QuizID = None
                        for UserAndQuizObject in UserAndQuizObjects:
                            if UserAndQuizObject[0]==UserID:
                                QuizID = UserAndQuizObject[1].getQuizID()
                                UserAndQuizObjects.pop(count)
                            count+=1
                        return redirect(url_for("QuizSection.viewResults",QuizID=QuizID))


                    CurrentQuestion = UserQuiz.NextQuestion()
                    QuestionType = CurrentQuestion.getQuestionType()
                    Questions = CurrentQuestion.getQuestion()
                    Answers = CurrentQuestion.getAnswer()
                    CorrectAnswer = CurrentQuestion.getCorrectAnswer()

                    if QuestionType == 'MC':
                        random.shuffle(Answers)
                    if QuestionType == 'QA':

                        QuestionsAndIds = []
                        AnswersAndIds = []

                        for x in range(len(Questions)):
                            QuestionID = x
                            Question = Questions[x]
                            QuestionsAndIds.append((QuestionID,Question))

                        for x in QuestionsAndIds:
                            for key,value in CorrectAnswer.items():
                                if x[1] == key:
                                    AnswersAndIds.append((x[0],value))

                        random.shuffle(AnswersAndIds)

                        Questions = QuestionsAndIds
                        Answers = AnswersAndIds

                    return render_template("QuizPreview.html",user=current_user,QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer)
                else:
                    flash('Inorrect',category='error')

                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()

                    cursor.execute("SELECT NumberOfTimesAnswered FROM Question WHERE QuestionID=?",(str(CurrentQuestion.getQuestionID()),))
                    QuestionInfo = cursor.fetchall()

                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=? WHERE QuestionID=?",(int(QuestionInfo[0][0])+1,str(CurrentQuestion.getQuestionID()),))
                    connection.commit()
                    connection.close()

                    return render_template("QuizPreview.html",user=current_user,QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=True,CorrectAnswer=CorrectAnswer)#if incorrect display correct answer and then go to next question

        if QuestionType == 'SM':

            MistakeInAnswer=''
            CorrectAnswerToMistake=''


            for x in range(len(Answers.split())):
                if Answers.split()[x] != CorrectAnswer.split()[x]:
                    MistakeInAnswer = Answers.split()[x]
                    CorrectAnswerToMistake = CorrectAnswer.split()[x]



            Answer = request.form.get('incorrectWord')

            if Answer != None:

                if Answer.lower() == MistakeInAnswer:
                                
                    flash('Correct',category='success')

                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()

                    cursor.execute("SELECT NumberOfTimesAnswered,NumberOfTimesAnsweredCorrectly FROM Question WHERE QuestionID=?",(str(CurrentQuestion.getQuestionID()),))
                    QuestionInfo = cursor.fetchall()


                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=?,NumberOfTimesAnsweredCorrectly=? WHERE QuestionID=?",(int(QuestionInfo[0][0])+1,int(QuestionInfo[0][1])+1,str(CurrentQuestion.getQuestionID()),))
                    connection.commit()


                    cursor.execute("SELECT NumberOfQuestionsAnsweredCorrectly FROM Quiz WHERE QuizID=?",(str(UserQuiz.getQuizID()),))
                    QuizInfo = cursor.fetchall()

                    cursor.execute("UPDATE Quiz SET NumberOfQuestionsAnsweredCorrectly=? WHERE QuizID=?",(int(QuizInfo[0][0])+1,str(UserQuiz.getQuizID()),))
                    connection.commit()

                    connection.close()

                    if UserQuiz.getQuestions().size() == 0:
                        count=0
                        QuizID = None
                        for UserAndQuizObject in UserAndQuizObjects:
                            if UserAndQuizObject[0]==UserID:
                                QuizID = UserAndQuizObject[1].getQuizID()
                                UserAndQuizObjects.pop(count)
                            count+=1
                        return redirect(url_for("QuizSection.viewResults",QuizID=QuizID))

                    CurrentQuestion = UserQuiz.NextQuestion()
                    QuestionType = CurrentQuestion.getQuestionType()
                    Questions = CurrentQuestion.getQuestion()
                    Answers = CurrentQuestion.getAnswer()
                    CorrectAnswer = CurrentQuestion.getCorrectAnswer()

                    if QuestionType == 'MC':
                        random.shuffle(Answers)
                    if QuestionType == 'QA':

                        QuestionsAndIds = []
                        AnswersAndIds = []

                        for x in range(len(Questions)):
                            QuestionID = x
                            Question = Questions[x]
                            QuestionsAndIds.append((QuestionID,Question))

                        for x in QuestionsAndIds:
                            for key,value in CorrectAnswer.items():
                                if x[1] == key:
                                    AnswersAndIds.append((x[0],value))

                        random.shuffle(AnswersAndIds)

                        Questions = QuestionsAndIds
                        Answers = AnswersAndIds

                    return render_template("QuizPreview.html",user=current_user,QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer)
                else:
                    flash('Inorrect',category='error')

                    connection = sqlite3.connect("database.db",check_same_thread=False)
                    cursor = connection.cursor()


                    cursor.execute("SELECT NumberOfTimesAnswered FROM Question WHERE QuestionID=?",(str(CurrentQuestion.getQuestionID()),))
                    QuestionInfo = cursor.fetchall()

                    cursor.execute("UPDATE Question SET NumberOfTimesAnswered=? WHERE QuestionID=?",(int(QuestionInfo[0][0])+1,str(CurrentQuestion.getQuestionID()),))
                    connection.commit()
                    connection.close()

                    return render_template("QuizPreview.html",user=current_user,QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=True,CorrectAnswer=CorrectAnswerToMistake)#if incorrect display correct answer and then go to next question


#answer as question and correct mistake as answer


        if QuestionType == 'QA':

            if request.form.get('Box0') == '0' and request.form.get('Box1') == '1' and request.form.get('Box2') == '2':      
                flash('Correct',category='success')


                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()

                cursor.execute("SELECT NumberOfTimesAnswered,NumberOfTimesAnsweredCorrectly FROM Question WHERE QuestionID=?",(str(CurrentQuestion.getQuestionID()),))
                QuestionInfo = cursor.fetchall()


                cursor.execute("UPDATE Question SET NumberOfTimesAnswered=?,NumberOfTimesAnsweredCorrectly=? WHERE QuestionID=?",(int(QuestionInfo[0][0])+1,int(QuestionInfo[0][1])+1,str(CurrentQuestion.getQuestionID()),))
                connection.commit()

                cursor.execute("SELECT NumberOfQuestionsAnsweredCorrectly FROM Quiz WHERE QuizID=?",(str(UserQuiz.getQuizID()),))
                QuizInfo = cursor.fetchall()

                cursor.execute("UPDATE Quiz SET NumberOfQuestionsAnsweredCorrectly=? WHERE QuizID=?",(int(QuizInfo[0][0])+1,str(UserQuiz.getQuizID()),))
                connection.commit()

                connection.close()



                if UserQuiz.getQuestions().size() == 0:
                    count=0
                    QuizID = None
                    for UserAndQuizObject in UserAndQuizObjects:
                        if UserAndQuizObject[0]==UserID:
                            QuizID = UserAndQuizObject[1].getQuizID()
                            UserAndQuizObjects.pop(count)
                        count+=1
                    return redirect(url_for("QuizSection.viewResults",QuizID=QuizID))


                CurrentQuestion = UserQuiz.NextQuestion()
                QuestionType = CurrentQuestion.getQuestionType()
                Questions = CurrentQuestion.getQuestion()
                Answers = CurrentQuestion.getAnswer()
                CorrectAnswer = CurrentQuestion.getCorrectAnswer()

                if QuestionType == 'MC':
                    random.shuffle(Answers)
                if QuestionType == 'QA':

                    QuestionsAndIds = []
                    AnswersAndIds = []

                    for x in range(len(Questions)):
                        QuestionID = x
                        Question = Questions[x]
                        QuestionsAndIds.append((QuestionID,Question))

                    for x in QuestionsAndIds:
                        for key,value in CorrectAnswer.items():
                            if x[1] == key:
                                AnswersAndIds.append((x[0],value))

                    random.shuffle(AnswersAndIds)

                    Questions = QuestionsAndIds
                    Answers = AnswersAndIds

                return render_template("QuizPreview.html",user=current_user,QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer)

            
            else:
                flash('Inorrect',category='error')

                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()

                cursor.execute("SELECT NumberOfTimesAnswered FROM Question WHERE QuestionID=?",(str(CurrentQuestion.getQuestionID()),))
                QuestionInfo = cursor.fetchall()
                cursor.execute("UPDATE Question SET NumberOfTimesAnswered=? WHERE QuestionID=?",(int(QuestionInfo[0][0])+1,str(CurrentQuestion.getQuestionID()),))
                connection.commit()
                connection.close()

                return render_template("QuizPreview.html",user=current_user,QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=True,CorrectAnswer=CorrectAnswer)#if incorrect display correct answer and then go to next question

    return render_template("QuizPreview.html",user=current_user,QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer)




@QuizSection.route('/viewResults/<QuizID>',  methods=['GET', 'POST'])
@login_required
def viewResults(QuizID):

    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT NumberOfQuestions,NumberOfQuestionsAnsweredCorrectly FROM Quiz WHERE QuizID=?",(QuizID,))
    Results = cursor.fetchall()
    connection.close()

    if request.method == 'POST':
        if request.form.get('Finish') == 'Finish':
            return redirect(url_for('HomePage.home'))

    return render_template("viewResults.html",user=current_user,Results=Results,)
    