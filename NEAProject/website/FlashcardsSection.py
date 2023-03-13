from flask import Blueprint, render_template, flash, redirect,url_for,request,jsonify,session
from flask_login import login_required, current_user
from .AnkiOperations import extractFlashcards, returnDecksAvailable, checkIfAnkiOpen, returnChildDecks
import sqlite3
from .models import Flashcard, FlashcardDeck
import json
import pickle


UserAndFlashcardDeckObjects = []


def ClearUserAndFlashcardDeckObjects(ID):
    UserID = ID 
    if request.url_rule.endpoint != 'FlashcardsSection.PracticeFlashcards':
        count=0
        for UserAndFlashcardDeckObject in UserAndFlashcardDeckObjects:
            if UserID == UserAndFlashcardDeckObject[0]:
                UserAndFlashcardDeckObjects.pop(count)
            count+=1





FlashcardsSection = Blueprint('FlashcardsSection',__name__)



@FlashcardsSection.route('/flashcards',  methods=['GET', 'POST'])
@login_required
def flashcards():
    
    if request.method == 'POST':

        if request.form.get('action1') == 'Import Flashcards':

            if checkIfAnkiOpen() == False:
                 flash('Anki is not open!', category='error')
                 return render_template("flashcards.html",user=current_user)

            return redirect(url_for('FlashcardsSection.importFlashcards'))

           

        elif  request.form.get('action2') == 'Manage Flashcards':
            return redirect(url_for('FlashcardsSection.chooseFlashcardDeckToManage',PageToDisplay='ManageFlashcards'))


        elif request.form.get('action3') == 'Create New Deck':
            return redirect(url_for('FlashcardsSection.CreateNewDeck'))


        elif request.form.get('action4') == 'Practice Flashcards':
            return redirect(url_for('FlashcardsSection.chooseFlashcardDeckToManage',PageToDisplay='PracticeFlashcards'))

        else:
            pass
    elif request.method == 'GET':
        return render_template("flashcards.html",user=current_user)
    
    return render_template("flashcards.html",user=current_user)
 

@FlashcardsSection.route('/PracticeFlashcards/<DeckName>',  methods=['GET', 'POST'])
@login_required
def PracticeFlashcards(DeckName):
    UserID = current_user.get_id()
    Deck = FlashcardDeck()
    if request.method == 'GET':

        for x in range(len(UserAndFlashcardDeckObjects)):
            IdOfUser = UserAndFlashcardDeckObjects[x][0]
            if IdOfUser == UserID:
                UserAndFlashcardDeckObjects.pop(x)


        Deck = FlashcardDeck()
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()


        cursor.execute("""  SELECT FlashcardsDecksAndUserIDs.ParentFlashcardDeckID 
                            FROM ParentFlashcardDeck,FlashcardsDecksAndUserIDs 
                            WHERE ParentFlashcardDeck.FlashcardDeckName=? 
                            AND FlashcardsDecksAndUserIDs.UserID=? 
                            AND FlashcardsDecksAndUserIDs.ParentFlashcardDeckID=ParentFlashcardDeck.ParentFlashcardDeckID"""
                            ,(DeckName,UserID,))

        parentDeckIDs = cursor.fetchone()
        
        if parentDeckIDs == None:


            cursor.execute("""  SELECT FlashcardDeck.FlashcardDeckID 
                                FROM FlashcardDeck,FlashcardsDecksAndUserIDs 
                                WHERE FlashcardsDecksAndUserIDs.UserID=? 
                                AND FlashcardDeck.FlashcardDeckID=FlashcardsDecksAndUserIDs.FlashcardDeckID 
                                AND FlashcardDeck.FlashcardDeckName=?""",(UserID,DeckName,))
            FlashcardDeckID = cursor.fetchall()

            cursor.execute("SELECT FlashcardID FROM FlashcardsDecksAndUserIDs WHERE FlashcardDeckID=? AND UserID=?",(FlashcardDeckID[0][0],UserID,))
            FlashcardIDs = cursor.fetchall()
            for FlashcardID in FlashcardIDs:
                cursor.execute("SELECT FlashcardQuestion,FlashcardAnswer,Keywords FROM Flashcard WHERE FlashcardID=?",(FlashcardID[0],))
                QuestionsAnswersAndKeywords = cursor.fetchall()
                Question = QuestionsAnswersAndKeywords[0][0]
                Answer = QuestionsAnswersAndKeywords[0][1]
                Keywords = QuestionsAnswersAndKeywords[0][2]
                newFlashcard = Flashcard(Question,Answer)
                newFlashcard.setKeywords(Keywords)
                Deck.AddToFlashcardDeck(newFlashcard)

            connection.close()
            UserIDAndFlashcardDeckObject = (UserID,Deck)
            UserAndFlashcardDeckObjects.append(UserIDAndFlashcardDeckObject)


        else:
            parentDeckID = parentDeckIDs[0]

            cursor.execute("SELECT FlashcardID FROM FlashcardsDecksAndUserIDs WHERE ParentFlashcardDeckID=? AND UserID=?",(parentDeckID,UserID,))

            FlashcardIDs = cursor.fetchall()

            for FlashcardID in FlashcardIDs:
                cursor.execute("SELECT FlashcardQuestion,FlashcardAnswer,Keywords FROM Flashcard WHERE FlashcardID=?",(FlashcardID[0],))
                QuestionsAnswersAndKeywords = cursor.fetchall()
                Question = QuestionsAnswersAndKeywords[0][0]
                Answer = QuestionsAnswersAndKeywords[0][1]
                Keywords = QuestionsAnswersAndKeywords[0][2]
                newFlashcard = Flashcard(Question,Answer)
                newFlashcard.setKeywords(Keywords)
                Deck.AddToFlashcardDeck(newFlashcard)

            connection.close()
            UserIDAndFlashcardDeckObject = (UserID,Deck)
            UserAndFlashcardDeckObjects.append(UserIDAndFlashcardDeckObject)


        for UserAndFlashcardDeckObject in UserAndFlashcardDeckObjects:
            if UserAndFlashcardDeckObject[0]==UserID:
                Deck = UserAndFlashcardDeckObject[1]
        


        ContentToDisplay = Deck.PeekFlashcardDeck().getQuestion()
        actionName = 'question'



        return render_template('practiceFlashcards.html',user=current_user,DeckName=DeckName,ContentToDisplay=ContentToDisplay,actionName=actionName)

    if request.method == 'POST':


        for UserAndFlashcardDeckObject in UserAndFlashcardDeckObjects:
            if UserAndFlashcardDeckObject[0]==UserID:
                Deck = UserAndFlashcardDeckObject[1]


        if request.form.get('question') == 'Flip Card':
            actionName = 'answer'
            ContentToDisplay = Deck.PeekFlashcardDeck().getAnswer()
            return render_template('practiceFlashcards.html',user=current_user,DeckName=DeckName,ContentToDisplay=ContentToDisplay,actionName=actionName)

        if request.form.get('answer') == 'Flip Card':
            actionName = 'question'
            ContentToDisplay = Deck.PeekFlashcardDeck().getQuestion()
            return render_template('practiceFlashcards.html',user=current_user,DeckName=DeckName,ContentToDisplay=ContentToDisplay,actionName=actionName)



        if request.form.get('action3') == 'Next Flashcard':

            if Deck.GetFlashcardDeck().size() == 1:

                ContentToDisplay = Deck.PeekFlashcardDeck().getQuestion()
                actionName = 'question'

                flash('You have reached the end of your reck',category='error')
                return render_template('practiceFlashcards.html',user=current_user,DeckName=DeckName,ContentToDisplay=ContentToDisplay,actionName=actionName)




            Deck.UseFlashcard()
            ContentToDisplay = Deck.PeekFlashcardDeck().getQuestion()
            actionName = 'question'
            return render_template('practiceFlashcards.html',user=current_user,DeckName=DeckName,ContentToDisplay=ContentToDisplay,actionName=actionName)

        if request.form.get('action2') == 'Previous Flashcard':
            if Deck.GetUsedFlashcards().size() == 0:

                ContentToDisplay = Deck.PeekFlashcardDeck().getQuestion()
                actionName = 'question'

                flash('You are already at the start of the deck',category='error')
                return render_template('practiceFlashcards.html',user=current_user,DeckName=DeckName,ContentToDisplay=ContentToDisplay,actionName=actionName)

            Deck.UndoFlashcardUse()
            ContentToDisplay = Deck.PeekFlashcardDeck().getQuestion()
            actionName = 'question'
            return render_template('practiceFlashcards.html',user=current_user,DeckName=DeckName,ContentToDisplay=ContentToDisplay,actionName=actionName)

        if request.form.get('action4') == 'Shuffle Deck':




            
            Deck.ShuffleDeck()
            if Deck.GetFlashcardDeck().size() == 1:
                ContentToDisplay = Deck.PeekFlashcardDeck().getQuestion()
            else:
                Deck.UseFlashcard()
                ContentToDisplay = Deck.PeekFlashcardDeck().getQuestion()

            actionName = 'question'
            return render_template('practiceFlashcards.html',user=current_user,DeckName=DeckName,ContentToDisplay=ContentToDisplay,actionName=actionName)




@FlashcardsSection.route('/CreateNewSubdeck/<DeckName>',  methods=['GET', 'POST'])
@login_required
def CreateNewSubdeck(DeckName):






    UserID = current_user.get_id()
    if request.method == 'POST':


        MainDeckName = DeckName
        SubDeckName = request.form.get('SubDeckName')



        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()



    

        cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(MainDeckName,))
        FlashcardDeckIDsWithSameName= cursor.fetchall()



        if len(FlashcardDeckIDsWithSameName) != 0:

            flash('Flashcard deck already exists with same name! ', category='error')
            connection.close()
            return render_template("createNewSubdeck.html", user=current_user)        

        else:

            
            cursor.execute("INSERT INTO FlashcardDeck (FlashcardDeckName) values(?)",(SubDeckName,))
            connection.commit()
            connection.close()
            flash('Flashcard deck created successfully ', category='success')

        Question = request.form.get('Question')
        Answer = request.form.get('Answer')
        NewFlashcard = Flashcard(Question,Answer)
        NewFlashcard.generateKeywords()
        Keywords = NewFlashcard.getKeywords()

        connection = sqlite3.connect("database.db",check_same_thread=False)#check before inserting,don
        cursor = connection.cursor()





        cursor.execute("SELECT COUNT(FlashcardID) FROM Flashcard")
        NextFlashcardDeckID = cursor.fetchall()
        NextFlashcardDeckID = int(NextFlashcardDeckID[0][0]) + 1

        cursor.execute("INSERT INTO Flashcard (FlashcardID,FlashcardQuestion,FlashcardAnswer,Keywords) values(?,?,?,?)",(NextFlashcardDeckID,Question,Answer,Keywords,))
        connection.commit()





        FlashcardID = NextFlashcardDeckID

        

        cursor.execute("SELECT ParentFlashcardDeckID FROM ParentFlashcardDeck WHERE FlashcardDeckName=?",(MainDeckName,))
        MainFlashcardDeckID = cursor.fetchall()

        cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(SubDeckName,))
        FlashcardDeckID = cursor.fetchall()
        cursor.execute("INSERT INTO FlashcardsDecksAndUserIDs(UserID,FlashcardDeckID,FlashcardID,ParentFlashcardDeckID) values(?,?,?,?)",(UserID,FlashcardDeckID[0][0],FlashcardID,MainFlashcardDeckID[0][0]))
        connection.commit()
        connection.close()
        flash('Flashcard added! ', category='success')
        return redirect(url_for('FlashcardsSection.flashcards',user=current_user))













    return render_template('createNewSubdeck.html',user=current_user)


@FlashcardsSection.route('/CreateNewDeck',  methods=['GET', 'POST'])
@login_required
def CreateNewDeck():
    UserID = current_user.get_id()
    if request.method == 'POST':



        MainDeckName = request.form.get('MainDeckName')
        SubDeckName = request.form.get('SubDeckName')



        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()



    

        cursor.execute("SELECT ParentFlashcardDeckID FROM ParentFlashcardDeck WHERE FlashcardDeckName=?",(MainDeckName,))
        ParentDeckIDsWithSameName= cursor.fetchall()



        if len(ParentDeckIDsWithSameName) != 0:

            flash('Flashcard deck already exists with same name! ', category='error')
            connection.close()
            return render_template("createNewDeck.html", user=current_user)        

        else:

            cursor.execute("INSERT INTO ParentFlashcardDeck (FlashcardDeckName) values(?)",(MainDeckName,))
            connection.commit()
            
            cursor.execute("INSERT INTO FlashcardDeck (FlashcardDeckName) values(?)",(SubDeckName,))
            connection.commit()
            connection.close()
            flash('Flashcard deck created successfully ', category='success')

        Question = request.form.get('Question')
        Answer = request.form.get('Answer')
        NewFlashcard = Flashcard(Question,Answer)
        NewFlashcard.generateKeywords()
        Keywords = NewFlashcard.getKeywords()

        connection = sqlite3.connect("database.db",check_same_thread=False)#check before inserting,don
        cursor = connection.cursor()





        cursor.execute("SELECT COUNT(FlashcardID) FROM Flashcard")
        NextFlashcardDeckID = cursor.fetchall()
        NextFlashcardDeckID = int(NextFlashcardDeckID[0][0]) + 1

        cursor.execute("INSERT INTO Flashcard (FlashcardID,FlashcardQuestion,FlashcardAnswer,Keywords) values(?,?,?,?)",(NextFlashcardDeckID,Question,Answer,Keywords,))
        connection.commit()





        FlashcardID = NextFlashcardDeckID

        

        cursor.execute("SELECT ParentFlashcardDeckID FROM ParentFlashcardDeck WHERE FlashcardDeckName=?",(MainDeckName,))
        MainFlashcardDeckID = cursor.fetchall()

        cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(SubDeckName,))
        FlashcardDeckID = cursor.fetchall()
        cursor.execute("INSERT INTO FlashcardsDecksAndUserIDs(UserID,FlashcardDeckID,FlashcardID,ParentFlashcardDeckID) values(?,?,?,?)",(UserID,FlashcardDeckID[0][0],FlashcardID[0][0],MainFlashcardDeckID[0][0]))
        connection.commit()
        connection.close()
        flash('Flashcard added! ', category='success')
        return redirect(url_for('FlashcardsSection.flashcards',user=current_user))

    return render_template("createNewDeck.html",user=current_user)



@FlashcardsSection.route('/chooseFlashcardDeckToManage/<PageToDisplay>',  methods=['GET', 'POST'])
@login_required
def chooseFlashcardDeckToManage(PageToDisplay):

    UserID = current_user.get_id()

    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()

    UserDeckNames = []
    ParentDecks = []

    cursor.execute("""  SELECT ParentFlashcardDeck.ParentFlashcardDeckID,ParentFlashcardDeck.FlashcardDeckName 
                        FROM ParentFlashcardDeck,FlashcardsDecksAndUserIDs 
                        WHERE FlashcardsDecksAndUserIDs.UserID=? 
                        AND FlashcardsDecksAndUserIDs.ParentFlashcardDeckID = ParentFlashcardDeck.ParentFlashcardDeckID"""
                        ,(UserID,))

    parentDecksOwnedByUser = cursor.fetchall()

    for ParentDeck in parentDecksOwnedByUser:
        ParentDeckID = ParentDeck[0]
        ParentDeckName = ParentDeck[1]

        cursor.execute("""  SELECT FlashcardDeck.FlashcardDeckName
                            FROM FlashcardsDecksAndUserIDs,FlashcardDeck 
                            WHERE FlashcardsDecksAndUserIDs.ParentFlashcardDeckID=?
                            AND FlashcardDeck.FlashcardDeckID=FlashcardsDecksAndUserIDs.FlashcardDeckID
                            """,(ParentDeckID,))
        
    
        subDecksOfParentDecks = cursor.fetchall()

        for subDeck in subDecksOfParentDecks:
            subDeckName = subDeck[0]
            AllDecksOwnedByUser = (UserID,ParentDeckName,subDeckName)
            UserDeckNames.append(AllDecksOwnedByUser)

    connection.close()

    for Name in UserDeckNames:
        if Name[0] == UserID:
            ParentDecks.append(Name[1])

    ParentDecks = list(dict.fromkeys(ParentDecks))

    if request.method == 'POST':
        deckNameToManage = request.form.get('deckName')
        if request.form.get('ManageSubDecks') == 'Manage subdecks':
            

            DeckToDisplay = request.args.get('DeckToDisplay')
            if DeckToDisplay == 'Child':
                ChildDecks = []

                for Name in UserDeckNames:
                    if Name[1] == deckNameToManage and Name[0] == UserID:
                        ChildDecks.append(Name[2])

                ChildDecks = list(dict.fromkeys(ChildDecks))


                return render_template("chooseFlashcardDeckToManage.html", user=current_user,Decks=ChildDecks,PageToDisplay=PageToDisplay,DeckToDisplay='Child')


        if request.form.get('Choose') == 'Choose':

            if PageToDisplay == 'ManageFlashcards':
                return redirect(url_for('FlashcardsSection.manageFlashcards',DeckName=deckNameToManage))
            if PageToDisplay == 'PracticeFlashcards':
                return redirect(url_for('FlashcardsSection.PracticeFlashcards',DeckName=deckNameToManage))

    return render_template("chooseFlashcardDeckToManage.html", user=current_user,Decks=ParentDecks,PageToDisplay=PageToDisplay,DeckToDisplay='Parent')





@FlashcardsSection.route('/manageFlashcards/<DeckName>',  methods=['GET', 'POST'])
@login_required
def manageFlashcards(DeckName):
    UserID = current_user.get_id()

    #Check if parent DeckFirst
    IsDeckAParentDeck = True

    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()

    cursor.execute("""  SELECT FlashcardsDecksAndUserIDs.ParentFlashcardDeckID 
                        FROM ParentFlashcardDeck,FlashcardsDecksAndUserIDs 
                        WHERE ParentFlashcardDeck.FlashcardDeckName=? 
                        AND FlashcardsDecksAndUserIDs.UserID=? 
                        AND FlashcardsDecksAndUserIDs.ParentFlashcardDeckID=ParentFlashcardDeck.ParentFlashcardDeckID"""
                        ,(DeckName,UserID,))

    parentDeckIDs = cursor.fetchone()
    connection.close()

    if parentDeckIDs == None:
        IsDeckAParentDeck = False






    if request.method == 'POST':
        if request.form.get('action1') == 'Change name of deck':
            return redirect(url_for('FlashcardsSection.changeFlashcardDeckName',DeckName=DeckName))
        
        if request.form.get('action2') == 'Add New Flashcards':
            return redirect(url_for('FlashcardsSection.AddNewFlashcards',DeckName=DeckName))

        if request.form.get('action3') == 'Delete Flashcards':
            return redirect(url_for('FlashcardsSection.DeleteFlashcards',DeckName=DeckName))


        
        if request.form.get('action7') == 'Create Subdeck':
            return redirect(url_for('FlashcardsSection.CreateNewSubdeck',DeckName=DeckName))

        if request.form.get('action') == 'Delete Deck':

            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()

            if IsDeckAParentDeck == True:

                
                cursor.execute("""  SELECT ParentFlashcardDeck.ParentFlashcardDeckID 
                                    FROM FlashcardsDecksAndUserIDs,ParentFlashcardDeck 
                                    WHERE ParentFlashcardDeck.FlashcardDeckName=? 
                                    AND FlashcardsDecksAndUserIDs.UserID=? 
                                    AND FlashcardsDecksAndUserIDs.ParentFlashcardDeckID=ParentFlashcardDeck.ParentFlashcardDeckID""",
                                    (DeckName,UserID,))
                
                FlashcardDeckToDelete = cursor.fetchone()
                cursor.execute("""  SELECT FlashcardID 
                                    FROM FlashcardsDecksAndUserIDs
                                    WHERE ParentFlashcardDeckID=?""",
                                    (FlashcardDeckToDelete[0],))
                
                FlashcardIDsToDelete = cursor.fetchall()
                for FlashcardID in FlashcardIDsToDelete:
                    cursor.execute("DELETE FROM Flashcard WHERE FlashcardID=?",(FlashcardID[0],))
                    connection.commit()

                cursor.execute("DELETE FROM ParentFlashcardDeck WHERE ParentFlashcardDeckID=?",(FlashcardDeckToDelete[0],))
                connection.commit()
                cursor.execute("DELETE FROM FlashcardsDecksAndUserIDs WHERE ParentFlashcardDeckID=?",(FlashcardDeckToDelete[0],))
                connection.commit()

                
                connection.close()
                flash('Deck deleted!',category='success')



            else:
                cursor.execute("""  SELECT FlashcardDeck.FlashcardDeckID 
                                    FROM FlashcardsDecksAndUserIDs,FlashcardDeck 
                                    WHERE FlashcardDeck.FlashcardDeckName=? AND FlashcardsDecksAndUserIDs.UserID=? 
                                    AND FlashcardsDecksAndUserIDs.FlashcardDeckID=FlashcardDeck.FlashcardDeckID""",
                                    (DeckName,UserID,))
                

                FlashcardDeckToDelete = cursor.fetchone()

                cursor.execute("""  SELECT FlashcardID 
                                    FROM FlashcardsDecksAndUserIDs
                                    WHERE FlashcardDeckID=?""",
                                    (FlashcardDeckToDelete[0],))
                
                FlashcardIDsToDelete = cursor.fetchall()
                for FlashcardID in FlashcardIDsToDelete:
                    cursor.execute("DELETE FROM Flashcard WHERE FlashcardID=?",(FlashcardID[0],))
                    connection.commit()

                cursor.execute("DELETE FROM FlashcardDeck WHERE FlashcardDeckID=?",(FlashcardDeckToDelete[0],))
                connection.commit()
                cursor.execute("DELETE FROM FlashcardsDecksAndUserIDs WHERE ParentFlashcardDeckID=?",(FlashcardDeckToDelete[0],))
                connection.commit()

                connection.close()
                flash('Deck deleted!',category='success')


            return(redirect(url_for('FlashcardsSection.flashcards')))

        if request.form.get('action4') == 'Edit contents':
            return redirect(url_for('FlashcardsSection.ChooseFlashcardToEdit',DeckName=DeckName))


        if request.form.get('action5') == 'View flashcards':

            if IsDeckAParentDeck == True:
                FlashcardQueryResults = []
                FlashcardIdsQuestionsAndAnswers = []

                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()
                cursor.execute("""  SELECT FlashcardsDecksAndUserIDs.FlashcardID,FlashcardDeck.FlashcardDeckName
                                    FROM FlashcardDeck,ParentFlashcardDeck,FlashcardsDecksAndUserIDs
                                    WHERE FlashcardsDecksAndUserIDs.UserID=?
                                    AND ParentFlashcardDeck.FlashcardDeckName=?
                                    AND FlashcardDeck.FlashcardDeckID=FlashcardsDecksAndUserIDs.FlashcardDeckID
        
                                    AND ParentFlashcardDeck.ParentFlashcardDeckID=FlashcardsDecksAndUserIDs.ParentFlashcardDeckID
                                """,(UserID,DeckName,))
                FlashcardIDs = cursor.fetchall()
                print(FlashcardIDs)

                for index in range(len(FlashcardIDs)):
                    cursor.execute("SELECT * from Flashcard WHERE FlashcardID=?",(FlashcardIDs[index][0],))
                    Flashcard = cursor.fetchone()
                    FlashcardAndDeckName = (FlashcardIDs[index][1],Flashcard)
                    FlashcardQueryResults.append(FlashcardAndDeckName)

                connection.close()

                for Result in FlashcardQueryResults:
                    FlashcardIdQuestionAndAnswer = (Result[0],Result[1][0],Result[1][1],Result[1][2])
                    FlashcardIdsQuestionsAndAnswers.append(FlashcardIdQuestionAndAnswer)

                FlashcardIdsQuestionsAndAnswers = list(dict.fromkeys(FlashcardIdsQuestionsAndAnswers))

            else:



                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()


                cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(DeckName,))
                DeckID = cursor.fetchall()

                FlashcardQueryResults = []
                FlashcardIdsQuestionsAndAnswers = []

                cursor.execute("SELECT FlashcardID FROM FlashcardsDecksAndUserIDs WHERE UserID=? AND FlashcardDeckID=?",(UserID,DeckID[0][0],))
                FlashcardIDs = cursor.fetchall()
                for index in range(len(FlashcardIDs)):
                    cursor.execute("SELECT * from Flashcard WHERE FlashcardID=?",(FlashcardIDs[index][0],))
                    Flashcard = cursor.fetchone()
                    FlashcardQueryResults.append(Flashcard)

                for Result in FlashcardQueryResults:
                    FlashcardIdQuestionAndAnswer = (Result[0],Result[1],Result[2])
                    FlashcardIdsQuestionsAndAnswers.append(FlashcardIdQuestionAndAnswer)

                connection.close()
                FlashcardIdsQuestionsAndAnswers = list(dict.fromkeys(FlashcardIdsQuestionsAndAnswers))
            return render_template('viewFlashcards.html', data=FlashcardIdsQuestionsAndAnswers, user=current_user, count = len(FlashcardIdsQuestionsAndAnswers), DeckName=DeckName,IsDeckAParentDeck=IsDeckAParentDeck)

    return render_template('manageFlashcards.html', user=current_user,DeckName=DeckName,IsDeckAParentDeck=IsDeckAParentDeck)


@FlashcardsSection.route('/autocomplete/<DeckName>',  methods=['GET', 'POST'])
def autocomplete(DeckName):

    UserID = current_user.get_id()
    #FlashcardQuestionAndIDs = {}
    FlashcardQuestions = []
     
    search = request.args.get('q')


    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(DeckName,))#after check if deck belongs to user as multiple users can have same decknames
    DeckID = cursor.fetchall()
    cursor.execute("SELECT FlashcardID FROM FlashcardsDecksAndUserIDs WHERE UserID=? AND FlashcardDeckID=?",(UserID,DeckID[0][0],))
    Flashcards = cursor.fetchall()

    for x in range(len(Flashcards)):
        FlashcardID = Flashcards[x][0]
        StringToSearchFor = str(search)
        cursor.execute(f"SELECT FlashcardQuestion FROM Flashcard WHERE FlashcardQuestion LIKE '%{StringToSearchFor}%' AND FlashcardID =? ",(FlashcardID,))
        Question = cursor.fetchall()
        if len(Question) != 0:
            FlashcardQuestions.append(Question[0][0])
            

        #FlashcardQuestionAndIDs.update({FlashcardID:Question[0][0]})

    connection.close()

    
     
    #FlashcardQuestions = FlashcardQuestionAndIDs.values()
    #return jsonify(QuestionsAndIDs = FlashcardQuestionAndIDs)
    
    return jsonify(Questions = FlashcardQuestions)

    







    
@FlashcardsSection.route('/DeleteFlashcards/<DeckName>',  methods=['GET', 'POST'])
@login_required
def DeleteFlashcards(DeckName):
    UserID = current_user.get_id()

    
    if request.method == 'POST':




        QuestionToDelete = request.form.get('autocomplete')#change name of variables to avoid plagarism
    
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        #First get FlashcardID
        #Then check wheteher it is owned by user
        #if owned then remove

        cursor.execute("SELECT FlashcardID FROM Flashcard WHERE FlashcardQuestion=?",(QuestionToDelete,))
        FlashcardIDs = cursor.fetchall() #Same questions can be stored in database, so can return different IDs
        for FlashcardId in FlashcardIDs:
            cursor.execute("SELECT UserID FROM FlashcardsDecksAndUserIDs WHERE FlashcardID=?",(FlashcardId[0],))
            UserWhoOwnsFlashcard = cursor.fetchall()
            if UserID == UserWhoOwnsFlashcard[0][0]:
                cursor.execute("DELETE FROM FlashcardsDecksAndUserIDs WHERE UserID=? AND FlashcardID=?",(UserID,FlashcardId[0],))
                connection.commit()
                flash('Flashcard removed ', category='success')

        connection.close()
        return render_template("deleteFlashcards.html",user=current_user,DeckName=DeckName)
    return render_template("deleteFlashcards.html",user=current_user,DeckName=DeckName)

    
@FlashcardsSection.route('/ChooseFlashcardToEdit/<DeckName>',  methods=['GET', 'POST'])
@login_required
def ChooseFlashcardToEdit(DeckName):
    UserID = current_user.get_id()
    if request.method == 'POST':
        QuestionAndAnswer = []
        FlashcardToEdit = request.form.get('autocomplete')
        
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        

        cursor.execute("SELECT FlashcardID FROM Flashcard WHERE FlashcardQuestion=?",(FlashcardToEdit,))
        FlashcardIDs = cursor.fetchall() #Same questions can be stored in database, so can return different IDs
        for FlashcardId in FlashcardIDs:
            cursor.execute("SELECT UserID FROM FlashcardsDecksAndUserIDs WHERE FlashcardID=?",(FlashcardId[0],))
            UserWhoOwnsFlashcard = cursor.fetchall()
            if UserID == UserWhoOwnsFlashcard[0][0]:
                FlashcardIdOfQuestion = FlashcardId[0]
                cursor.execute("SELECT FlashcardQuestion FROM Flashcard WHERE FlashcardID=?",(FlashcardIdOfQuestion,))
                Question = cursor.fetchall()
                QuestionAndAnswer.append(Question[0][0])
                cursor.execute("SELECT FlashcardAnswer FROM Flashcard WHERE FlashcardID=?",(FlashcardIdOfQuestion,))
                Answer = cursor.fetchall()
                QuestionAndAnswer.append(Answer[0][0])
                QuestionAndAnswer.append(FlashcardIdOfQuestion)

        connection.close()
        #redirect(url_for('FlashcardsSection.EditContent',DeckName=DeckName))
        return render_template("editContents.html",user=current_user,OptionChosen=True,QuestionAndAnswer=QuestionAndAnswer,DeckName=DeckName)
        
    return render_template("editContents.html",user=current_user,OptionChosen=False,QuestionAndAnswer=None,DeckName=DeckName)




@FlashcardsSection.route('/EditContent/<DeckName>',  methods=['GET', 'POST'])
@login_required
def EditContent(DeckName):
        
    if request.method == 'POST':

        OldQuestionAndAnswer = []
        OldQuestionAndAnswerID = request.args.get('OldQuestionAndAnswerID')


        FlashcardIdOfQuestion = OldQuestionAndAnswerID
        QuestionFromForm = request.form.get('Question')
        AnswerFromForm = request.form.get('Answer')



        UpdatedFlashcard = Flashcard(QuestionFromForm,AnswerFromForm)
        UpdatedFlashcard.generateKeywords()

        FlashcardQuestion = UpdatedFlashcard.getQuestion()
        FlashcardAnswer = UpdatedFlashcard.getAnswer()
        Keywords = UpdatedFlashcard.getKeywords()

    
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
    
        cursor.execute("SELECT FlashcardQuestion FROM Flashcard WHERE FlashcardID=?",(FlashcardIdOfQuestion,))
        OldQuestion = cursor.fetchall()
        OldQuestionAndAnswer.append(OldQuestion[0][0])
        cursor.execute("SELECT FlashcardAnswer FROM Flashcard WHERE FlashcardID=?",(FlashcardIdOfQuestion,))
        OldAnswer = cursor.fetchall()
        OldQuestionAndAnswer.append(OldAnswer[0][0])


        OldQuestionAndAnswer.append(FlashcardIdOfQuestion)


        if QuestionFromForm != OldQuestion[0][0]: #i.e if question has changed from origional

            cursor.execute("SELECT FlashcardID FROM Flashcard WHERE FlashcardQuestion=?",(QuestionFromForm,))
            DuplicateFlashcards = cursor.fetchall()#Checking if changed to a question that already exists


            if len(DuplicateFlashcards) == 0:

                cursor.execute("UPDATE Flashcard SET FlashcardQuestion=?,FlashcardAnswer=?, keywords=? WHERE FlashcardID=?",(FlashcardQuestion,FlashcardAnswer,Keywords,FlashcardIdOfQuestion,))
                connection.commit()
                flash('Question updated! ', category='success')

            else:
                flash('Question already exists! ', category='error')
                return redirect(url_for("FlashcardsSection.ChooseFlashcardToEdit",DeckName=DeckName))

        if AnswerFromForm != OldAnswer[0][0]:
            cursor.execute("UPDATE Flashcard SET FlashcardQuestion=?,FlashcardAnswer=?, keywords=? WHERE FlashcardID=?",(FlashcardQuestion,FlashcardAnswer,Keywords,FlashcardIdOfQuestion,))
            connection.commit()
            flash('Answer updated! ', category='success')

        connection.close()

        return redirect(url_for("FlashcardsSection.ChooseFlashcardToEdit",DeckName=DeckName))
    
    return render_template("editContents.html",user=current_user,DeckName=DeckName,OptionChosen=True,QuestionAndAnswer=OldQuestionAndAnswer)






@FlashcardsSection.route('/AddNewFlashcards/<DeckName>',  methods=['GET', 'POST'])
@login_required
def AddNewFlashcards(DeckName):
    UserID = current_user.get_id()
    if request.method == 'POST':

        Question = request.form.get('Question')#consider removing OOP here
        Answer = request.form.get('Answer')
        NewFlashcard = Flashcard(Question,Answer)
        NewFlashcard.generateKeywords()
        Keywords = NewFlashcard.getKeywords()

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("SELECT FlashcardID FROM Flashcard WHERE FlashcardQuestion=? AND FlashcardAnswer =?",(Question,Answer,))#wrong querey need to be specific to user
        DuplicateFlashcards = cursor.fetchall()#needs to check if flashcard exists in same deck

        Duplicates = False

        for DuplicateFlashcard in DuplicateFlashcards:
            cursor.execute("SELECT UserID FROM FlashcardsDecksAndUserIDs WHERE FlashcardID=?", (DuplicateFlashcard[0],))#statemetn is necessary as duplicat flashcards may exist in database but user cannot have duplicate
            UserIDsToWhichFlashcardsBelongTo = cursor.fetchall()
            if len(UserIDsToWhichFlashcardsBelongTo) != 0:
                Duplicates = True
    
        connection.close()

        if Duplicates == True:
            flash('Flashcard already exists! ', category='error')
            return render_template('addNewFlashcards.html',user=current_user, DeckName=DeckName)
        else:

            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()

            cursor.execute("INSERT INTO Flashcard (FlashcardQuestion,FlashcardAnswer,Keywords) values(?,?,?)",(Question,Answer,Keywords,))
            connection.commit()

            cursor.execute("SELECT FlashcardID FROM Flashcard WHERE FlashcardQuestion=? AND FlashcardAnswer=? AND Keywords=?",(Question,Answer,Keywords,))
            FlashcardID = cursor.fetchall()
            cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(DeckName,))
            DeckID = cursor.fetchall()

            cursor.execute("INSERT INTO FlashcardsDecksAndUserIDs (FlashcardID,UserID,FlashcardDeckID) values(?,?,?)",(FlashcardID[0][0],UserID,DeckID[0][0],))
            connection.commit()
            connection.close

            flash('Flashcard added ', category='success')
            return render_template('addNewFlashcards.html',user=current_user, DeckName=DeckName)

    return render_template('addNewFlashcards.html',user=current_user, DeckName=DeckName)





@FlashcardsSection.route('/changeFlashcardDeckName/<DeckName>',  methods=['GET', 'POST'])
@login_required
def changeFlashcardDeckName(DeckName):
    UserID=current_user.get_id()
    IsDeckAParentDeck = True

    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()

    cursor.execute("""  SELECT FlashcardsDecksAndUserIDs.ParentFlashcardDeckID 
                        FROM ParentFlashcardDeck,FlashcardsDecksAndUserIDs 
                        WHERE ParentFlashcardDeck.FlashcardDeckName=? 
                        AND FlashcardsDecksAndUserIDs.UserID=? 
                        AND FlashcardsDecksAndUserIDs.ParentFlashcardDeckID=ParentFlashcardDeck.ParentFlashcardDeckID"""
                        ,(DeckName,UserID,))

    parentDeckIDs = cursor.fetchone()
    connection.close()

    if parentDeckIDs == None:
        IsDeckAParentDeck = False



    if request.method == 'POST':
        newName = request.form.get('name')
        if newName == DeckName:
            flash('Name entered is the same as the current name! ', category='error')
            return render_template("changeFlashcardDeckName.html", user=current_user,DeckName=DeckName)
        


        if IsDeckAParentDeck == True:


            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()

            
            cursor.execute("SELECT ParentFlashcardDeckID FROM ParentFlashcardDeck WHERE FlashcardDeckName=?",(newName,))
            DeckIDOfNewName = cursor.fetchall()
            cursor.execute("SELECT ParentFlashcardDeckID FROM ParentFlashcardDeck WHERE FlashcardDeckName=?",(DeckName,))
            DeckIDOfOldName = cursor.fetchall()

            if len(DeckIDOfNewName)!= 0:
                flash('Flashcard deck already exists with same name! ', category='error')
                return render_template("changeFlashcardDeckName.html", user=current_user,DeckName=DeckName)
            else:
                cursor.execute("UPDATE ParentFlashcardDeck SET FlashcardDeckName=? WHERE ParentFlashcardDeckID=?",(newName,DeckIDOfOldName[0][0],))
                connection.commit()
                flash('Name changed successfully ', category='success')

            connection.close()


        else:




            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()

            
            cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(newName,))
            DeckIDOfNewName = cursor.fetchall()
            cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(DeckName,))
            DeckIDOfOldName = cursor.fetchall()

            if len(DeckIDOfNewName)!= 0:
                flash('Flashcard deck already exists with same name! ', category='error')
                return render_template("changeFlashcardDeckName.html", user=current_user,DeckName=DeckName)
            else:
                cursor.execute("UPDATE FlashcardDeck SET FlashcardDeckName=? WHERE FlashcardDeckID=?",(newName,DeckIDOfOldName[0][0],))
                connection.commit()
                flash('Name changed successfully ', category='success')

            connection.close()

        return redirect(url_for('FlashcardsSection.manageFlashcards',DeckName=newName))
    
    return render_template('changeFlashcardDeckName.html',user=current_user,DeckName=DeckName)







@FlashcardsSection.route('/importFlashcards',  methods=['GET', 'POST'])
@login_required
def importFlashcards():
    UserID = current_user.get_id()
    flashcardDecks = returnDecksAvailable()
    if request.method == 'POST':

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        deckNameToImport = request.form.get('deckName')


        childDecks = returnChildDecks(deckNameToImport)

#import whole deck but in anki operations give deckname 


        cursor.execute("INSERT INTO ParentFlashcardDeck(FlashcardDeckName) values(?)",(deckNameToImport,))
        connection.commit()
        cursor.execute("SELECT ParentFlashcardDeckID FROM ParentFlashcardDeck WHERE FlashcardDeckName=?",(deckNameToImport,))
        ParentFlashcardDeckID = cursor.fetchall()
        #ParentFlashcardDeckID= ParentFlashcardDeckID[0][0]






        FlashcardsData = extractFlashcards(deckNameToImport)
        for card in FlashcardsData:

            #FlashcardID = card.get('cardID')
            FlashcardQuestion = card.get('question')
            FlashcardAnswer = card.get('answer')
            Keywords = card.get('keywords')
            FlashcardDeckName = card.get('deckName')
            #FlashcardDeckID = card.get('deckID')

            #try:
            cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(FlashcardDeckName,))
            FlashcardDeckIDs = cursor.fetchall()
            if len(FlashcardDeckIDs) == 0:
                cursor.execute("INSERT INTO FlashcardDeck (FlashcardDeckName) values(?)", (FlashcardDeckName,))
                connection.commit()

            cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(FlashcardDeckName,))
            FlashcardDeckIDs = cursor.fetchall()
            #FlashcardDeckID = FlashcardDeckIDs[0][0]







            
            cursor.execute("INSERT INTO Flashcard (FlashcardQuestion,FlashcardAnswer,Keywords) values(?,?,?)", (FlashcardQuestion,FlashcardAnswer,Keywords,))
            connection.commit()

            cursor.execute("SELECT FlashcardID FROM Flashcard WHERE FlashcardQuestion=? AND FlashcardAnswer=? AND Keywords=?",(FlashcardQuestion,FlashcardAnswer,Keywords,))
            FlashcardID = cursor.fetchall()
            FlashcardID=FlashcardID[0][0]#need to check FlashcardsDecksAndUserIDs when looking at flashcar ids as sub decks may contain duplicarsd

            cursor.execute("INSERT INTO FlashcardsDecksAndUserIDs (FlashcardID,UserID,FlashcardDeckID,ParentFlashcardDeckID) values(?,?,?,?)",(FlashcardID,UserID,FlashcardDeckIDs[0][0],ParentFlashcardDeckID[0][0],))
            
            
            connection.commit()


                    
                

            # except:    
            #     flash('You are trying to import flashcards that have already been imported!', category='error')#wrong error message needs to check if has same questions

            
        connection.close()

        flash('Flashcards Imported!', category='success')


        return redirect(url_for('FlashcardsSection.flashcards'))

    return render_template("importFlashcards.html",user=current_user, flashcardDecks=flashcardDecks)