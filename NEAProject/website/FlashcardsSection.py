from flask import Blueprint, render_template, flash, redirect,url_for,request,jsonify
from flask_login import login_required, current_user
from .ankiAPIOperations import extractFlashcards, returnDecksAvailable, checkIfAnkiOpen
import sqlite3
from .models import Flashcard, FlashcardDeck



userAndFlashcardDeckObjects = []
#Global variable used to keep track of flashcard decks being used
flashcardsSection = Blueprint('flashcardsSection',__name__)

@flashcardsSection.route('/flashcards',  methods=['GET', 'POST'])
@login_required
def flashcards():
    #Flashcard menu page
    if request.method == 'POST':
        if request.form.get('action1') == 'Import Flashcards':

            if checkIfAnkiOpen() == False:
                 flash('Anki is not open!', category='error')
                 return render_template("flashcards.html",user=current_user)
                
            return redirect(url_for('flashcardsSection.importFlashcards'))
            #If API connection is successful then redirected to page to import flashcards
        elif  request.form.get('action2') == 'Manage Flashcards':
            return redirect(url_for('flashcardsSection.chooseFlashcardDeckToManage',pageToDisplay='ManageFlashcards'))
            #Redirects to page to choose a flashcard deck to practice
        elif request.form.get('action3') == 'Create New Deck':
            return redirect(url_for('flashcardsSection.CreateNewDeck'))
            #Redirects to page to create new deck

        elif request.form.get('action4') == 'Practice Flashcards':
            return redirect(url_for('flashcardsSection.chooseFlashcardDeckToManage',pageToDisplay='PracticeFlashcards'))
            #Redirects to page to choose a flashcard deck to practice
        else:
            pass
    elif request.method == 'GET':
        return render_template("flashcards.html",user=current_user)
        #Renders quiz menu on get request
    return render_template("flashcards.html",user=current_user)
   


@flashcardsSection.route('/PracticeFlashcards/<deckName>',  methods=['GET', 'POST'])
@login_required
def PracticeFlashcards(deckName):
    UserID = current_user.get_id()
    Deck = FlashcardDeck()
    if request.method == 'GET':

        for x in range(len(userAndFlashcardDeckObjects)):
            IdOfUser = userAndFlashcardDeckObjects[x][0]
            if IdOfUser == UserID:
                userAndFlashcardDeckObjects.pop(x)
        #If the user already has a flashcard deck object then the object is retrieved from the global array
        Deck = FlashcardDeck()#Flashcard deck object created
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT FlashcardsDecksAndUserIDs.ParentFlashcardDeckID 
            FROM FlashcardsDecksAndUserIDs 
            INNER JOIN ParentFlashcardDeck 
            ON FlashcardsDecksAndUserIDs.ParentFlashcardDeckID = ParentFlashcardDeck.ParentFlashcardDeckID 
            WHERE ParentFlashcardDeck.FlashcardDeckName = ? 
            AND FlashcardsDecksAndUserIDs.UserID = ? 
        """, (deckName, UserID,))
        #Parent deck id of the deck name specified is queried
        parentDeckIDs = cursor.fetchone()
        if parentDeckIDs == None:
            #If there are not results from the query then the deck name supplies is not a parent deck
            cursor.execute("""
                SELECT FlashcardDeck.FlashcardDeckID 
                FROM FlashcardDeck 
                INNER JOIN FlashcardsDecksAndUserIDs 
                ON FlashcardDeck.FlashcardDeckID = FlashcardsDecksAndUserIDs.FlashcardDeckID 
                WHERE FlashcardsDecksAndUserIDs.UserID = ? 
                AND FlashcardDeck.FlashcardDeckName = ?
            """, (UserID, deckName,))
            #If deck name is not a parent deck then it has to be a child deck
            flashcardDeckID = cursor.fetchall()
            #The deck id of the deck name specified is queried
            cursor.execute("SELECT FlashcardID FROM FlashcardsDecksAndUserIDs WHERE FlashcardDeckID=? AND UserID=?",(flashcardDeckID[0][0],UserID,))
            flashcardIDs = cursor.fetchall()
            #All the flashcardIDs withn the flashcard deck specified are queried
            for flashcardID in flashcardIDs:
                cursor.execute("SELECT FlashcardQuestion,FlashcardAnswer,Keywords FROM Flashcard WHERE FlashcardID=?",(flashcardID[0],))
                #The flashcard details are queried for all the flashcards within the flashcard deck
                questionsAnswersAndKeywords = cursor.fetchall()
                question = questionsAnswersAndKeywords[0][0]
                answer = questionsAnswersAndKeywords[0][1]
                keywords = questionsAnswersAndKeywords[0][2]
                
                newFlashcard = Flashcard(flashcardID[0],question,answer,UserID)
                #New object is created with the details queried
                newFlashcard.setKeywords(keywords)
                Deck.addToFlashcardDeck(newFlashcard)
                #The flashcard object is pushed onto the flashcard deck stack

            connection.close()
            userIDAndFlashcardDeckObject = (UserID,Deck)
            userAndFlashcardDeckObjects.append(userIDAndFlashcardDeckObject)
            #The userID and the flashcard deck object are linked and added to the global array

        else:
            #If the the deckname specified is a parent deck
            parentDeckID = parentDeckIDs[0]
            cursor.execute("SELECT FlashcardID FROM FlashcardsDecksAndUserIDs WHERE ParentFlashcardDeckID=? AND UserID=?",(parentDeckID,UserID,))
            flashcardIDs = cursor.fetchall()
            #All ids of flashcards within the parent deck are queried
            for flashcardID in flashcardIDs:
                cursor.execute("SELECT FlashcardQuestion,FlashcardAnswer,Keywords FROM Flashcard WHERE FlashcardID=?",(flashcardID[0],))
                questionsAnswersAndKeywords = cursor.fetchall()
                question = questionsAnswersAndKeywords[0][0]
                answer = questionsAnswersAndKeywords[0][1]
                keywords = questionsAnswersAndKeywords[0][2]
                newFlashcard = Flashcard(flashcardID[0],question,answer,UserID)
                #Flashcard object is created with the details from the query
                newFlashcard.setKeywords(keywords)
                Deck.addToFlashcardDeck(newFlashcard)
                #The flashcard object is pushed onto the flashcard deck stack

            connection.close()
            userIDAndFlashcardDeckObject = (UserID,Deck)
            userAndFlashcardDeckObjects.append(userIDAndFlashcardDeckObject)
            #The userID and the flashcard deck object are linked and added to the global array

        for userAndFlashcardDeckObject in userAndFlashcardDeckObjects:
            if userAndFlashcardDeckObject[0]==UserID:
                Deck = userAndFlashcardDeckObject[1]
                #Search for the deck object associated with the user's id
        contentToDisplay = Deck.peekFlashcardDeck().getQuestion()
        #The first question in the deck is returned so that it can be displayed to the user
        actionName = 'question'
        #Specifies to the template that the string being passed is a question
        return render_template('practiceFlashcards.html',user=current_user,deckName=deckName,ContentToDisplay=contentToDisplay,actionName=actionName)
        #page is displayed with the first question
    if request.method == 'POST':

        for userAndFlashcardDeckObject in userAndFlashcardDeckObjects:
            if userAndFlashcardDeckObject[0]==UserID:
                Deck = userAndFlashcardDeckObject[1]
                #Search for the deck object associated with the user's id

        if request.form.get('question') == 'Flip Card':
            #If user presses button to flip card
            actionName = 'answer'
            #Specifies to the template that the string being passed is a now an answer
            contentToDisplay = Deck.peekFlashcardDeck().getAnswer()
            #The answer to the current flashcard is returned
            return render_template('practiceFlashcards.html',user=current_user,deckName=deckName,ContentToDisplay=contentToDisplay,actionName=actionName)

        if request.form.get('answer') == 'Flip Card':
            actionName = 'question'
            #Specifies to the template that the string being passed is a now an answer
            contentToDisplay = Deck.peekFlashcardDeck().getQuestion()
            #The question to the current flashcard is returned
            return render_template('practiceFlashcards.html',user=current_user,deckName=deckName,ContentToDisplay=contentToDisplay,actionName=actionName)

        if request.form.get('action3') == 'Next Flashcard':
            #If user presses button to change to next flashcard
            if Deck.getFlashcardDeck().size() == 1:
                #If there are is only one flashcard left in the stack
                contentToDisplay = Deck.peekFlashcardDeck().getQuestion()
                actionName = 'question'
                flash('You have reached the end of your reck',category='error')
                return render_template('practiceFlashcards.html',user=current_user,deckName=deckName,ContentToDisplay=contentToDisplay,actionName=actionName)

            Deck.useFlashcard()
            #If there are more then 1 flashcards in the stack
            contentToDisplay = Deck.peekFlashcardDeck().getQuestion()
            actionName = 'question'
            return render_template('practiceFlashcards.html',user=current_user,deckName=deckName,ContentToDisplay=contentToDisplay,actionName=actionName)

        if request.form.get('action2') == 'Previous Flashcard':
            #If user presses button to change to previous flashcard
            if Deck.getUsedFlashcards().size() == 0:
                #If the used flashcards stack is empty then no flashcards have been used
                contentToDisplay = Deck.peekFlashcardDeck().getQuestion()
                #Current question is redisplayed
                actionName = 'question'
                flash('You are already at the start of the deck',category='error')
                return render_template('practiceFlashcards.html',user=current_user,deckName=deckName,ContentToDisplay=contentToDisplay,actionName=actionName)

            Deck.undoFlashcardUse()
            #If the user is not at the start of the deck
            contentToDisplay = Deck.peekFlashcardDeck().getQuestion()
            actionName = 'question'
            return render_template('practiceFlashcards.html',user=current_user,deckName=deckName,ContentToDisplay=contentToDisplay,actionName=actionName)

        if request.form.get('action4') == 'Shuffle Deck':
            #If the user presses button to shuffle deck
            Deck.shuffleDeck()
            #The flashcard objects in the stack are shuffled
            if Deck.getFlashcardDeck().size() == 1:
                #If there is only one flashcard left then shuffle function doesn't do anything
                #Same flashcard question is redisplayed
                contentToDisplay = Deck.peekFlashcardDeck().getQuestion()
            else:
                #If shuffle is successful then the next flashcard is displayed
                Deck.useFlashcard()
                contentToDisplay = Deck.peekFlashcardDeck().getQuestion()

            actionName = 'question'
            return render_template('practiceFlashcards.html',user=current_user,deckName=deckName,ContentToDisplay=contentToDisplay,actionName=actionName)




@flashcardsSection.route('/CreateNewSubdeck/<DeckName>',  methods=['GET', 'POST'])
@login_required
def CreateNewSubdeck(DeckName):
    #Deckname is passed in as a parameter from other pages
    #Deck name here represents the parent flashcard deck
    UserID = current_user.get_id()
    if request.method == 'POST':

        mainDeckName = DeckName
        subDeckName = request.form.get('SubDeckName')
        #Form details are recieved
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(mainDeckName,))
        flashcardDeckIDsWithSameName= cursor.fetchall()
        #query searches for flashcard decks with the same name as the one entered
        if len(flashcardDeckIDsWithSameName) != 0:
            #If query results are not empty
            flash('Flashcard deck already exists with same name! ', category='error')
            connection.close()
            return render_template("createNewSubdeck.html", user=current_user)        

        else:
            #If deck name entered is not in database then the database is updated
            cursor.execute("INSERT INTO FlashcardDeck (FlashcardDeckName) values(?)",(subDeckName,))
            connection.commit()
            connection.close()
            flash('Flashcard deck created successfully ', category='success')

        question = request.form.get('Question')
        answer = request.form.get('Answer')
        #Form details are recieved
        newFlashcard = Flashcard(0,question,answer,UserID)
        #Flashcard object is created so that keywords can be extracted
        keywords = newFlashcard.getKeywords()
        #keywords generated

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(FlashcardID) FROM Flashcard")
        nextFlashcardDeckID = cursor.fetchall()
        nextFlashcardDeckID = int(nextFlashcardDeckID[0][0]) + 1
        #FlashcardID is a primary key and is autoincremented
        #Because it is auto incremented, the next flashcard ID can be identified by looking at the number of flashcards
        cursor.execute("INSERT INTO Flashcard (FlashcardID,FlashcardQuestion,FlashcardAnswer,Keywords) values(?,?,?,?)",(nextFlashcardDeckID,question,answer,keywords,))
        connection.commit()
        flashcardID = nextFlashcardDeckID

        cursor.execute("SELECT ParentFlashcardDeckID FROM ParentFlashcardDeck WHERE FlashcardDeckName=?",(mainDeckName,))
        mainFlashcardDeckID = cursor.fetchall()
        cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(subDeckName,))
        flashcardDeckID = cursor.fetchall()
        cursor.execute("INSERT INTO FlashcardsDecksAndUserIDs(UserID,FlashcardDeckID,FlashcardID,ParentFlashcardDeckID) values(?,?,?,?)",(UserID,flashcardDeckID[0][0],flashcardID,mainFlashcardDeckID[0][0]))
        connection.commit()
        #Database is updated with new flashcard
        connection.close()
        flash('Flashcard added! ', category='success')
        return redirect(url_for('flashcardsSection.flashcards',user=current_user))

    return render_template('createNewSubdeck.html',user=current_user)



@flashcardsSection.route('/CreateNewDeck',  methods=['GET', 'POST'])
@login_required
def CreateNewDeck():
    UserID = current_user.get_id()
    if request.method == 'POST':

        mainDeckName = request.form.get('mainDeckName')
        subDeckName = request.form.get('SubDeckName')
        #Form details are recieved
        if mainDeckName == '' or subDeckName == '':     #Ensures form is not blank
            flash('Please fill out the form fully',category='error')
            return render_template("createNewDeck.html",user=current_user)
        
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("SELECT ParentFlashcardDeckID FROM ParentFlashcardDeck WHERE FlashcardDeckName=?",(mainDeckName,))
        parentDeckIDsWithSameName= cursor.fetchall()
        #query searches for parent flashcard decks with the same name as the one entered

        if len(parentDeckIDsWithSameName) != 0:
            #If query results are not empty
            flash('Flashcard deck already exists with same name! ', category='error')
            connection.close()
            return render_template("createNewDeck.html", user=current_user)        

        else:
            #If query results are empty
            cursor.execute("INSERT INTO ParentFlashcardDeck (FlashcardDeckName) values(?)",(mainDeckName,))
            connection.commit()
            cursor.execute("INSERT INTO FlashcardDeck (FlashcardDeckName) values(?)",(subDeckName,))
            connection.commit()
            connection.close()
            #Database is updated with new flashcard deck
            flash('Flashcard deck created successfully ', category='success')

        question = request.form.get('Question')
        answer = request.form.get('Answer')

        if question == '' or answer == '':     #Ensures form is not blank
            flash('Please fill out the form fully',category='error')
            return render_template("createNewDeck.html",user=current_user)

        #Form data is recieved
        newFlashcard = Flashcard(0,question,answer,UserID)
        #Flashcard object is created so that keywords can be extracted
        keywords = newFlashcard.getKeywords()
        #Keywords generated

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(FlashcardID) FROM Flashcard")
        nextFlashcardDeckID = cursor.fetchall()
        #FlashcardID is a primary key and is autoincremented
        #Because it is auto incremented, the next flashcard ID can be identified by looking at the number of flashcards
        nextFlashcardDeckID = int(nextFlashcardDeckID[0][0]) + 1
        cursor.execute("INSERT INTO Flashcard (FlashcardID,FlashcardQuestion,FlashcardAnswer,Keywords) values(?,?,?,?)",(nextFlashcardDeckID,question,answer,keywords,))
        connection.commit()
    
        flashcardID = nextFlashcardDeckID
        cursor.execute("SELECT ParentFlashcardDeckID FROM ParentFlashcardDeck WHERE FlashcardDeckName=?",(mainDeckName,))
        mainFlashcardDeckID = cursor.fetchall()

        cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(subDeckName,))
        flashcardDeckID = cursor.fetchall()

        cursor.execute("INSERT INTO FlashcardsDecksAndUserIDs(UserID,FlashcardDeckID,FlashcardID,ParentFlashcardDeckID) values(?,?,?,?)",(UserID,flashcardDeckID[0][0],flashcardID[0][0],mainFlashcardDeckID[0][0]))
        connection.commit()
        connection.close()
        #Database is updated with the new parent flashcard deck
        flash('Flashcard added! ', category='success')
        return redirect(url_for('flashcardsSection.flashcards',user=current_user))

    return render_template("createNewDeck.html",user=current_user)



@flashcardsSection.route('/chooseFlashcardDeckToManage/<pageToDisplay>',  methods=['GET', 'POST'])
@login_required
def chooseFlashcardDeckToManage(pageToDisplay):
    UserID = current_user.get_id()

    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()

    userDeckNames = []
    parentDecks = []

    cursor.execute("""
        SELECT ParentFlashcardDeck.ParentFlashcardDeckID, ParentFlashcardDeck.FlashcardDeckName 
        FROM ParentFlashcardDeck 
        INNER JOIN FlashcardsDecksAndUserIDs 
        ON ParentFlashcardDeck.ParentFlashcardDeckID = FlashcardsDecksAndUserIDs.ParentFlashcardDeckID 
        WHERE FlashcardsDecksAndUserIDs.UserID = ?
    """, (UserID,))

    parentDecksOwnedByUser = cursor.fetchall()
    #All parent decks owned by user are queried
    for parentDeck in parentDecksOwnedByUser:
        parentDeckID = parentDeck[0]
        parentDeckName = parentDeck[1]

        cursor.execute("""
            SELECT FlashcardDeck.FlashcardDeckName 
            FROM FlashcardsDecksAndUserIDs 
            INNER JOIN FlashcardDeck 
            ON FlashcardsDecksAndUserIDs.FlashcardDeckID = FlashcardDeck.FlashcardDeckID 
            WHERE FlashcardsDecksAndUserIDs.ParentFlashcardDeckID = ?
        """, (parentDeckID,))

        subDecksOfParentDecks = cursor.fetchall()
        #The sub decks within the parent decks owned are queried

        for subDeck in subDecksOfParentDecks:
            subDeckName = subDeck[0]
            allDecksOwnedByUser = (UserID,parentDeckName,subDeckName)
            userDeckNames.append(allDecksOwnedByUser)
            #the parent decks and their corresponding child decks added to the array
    connection.close()

    for name in userDeckNames:
        if name[0] == UserID:
            parentDecks.append(name[1])
    #Checks if the user who owns the deck is the current user
    parentDecks = list(dict.fromkeys(parentDecks))
    #Duplicates are removed

    if request.method == 'POST':
        deckNameToManage = request.form.get('deckName')
        if deckNameToManage == None:
            flash('Please choose one of the options',category='error')
            return render_template("chooseFlashcardDeckToManage.html", user=current_user,Decks=parentDecks,PageToDisplay=pageToDisplay,DeckToDisplay='Parent')
        #Form data recieved
        if request.form.get('ManageSubDecks') == 'Manage subdecks':
            #If user presses button to manage subdecks
            deckToDisplay = request.args.get('DeckToDisplay')
            if deckToDisplay == 'Child':
                childDecks = []

                for name in userDeckNames:
                    if name[1] == deckNameToManage and name[0] == UserID:
                        childDecks.append(name[2])

                childDecks = list(dict.fromkeys(childDecks))
                #The child decks of the parent deck given are returned and redisplayed to the suer
                return render_template("chooseFlashcardDeckToManage.html", user=current_user,Decks=childDecks,PageToDisplay=pageToDisplay,DeckToDisplay='Child')

        if request.form.get('Choose') == 'Choose':
            #If the user chooses an flashcard deck
            if pageToDisplay == 'ManageFlashcards':
                return redirect(url_for('flashcardsSection.manageFlashcards',deckName=deckNameToManage))
            if pageToDisplay == 'PracticeFlashcards':
                return redirect(url_for('flashcardsSection.PracticeFlashcards',deckName=deckNameToManage))
            if pageToDisplay == 'TakeQuiz':
                return redirect(url_for('quizSection.TakeQuiz',DeckName=deckNameToManage))
            #The same page is used to redirect to differnt pages
            #The pageToDisplay variable is used to know which page to redirect to
    return render_template("chooseFlashcardDeckToManage.html", user=current_user,Decks=parentDecks,PageToDisplay=pageToDisplay,DeckToDisplay='Parent')



@flashcardsSection.route('/manageFlashcards/<deckName>',  methods=['GET', 'POST'])
@login_required
def manageFlashcards(deckName):
    UserID = current_user.get_id()

    isDeckAParentDeck = True

    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT FlashcardsDecksAndUserIDs.ParentFlashcardDeckID 
        FROM FlashcardsDecksAndUserIDs 
        INNER JOIN ParentFlashcardDeck 
        ON FlashcardsDecksAndUserIDs.ParentFlashcardDeckID = ParentFlashcardDeck.ParentFlashcardDeckID 
        WHERE ParentFlashcardDeck.FlashcardDeckName = ? 
        AND FlashcardsDecksAndUserIDs.UserID = ?
    """, (deckName, UserID,))

    parentDeckIDs = cursor.fetchone()
    connection.close()
    #Database is queried to check if the deckname passed in as the parameter is a parent deck

    if parentDeckIDs == None:
        #If query results are empty then it is not a parent deck
        isDeckAParentDeck = False

    if request.method == 'POST':
        if request.form.get('action1') == 'Change name of deck':
            #If the user presses the button to change name of deck
            return redirect(url_for('flashcardsSection.changeFlashcardDeckName',DeckName=deckName))
        
        if request.form.get('action2') == 'Add New Flashcards':
            #If the user presses the button to add new flashcards
            return redirect(url_for('flashcardsSection.AddNewFlashcards',deckName=deckName))

        if request.form.get('action3') == 'Delete Flashcards':
            #If the user presses the button to delete flashcards
            return redirect(url_for('flashcardsSection.DeleteFlashcards',DeckName=deckName))
        
        if request.form.get('action7') == 'Create Subdeck':
            #If the user presses the button to create subdeck
            return redirect(url_for('flashcardsSection.CreateNewSubdeck',DeckName=deckName))

        if request.form.get('action') == 'Delete Deck':
            #If the user presses the button to delete deck
            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()

            if isDeckAParentDeck == True:

                cursor.execute("""
                    SELECT ParentFlashcardDeck.ParentFlashcardDeckID 
                    FROM FlashcardsDecksAndUserIDs 
                    INNER JOIN ParentFlashcardDeck 
                    ON FlashcardsDecksAndUserIDs.ParentFlashcardDeckID = ParentFlashcardDeck.ParentFlashcardDeckID 
                    WHERE ParentFlashcardDeck.FlashcardDeckName = ? 
                    AND FlashcardsDecksAndUserIDs.UserID = ?
                """, (deckName, UserID,))

                flashcardDeckToDelete = cursor.fetchone()
                cursor.execute("""  SELECT FlashcardID 
                                    FROM FlashcardsDecksAndUserIDs
                                    WHERE ParentFlashcardDeckID=?""",
                                    (flashcardDeckToDelete[0],))
                
                flashcardIDsToDelete = cursor.fetchall()
                for flashcardID in flashcardIDsToDelete:
                    cursor.execute("DELETE FROM Flashcard WHERE FlashcardID=?",(flashcardID[0],))
                    connection.commit()

                cursor.execute("DELETE FROM ParentFlashcardDeck WHERE ParentFlashcardDeckID=?",(flashcardDeckToDelete[0],))
                connection.commit()
                cursor.execute("DELETE FROM FlashcardsDecksAndUserIDs WHERE ParentFlashcardDeckID=?",(flashcardDeckToDelete[0],))
                connection.commit()
                #If the deck name is a parent deck then it is removed from its relevant tables in the database
                connection.close()
                flash('Deck deleted!',category='success')

            else:

                cursor.execute("""
                    SELECT FlashcardDeck.FlashcardDeckID 
                    FROM FlashcardsDecksAndUserIDs 
                    INNER JOIN FlashcardDeck 
                    ON FlashcardsDecksAndUserIDs.FlashcardDeckID = FlashcardDeck.FlashcardDeckID 
                    WHERE FlashcardDeck.FlashcardDeckName = ? 
                    AND FlashcardsDecksAndUserIDs.UserID = ?
                """, (deckName, UserID,))

                flashcardDeckToDelete = cursor.fetchone()

                cursor.execute("""  SELECT FlashcardID 
                                    FROM FlashcardsDecksAndUserIDs
                                    WHERE FlashcardDeckID=?""",
                                    (flashcardDeckToDelete[0],))
                
                flashcardIDsToDelete = cursor.fetchall()
                for flashcardID in flashcardIDsToDelete:
                    cursor.execute("DELETE FROM Flashcard WHERE FlashcardID=?",(flashcardID[0],))
                    connection.commit()

                cursor.execute("DELETE FROM FlashcardDeck WHERE FlashcardDeckID=?",(flashcardDeckToDelete[0],))
                connection.commit()
                cursor.execute("DELETE FROM FlashcardsDecksAndUserIDs WHERE ParentFlashcardDeckID=?",(flashcardDeckToDelete[0],))
                connection.commit()

                connection.close()
                #If the deck name is a child deck then it is removed from its relevant tables in the database
                flash('Deck deleted!',category='success')

            return(redirect(url_for('flashcardsSection.flashcards')))

        if request.form.get('action4') == 'Edit contents':
            #If the user presses the button to edit contents
            return redirect(url_for('flashcardsSection.ChooseFlashcardToEdit',deckName=deckName))

        if request.form.get('action5') == 'View flashcards':
            #If the user presses the button to view flashcards
            if isDeckAParentDeck == True:
                #If the current deck that the user is managing is a parent deck then all flashcards associated with it are queried and returned
                flashcardQueryResults = []
                flashcardIDsQuestionsAndAnswers = []

                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()

                cursor.execute("""
                    SELECT FlashcardsDecksAndUserIDs.FlashcardID, FlashcardDeck.FlashcardDeckName
                    FROM FlashcardsDecksAndUserIDs 
                    INNER JOIN FlashcardDeck 
                    ON FlashcardsDecksAndUserIDs.FlashcardDeckID = FlashcardDeck.FlashcardDeckID 
                    INNER JOIN ParentFlashcardDeck 
                    ON FlashcardsDecksAndUserIDs.ParentFlashcardDeckID = ParentFlashcardDeck.ParentFlashcardDeckID
                    WHERE FlashcardsDecksAndUserIDs.UserID = ?
                    AND ParentFlashcardDeck.FlashcardDeckName = ?
                """, (UserID, deckName,))

                flashcardIDs = cursor.fetchall()
    
                for index in range(len(flashcardIDs)):
                    cursor.execute("SELECT * from Flashcard WHERE FlashcardID=?",(flashcardIDs[index][0],))
                    Flashcard = cursor.fetchone()
                    FlashcardAndDeckName = (flashcardIDs[index][1],Flashcard)
                    flashcardQueryResults.append(FlashcardAndDeckName)

                connection.close()

                for result in flashcardQueryResults:
                    flashcardIDQuestionAndAnswer = (result[0],result[1][0],result[1][1],result[1][2])
                    flashcardIDsQuestionsAndAnswers.append(flashcardIDQuestionAndAnswer)

                flashcardIDsQuestionsAndAnswers = list(dict.fromkeys(flashcardIDsQuestionsAndAnswers))
                
            else:
                #If the current deck that the user is managing is a child deck then all flashcards associated with it are queried and returned
                connection = sqlite3.connect("database.db",check_same_thread=False)
                cursor = connection.cursor()

                cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(deckName,))
                deckID = cursor.fetchall()

                flashcardQueryResults = []
                flashcardIDsQuestionsAndAnswers = []

                cursor.execute("SELECT FlashcardID FROM FlashcardsDecksAndUserIDs WHERE UserID=? AND FlashcardDeckID=?",(UserID,deckID[0][0],))
                flashcardIDs = cursor.fetchall()
                for index in range(len(flashcardIDs)):
                    cursor.execute("SELECT * from Flashcard WHERE FlashcardID=?",(flashcardIDs[index][0],))
                    flashcard = cursor.fetchone()
                    flashcardQueryResults.append(flashcard)

                for result in flashcardQueryResults:
                    flashcardIDQuestionAndAnswer = (result[0],result[1],result[2])
                    flashcardIDsQuestionsAndAnswers.append(flashcardIDQuestionAndAnswer)

                connection.close()
                flashcardIDsQuestionsAndAnswers = list(dict.fromkeys(flashcardIDsQuestionsAndAnswers))
            return render_template('viewFlashcards.html', data=flashcardIDsQuestionsAndAnswers, user=current_user, count = len(flashcardIDsQuestionsAndAnswers), DeckName=deckName,IsDeckAParentDeck=isDeckAParentDeck)
            #Flashcards associated with the deckname specified are displayed to the user
    return render_template('manageFlashcards.html', user=current_user,DeckName=deckName,IsDeckAParentDeck=isDeckAParentDeck)


@flashcardsSection.route('/searchByQuestions/<DeckName>',  methods=['GET', 'POST'])
def searchByQuestions(DeckName):

    UserID = current_user.get_id()
    flashcardQuestions = []
    search = request.args.get('searchItem')
    #The item chosen is returned
    #Jquery is used to create a drop down search bar
    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(DeckName,))
    deckID = cursor.fetchall()
    cursor.execute("SELECT FlashcardID FROM FlashcardsDecksAndUserIDs WHERE UserID=? AND FlashcardDeckID=?",(UserID,deckID[0][0],))
    flashcards = cursor.fetchall()

    for x in range(len(flashcards)):
        flashcardID = flashcards[x][0]
        stringToSearchFor = str(search)
        cursor.execute(f"SELECT FlashcardQuestion FROM Flashcard WHERE FlashcardQuestion LIKE '%{stringToSearchFor}%' AND FlashcardID =? ",(flashcardID,))
        question = cursor.fetchall()
        if len(question) != 0:
            flashcardQuestions.append(question[0][0])
    #All the flashcard questions within the deck are returned
    connection.close()
    return jsonify(Questions = flashcardQuestions)
    #Items are converted into javascript objects and passed into the HTML file
    #The questions are used to the search by question


@flashcardsSection.route('/DeleteFlashcards/<DeckName>',  methods=['GET', 'POST'])
@login_required
def DeleteFlashcards(DeckName):
    UserID = current_user.get_id()

    if request.method == 'POST':

        questionToDelete = request.form.get('searchByQuestions')
        #Form data is recieved
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("SELECT FlashcardID FROM Flashcard WHERE FlashcardQuestion=?",(questionToDelete,))
        flashcardIDs = cursor.fetchall()
        #The flashcard ID of the flashcard question chosen is queried
        removed =False
        count = 0
        while removed == False:
            flashcardId = flashcardIDs[count]
            cursor.execute("SELECT UserID FROM FlashcardsDecksAndUserIDs WHERE FlashcardID=?",(flashcardId[0],))
            userWhoOwnsFlashcard = cursor.fetchall()
            userWhoOwnsFlashcard = list(dict.fromkeys(userWhoOwnsFlashcard))

            if UserID == str(userWhoOwnsFlashcard[0][0]):
                cursor.execute("DELETE FROM FlashcardsDecksAndUserIDs WHERE UserID=? AND FlashcardID=?",(UserID,flashcardId[0],))
                connection.commit()
                flash('Flashcard removed ', category='success')
                removed=True
                #Flashcard is removed from the database
            count+=1


        for flashcardId in flashcardIDs:
            cursor.execute("SELECT UserID FROM FlashcardsDecksAndUserIDs WHERE FlashcardID=?",(flashcardId[0],))
            userWhoOwnsFlashcard = cursor.fetchall()

            if UserID == userWhoOwnsFlashcard[0][0]:
                cursor.execute("DELETE FROM FlashcardsDecksAndUserIDs WHERE UserID=? AND FlashcardID=?",(UserID,flashcardId[0],))
                connection.commit()
                flash('Flashcard removed ', category='success')
                #Flashcard is removed from the database



        connection.close()
        return render_template("deleteFlashcards.html",user=current_user,DeckName=DeckName)
    return render_template("deleteFlashcards.html",user=current_user,DeckName=DeckName)


    
@flashcardsSection.route('/ChooseFlashcardToEdit/<deckName>',  methods=['GET', 'POST'])
@login_required
def ChooseFlashcardToEdit(deckName):
    UserID = current_user.get_id()
    if request.method == 'POST':
        questionAndAnswer = []
        flashcardToEdit = request.form.get('searchByQuestions')
        #Form data is recieved
        
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        
        cursor.execute("SELECT FlashcardID FROM Flashcard WHERE FlashcardQuestion=?",(flashcardToEdit,))
        flashcardIDs = cursor.fetchall()
        #The flashcard ID of the flashcard question chosen is queried

        for flashcardId in flashcardIDs:
            cursor.execute("SELECT UserID FROM FlashcardsDecksAndUserIDs WHERE FlashcardID=?",(flashcardId[0],))
            userWhoOwnsFlashcard = cursor.fetchall()
            userWhoOwnsFlashcard = list(dict.fromkeys(userWhoOwnsFlashcard))
            #Duplicates are removed

            if userWhoOwnsFlashcard!= []:#Not an empty array
                if UserID == str(userWhoOwnsFlashcard[0][0]):
                    flashcardIdOfQuestion = flashcardId[0]
                    cursor.execute("SELECT FlashcardQuestion FROM Flashcard WHERE FlashcardID=?",(flashcardIdOfQuestion,))
                    question = cursor.fetchall()

                    questionAndAnswer.append(question[0][0])
                    cursor.execute("SELECT FlashcardAnswer FROM Flashcard WHERE FlashcardID=?",(flashcardIdOfQuestion,))
                    answer = cursor.fetchall()

                    questionAndAnswer.append(answer[0][0])
                    questionAndAnswer.append(flashcardIdOfQuestion)

        connection.close()
        #The user is redirected to a page to edit the contents of the flashcard chosen
        return render_template("editContents.html",user=current_user,OptionChosen=True,QuestionAndAnswer=questionAndAnswer,DeckName=deckName)
        
    return render_template("editContents.html",user=current_user,OptionChosen=False,QuestionAndAnswer=None,DeckName=deckName)



@flashcardsSection.route('/EditContent/<deckName>',  methods=['GET', 'POST'])
@login_required
def EditContent(deckName):
    UserID=current_user.get_id()
    if request.method == 'POST':

        oldQuestionAndAnswer = []
        oldQuestionAndAnswerID = request.args.get('oldQuestionAndAnswerID')
        flashcardIdOfQuestion = oldQuestionAndAnswerID
        questionFromForm = request.form.get('Question')
        answerFromForm = request.form.get('Answer')
        #Form data is recieved
        updatedFlashcard = Flashcard(0,questionFromForm,answerFromForm,UserID)
        #Flashcard object created
        #Keywords are generated again as contents of the flashcard have changed

        flashcardQuestion = updatedFlashcard.getQuestion()
        flashcardAnswer = updatedFlashcard.getAnswer()
        keywords = updatedFlashcard.getKeywords()

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
    
        cursor.execute("SELECT FlashcardQuestion FROM Flashcard WHERE FlashcardID=?",(flashcardIdOfQuestion,))
        oldQuestion = cursor.fetchall()

        oldQuestionAndAnswer.append(oldQuestion[0][0])
        cursor.execute("SELECT FlashcardAnswer FROM Flashcard WHERE FlashcardID=?",(flashcardIdOfQuestion,))
        oldAnswer = cursor.fetchall()
        #The question and answer of the flashcard are queried

        oldQuestionAndAnswer.append(oldAnswer[0][0])
        oldQuestionAndAnswer.append(flashcardIdOfQuestion)

        if questionFromForm != oldQuestion[0][0]: 
            #if question has been changed from the origional

            cursor.execute("SELECT FlashcardID FROM Flashcard WHERE FlashcardQuestion=?",(questionFromForm,))
            duplicateFlashcards = cursor.fetchall()

            if len(duplicateFlashcards) == 0:
                #If there are no flashcards with the same question
                cursor.execute("UPDATE Flashcard SET FlashcardQuestion=?,FlashcardAnswer=?, keywords=? WHERE FlashcardID=?",(flashcardQuestion,flashcardAnswer,keywords,flashcardIdOfQuestion,))
                connection.commit()
                flash('Question updated! ', category='success')
                #Database is updated with new contents
            else:
                flash('Question already exists! ', category='error')
                return redirect(url_for("flashcardsSection.ChooseFlashcardToEdit",DeckName=deckName))

        if answerFromForm != oldAnswer[0][0]:
            #If the question has changed
            cursor.execute("UPDATE Flashcard SET FlashcardQuestion=?,FlashcardAnswer=?, keywords=? WHERE FlashcardID=?",(flashcardQuestion,flashcardAnswer,keywords,flashcardIdOfQuestion,))
            connection.commit()
            flash('Answer updated! ', category='success')
            #Database is updated with new contents
        connection.close()
        return redirect(url_for("flashcardsSection.ChooseFlashcardToEdit",DeckName=deckName))
    
    return render_template("editContents.html",user=current_user,DeckName=deckName,OptionChosen=True,QuestionAndAnswer=oldQuestionAndAnswer)



@flashcardsSection.route('/AddNewFlashcards/<deckName>',  methods=['GET', 'POST'])
@login_required
def AddNewFlashcards(deckName):
    UserID = current_user.get_id()
    if request.method == 'POST':

        question = request.form.get('Question')
        answer = request.form.get('Answer')
        #Form data recieved
        newFlashcard = Flashcard(0,question,answer,UserID)
        #Flashcard object created
        keywords = newFlashcard.getKeywords()
        #Keywords are generated as a new flashcard is being created

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("SELECT FlashcardID FROM Flashcard WHERE FlashcardQuestion=? AND FlashcardAnswer =?",(question,answer,))
        #Queries for flashcards that match with the form details entered

        duplicateFlashcards = cursor.fetchall()
        duplicates = False

        for duplicateFlashcard in duplicateFlashcards:
            cursor.execute("SELECT UserID FROM FlashcardsDecksAndUserIDs WHERE FlashcardID=?", (duplicateFlashcard[0],))
            UserIDsToWhichFlashcardsBelongTo = cursor.fetchall()
            if len(UserIDsToWhichFlashcardsBelongTo) != 0:
                duplicates = True
            #If a flashcard already exists with the question and answer entered
        connection.close()

        if duplicates == True:
            flash('Flashcard already exists! ', category='error')
            return render_template('addNewFlashcards.html',user=current_user, DeckName=deckName)
        else:
            #If the flashcard entered is
            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()

            cursor.execute("INSERT INTO Flashcard (FlashcardQuestion,FlashcardAnswer,Keywords) values(?,?,?)",(question,answer,keywords,))
            connection.commit()

            cursor.execute("SELECT FlashcardID FROM Flashcard WHERE FlashcardQuestion=? AND FlashcardAnswer=? AND Keywords=?",(question,answer,keywords,))
            flashcardID = cursor.fetchall()
            cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(deckName,))
            deckID = cursor.fetchall()

            cursor.execute("INSERT INTO FlashcardsDecksAndUserIDs (FlashcardID,UserID,FlashcardDeckID) values(?,?,?)",(flashcardID[0][0],UserID,deckID[0][0],))
            connection.commit()
            connection.close

            flash('Flashcard added ', category='success')
            #Database is updated with the new flashcard
            return render_template('addNewFlashcards.html',user=current_user, DeckName=deckName)

    return render_template('addNewFlashcards.html',user=current_user, DeckName=deckName)




@flashcardsSection.route('/changeFlashcardDeckName/<DeckName>',  methods=['GET', 'POST'])
@login_required
def changeFlashcardDeckName(DeckName):
    UserID=current_user.get_id()
    isDeckAParentDeck = True

    connection = sqlite3.connect("database.db",check_same_thread=False)
    cursor = connection.cursor()

    cursor.execute("""
                        SELECT FlashcardsDecksAndUserIDs.ParentFlashcardDeckID
                        FROM FlashcardsDecksAndUserIDs
                        JOIN ParentFlashcardDeck ON FlashcardsDecksAndUserIDs.ParentFlashcardDeckID = ParentFlashcardDeck.ParentFlashcardDeckID
                        WHERE ParentFlashcardDeck.FlashcardDeckName = ?
                        AND FlashcardsDecksAndUserIDs.UserID = ?
                    """,(DeckName,UserID,))

    parentDeckIDs = cursor.fetchone()
    connection.close()
    #Query searches for parent decks with the same name as the one given

    if parentDeckIDs == None:
        #If query has no results
        isDeckAParentDeck = False

    if request.method == 'POST':
        newName = request.form.get('name')
        #form data recieved
        if newName == DeckName:
            flash('Name entered is the same as the current name! ', category='error')
            return render_template("changeFlashcardDeckName.html", user=current_user,DeckName=DeckName)
        
        if isDeckAParentDeck == True:

            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()

            cursor.execute("SELECT ParentFlashcardDeckID FROM ParentFlashcardDeck WHERE FlashcardDeckName=?",(newName,))
            deckIDOfNewName = cursor.fetchall()
            cursor.execute("SELECT ParentFlashcardDeckID FROM ParentFlashcardDeck WHERE FlashcardDeckName=?",(DeckName,))
            deckIDOfOldName = cursor.fetchall()

            if len(deckIDOfNewName)!= 0:
                flash('Flashcard deck already exists with same name! ', category='error')
                return render_template("changeFlashcardDeckName.html", user=current_user,DeckName=DeckName)
            else:
                cursor.execute("UPDATE ParentFlashcardDeck SET FlashcardDeckName=? WHERE ParentFlashcardDeckID=?",(newName,deckIDOfOldName[0][0],))
                connection.commit()
                flash('Name changed successfully ', category='success')
            #Database is updated with the new flashcard deck name
            connection.close()

        else:
            #If the deck is not a parent deck
            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()

            cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(newName,))
            deckIDOfNewName = cursor.fetchall()
            cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(DeckName,))
            deckIDOfOldName = cursor.fetchall()

            if len(deckIDOfNewName)!= 0:
                flash('Flashcard deck already exists with same name! ', category='error')
                return render_template("changeFlashcardDeckName.html", user=current_user,DeckName=DeckName)
            else:
                cursor.execute("UPDATE FlashcardDeck SET FlashcardDeckName=? WHERE FlashcardDeckID=?",(newName,deckIDOfOldName[0][0],))
                connection.commit()
                flash('Name changed successfully ', category='success')
                #Database is updated with the new flashcard deck name
            connection.close()

        return redirect(url_for('flashcardsSection.manageFlashcards',deckName=newName))
    
    return render_template('changeFlashcardDeckName.html',user=current_user,DeckName=DeckName)



@flashcardsSection.route('/importFlashcards',  methods=['GET', 'POST'])
@login_required
def importFlashcards():
    UserID = current_user.get_id()
    flashcardDecks = returnDecksAvailable()
    #sends request to Anki API to get flashcard decks available
    if request.method == 'POST':
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        deckNameToImport = request.form.get('deckName')
        if deckNameToImport == None:
            flash('Please choose one of the options',category='error')
            return render_template("importFlashcards.html",user=current_user, flashcardDecks=flashcardDecks)
        #Form data is recieved - the deck name chosen to import

        cursor.execute("INSERT INTO ParentFlashcardDeck(FlashcardDeckName) values(?)",(deckNameToImport,))
        connection.commit()
        cursor.execute("SELECT ParentFlashcardDeckID FROM ParentFlashcardDeck WHERE FlashcardDeckName=?",(deckNameToImport,))
        parentFlashcardDeckID = cursor.fetchall()
        #Database is updated with the new parent flashcard deck
        FlashcardsData = extractFlashcards(deckNameToImport)
        #Function is called to extract flashcards from Anki
        for card in FlashcardsData:

            FlashcardQuestion = card.get('question')
            FlashcardAnswer = card.get('answer')
            keywords = card.get('keywords')
            FlashcardDeckName = card.get('deckName')

            cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(FlashcardDeckName,))
            FlashcardDeckIDs = cursor.fetchall()
            if len(FlashcardDeckIDs) == 0:
                cursor.execute("INSERT INTO FlashcardDeck (FlashcardDeckName) values(?)", (FlashcardDeckName,))
                connection.commit()

            cursor.execute("SELECT FlashcardDeckID FROM FlashcardDeck WHERE FlashcardDeckName=?",(FlashcardDeckName,))
            FlashcardDeckIDs = cursor.fetchall()
     
            cursor.execute("INSERT INTO Flashcard (FlashcardQuestion,FlashcardAnswer,Keywords) values(?,?,?)", (FlashcardQuestion,FlashcardAnswer,keywords,))
            connection.commit()

            cursor.execute("SELECT FlashcardID FROM Flashcard WHERE FlashcardQuestion=? AND FlashcardAnswer=? AND Keywords=?",(FlashcardQuestion,FlashcardAnswer,keywords,))
            flashcardID = cursor.fetchall()
            flashcardID=flashcardID[0][0]

            cursor.execute("INSERT INTO FlashcardsDecksAndUserIDs (FlashcardID,UserID,FlashcardDeckID,ParentFlashcardDeckID) values(?,?,?,?)",(flashcardID,UserID,FlashcardDeckIDs[0][0],parentFlashcardDeckID[0][0],))
            connection.commit()
   
        connection.close()
        #Database is updated with the new flashcards
        flash('Flashcards Imported!', category='success')

        return redirect(url_for('flashcardsSection.flashcards'))

    return render_template("importFlashcards.html",user=current_user, flashcardDecks=flashcardDecks)