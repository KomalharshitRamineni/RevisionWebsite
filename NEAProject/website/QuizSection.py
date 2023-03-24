from flask import Blueprint, render_template, flash, redirect,url_for,request,session
from flask_login import login_required, current_user
from .AnkiOperations import extractFlashcards, returnDecksAvailable, checkIfAnkiOpen
import sqlite3
from .models import Flashcard, FlashcardDeck,Quiz
import random
from flask_socketio import join_room, leave_room,send,SocketIO
from string import ascii_uppercase



#socketio = SocketIO(app)




QuizSection = Blueprint('QuizSection',__name__)

UserAndQuizObjects = []
AllQuizQuestions = []

rooms = {}



def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    return code




@QuizSection.route('/quizMenu',  methods=['GET', 'POST'])
@login_required
def quizMenu():
    session.clear()
    if request.method == 'POST':
        if request.form.get('TakeQuiz') == 'Take Quiz':
            return redirect(url_for("QuizSection.quizMenchooseDeckToQuizOnu"))
        
        else:

            name = request.form.get("name")
            code = request.form.get("code")
            join = request.form.get("join", False)
            create = request.form.get("create", False)

            if not name:
                return render_template("quizMenu.html", user=current_user,error="Please enter a name.", code=code, name=name)

            if join != False and not code:
                return render_template("quizMenu.html",user=current_user, error="Please enter a room code.", code=code, name=name)

            room = code
            if create != False:
                room = generate_unique_code(4)
                rooms[room] = {"members": 0, "messages": []}
            elif code not in rooms:
                return render_template("quizMenu.html",user=current_user, error="Room does not exist.", code=code, name=name)
            
            session["room"] = room
            session["name"] = name
            return redirect(url_for("QuizSection.room"))

    return render_template("quizMenu.html",user=current_user)


@QuizSection.route("/room",  methods=['GET', 'POST'])
@login_required
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("QuizSection.quizMenu"))

    return render_template("room.html",user=current_user, code=room, messages=rooms[room]["messages"])



@QuizSection.route('/multiplayerQuiz/<QuizID>',  methods=['GET', 'POST'])
@login_required
def multiplayerQuiz(QuizID):
    QuizID = int(QuizID)
    #create array of questoinIDs in quiz
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
            if x[0][0] in QuestionIds:
                QuizQuestions = x
                QuizExists = True

        if QuizExists == True:
            
            Question = QuizQuestions[0]
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
                QuizQuestions.append(cursor.fetchall()[0])
            connection.close()
            
            AllQuizQuestions.append(QuizQuestions)
            Question = QuizQuestions[0]
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

            if x[0][0] in QuestionIds:

                QuizQuestions = x


        Question = QuizQuestions[0]
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
#removing from whole
        

        if request.form.get('NextQuestion') == 'Next Question':

            for x in AllQuizQuestions:
                if x[0][0] in QuestionIds:
                    AllQuizQuestions[AllQuizQuestions.index(x)].pop(0)
                    QuizQuestions = x

            if len(QuizQuestions) == 0:
                return render_template('quizEnd.html')

                
            Question = QuizQuestions[0]
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

            return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer)

        if QuestionType == 'MC':
            multipleChoiceAnswer = request.form.get('answer')
            if request.form.get('Choose') == 'Submit':
                if multipleChoiceAnswer == CorrectAnswer:

                    flash('Correct',category='success')



                    for x in AllQuizQuestions:
                        if x[0][0] in QuestionIds:
                            AllQuizQuestions[AllQuizQuestions.index(x)].pop(0)
                            QuizQuestions = x
                        
                    if len(QuizQuestions) == 0:
                        return render_template('quizEnd.html')    
                        
                    Question = QuizQuestions[0]
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


                    return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer)
                else:
                    flash('Inorrect',category='error')

                    return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=True,CorrectAnswer=CorrectAnswer)#if incorrect display correct answer and then go to next question


        if QuestionType == 'FB':
            Answer = request.form.get('Answer')
            if Answer!=None:
                if Answer.lower() == CorrectAnswer:
                        





                    for x in AllQuizQuestions:
                        if x[0][0] in QuestionIds:
                            AllQuizQuestions[AllQuizQuestions.index(x)].pop(0)
                            QuizQuestions = x
                    if len(QuizQuestions) == 0:
                        return render_template('quizEnd.html')          

                        
                    Question = QuizQuestions[0]
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

                    return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer)
                else:
                    flash('Inorrect',category='error')

                    return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=True,CorrectAnswer=CorrectAnswer)#if incorrect display correct answer and then go to next question

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


                    
                    for x in AllQuizQuestions:
                        if x[0][0] in QuestionIds:

                            AllQuizQuestions[AllQuizQuestions.index(x)].pop(0)
                            QuizQuestions = x

                    if len(QuizQuestions) == 0:
                        return render_template('quizEnd.html')


                        
                    Question = QuizQuestions[0]
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

                    return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer)
                else:
                    flash('Inorrect',category='error')


                    return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=True,CorrectAnswer=CorrectAnswerToMistake)#if incorrect display correct answer and then go to next question


#answer as question and correct mistake as answer


        if QuestionType == 'QA':

            if request.form.get('Box0') == '0' and request.form.get('Box1') == '1' and request.form.get('Box2') == '2':      
                flash('Correct',category='success')



                for x in AllQuizQuestions:
                    if x[0][0] in QuestionIds:
                        AllQuizQuestions[AllQuizQuestions.index(x)].pop(0)
                        QuizQuestions = x

                if len(QuizQuestions) == 0:
                    return render_template('quizEnd.html')                    
                    
                Question = QuizQuestions[0]
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

                return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer)

            
            else:

                return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=True,CorrectAnswer=CorrectAnswer)#if incorrect display correct answer and then go to next question

    return render_template("multiplayerQuiz.html",QuestionType=QuestionType,Questions=Questions,Answers=Answers,DisplayCorrectAnswer=False,CorrectAnswer=CorrectAnswer)























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
        cursor.execute("INSERT INTO Quiz(QuizID,NumberOfQuestions,NumberOfQuestionsAnsweredCorrectly) values(?,?,?)",(UserQuiz.getQuizID(),NumberOfQuestions,0))#not working fix
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
    