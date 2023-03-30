from flask_login import UserMixin
from .functions import generateKeywords,removePunc,merge_sort_by_index
import random
import sqlite3
class User(UserMixin):
    
    def __init__(self, id, firstname, password, email):
        self.__id = id
        self.__firstname = firstname
        self.__password = password
        self.__email = email

    def get_id(self):
        return self.__id
    
    def get_firstname(self):
        return self.__firstname
    
    def get_password(self):
        return self.__password
    
    def get_email(self):
        return self.__email


class Flashcard():
    def __init__(self,flashcardID,question,answer,userID):
        self.___flashcardID = flashcardID
        self.__userIDBelongsTo = userID
        self.__question = question
        self.__answer = answer
        self.__keywords =  ''
        self.__possibleQuestionTypes = ['MC','FB','QA','SM']
        #Question type : MC - Multiple choice
        #Question type : FB - Fill in the blanks
        #Question type : QA - Match question to answer
        #Question type : SM - Spot the mistake
        

    def __setKeywords(self,Keywords):
        self.__keywords = Keywords
        #If flashcard already has keywords then it can be used by passing them in as a parameter

    def __generateKeywords(self):
        #If flashcard does not have any keywords existing the they can be generated
        Keywords = generateKeywords(self.__question,self.__answer)
        self.__setKeywords(Keywords)
        
    def getQuestion(self):
        return self.__question
    def getAnswer(self):
        return self.__answer
    def getKeywords(self):
        return self.__keywords
    def getUserID(self):
        return self.__userIDBelongsTo
    def getFlashcardID(self):
        return self.___flashcardID

    def __setPossibleQuestionTypes(self):
        #The different types of questions are restriced by number of flashcards which are similar to the current one
        
        string = self.__keywords
        string = string.replace(' ','')
        if string.isnumeric() == True:
            #If the keywords are numbers not keywords then Question type MC and QA are not possible
            self.__possibleQuestionTypes.remove('MC')
            self.__possibleQuestionTypes.remove('QA')

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("""  SELECT ParentFlashcardDeck.FlashcardDeckName
                            FROM ParentFlashcardDeck,FlashcardsDecksAndUserIDs,Flashcard
                            WHERE ParentFlashcardDeck.ParentFlashcardDeckID=FlashcardsDecksAndUserIDs.ParentFlashcardDeckID
                            AND FlashcardsDecksAndUserIDs.UserID=?
                            AND Flashcard.FlashcardID=?
                            AND Flashcard.FlashcardID=FlashcardsDecksAndUserIDs.FlashcardID
                            
                            """,(self.__userIDBelongsTo,self.___flashcardID,))
        #Query returns the name of the deck to which the flashcards belong to
        deckName = cursor.fetchall()
        deckName = list(dict.fromkeys(deckName))
        #Duplicate values from query are removed

        cursor.execute("""
    
                            SELECT Flashcard.FlashcardID,Flashcard.Keywords
                            FROM Flashcard
                            JOIN FlashcardsDecksAndUserIDs ON FlashcardsDecksAndUserIDs.FlashcardID = Flashcard.FlashcardID
                            JOIN ParentFlashcardDeck ON ParentFlashcardDeck.ParentFlashcardDeckID = FlashcardsDecksAndUserIDs.ParentFlashcardDeckID
                            WHERE FlashcardsDecksAndUserIDs.UserID = ?
                            AND ParentFlashcardDeck.FlashcardDeckName = ?

        """,(self.__userIDBelongsTo,deckName[0][0]))
        #Query returns the flashcardIDs and the keywords from the deck specifid

        flashcardIDsAndKeywords = cursor.fetchall()
        matchingFlashCards=[]

        for flashcardIDAndKeywords in flashcardIDsAndKeywords:
            matchCount=0
            for x in self.__keywords.split():

                if x in flashcardIDAndKeywords[1]:
                    matchCount=+1
            if flashcardIDAndKeywords[1] != self.getKeywords():
                matchingFlashCards.append((flashcardIDAndKeywords,matchCount))
        #Matching flashcards are identifed by looking if the contain the same keywords
        #The match count represents the number of keywords that match between the two flashcards


        for x in reversed(range(len(matchingFlashCards))):

            string = matchingFlashCards[x][0][1]
            string = string.replace(' ','')
            if string.isnumeric() == True or matchingFlashCards[x][1] == 0:
                matchingFlashCards.pop(x)
        #If the match count of a flashcard is 0 then the flashcard is removed from the array
        #If a flashcard contains numbers then the flashcard is removed from the array

        matchingFlashCards = list(dict.fromkeys(matchingFlashCards))
        #Any duplicate values are removed
        matchingFlashCards = merge_sort_by_index(matchingFlashCards,1,True)
        #The flashcards are sorted by their match count giving higher priority to flashcards which have a higher match count

        if len(matchingFlashCards) <=3:
            #If there are less than 3 matching flashcards the MC question type is removed from the possible question types
            self.__possibleQuestionTypes.remove('MC')

        # matchingFlashCards=[]

        # for flashcardIDAndKeywords in flashcardIDsAndKeywords:
        #     matchCount=0
        #     for x in self.__keywords.split():
        #         if x in flashcardIDAndKeywords[1]:
        #             matchCount=+1

        #     if flashcardIDAndKeywords[1] != self.__keywords:
        #         matchingFlashCards.append((flashcardIDAndKeywords,matchCount))

        # for x in reversed(range(len(matchingFlashCards))):


        #     string = matchingFlashCards[x][0][1]
        #     string = string.replace(' ','')
        #     if string.isnumeric() == True or matchingFlashCards[x][1] == 0:
        #         matchingFlashCards.pop(x)

        # matchingFlashCards = list(dict.fromkeys(matchingFlashCards))
        # matchingFlashCards = merge_sort_by_index(matchingFlashCards,1,False)

        if len(matchingFlashCards) <=1:
            #If there are less than 2 matching flashcards then the questiont type QA is removed from the question types
            self.__possibleQuestionTypes.remove('QA')

        keywords = []

        for x in matchingFlashCards:
            keywordsArray = x[0][1]
            keywordsArraySplit = keywordsArray.split()

            for i in keywordsArraySplit:
                keywords.append(i)

        #Gets all the keywords from the flashcards which are similar to the current one and adds to keywords array

        keywords = list(dict.fromkeys(keywords))
        #Duplicate keywords are removed
        if len(keywords) == 0:
            #If there are no keywords then the question type SM is removed
            self.__possibleQuestionTypes.remove('SM')

        keywordInAnswer = False
        for x in self.__keywords.split():
            if x in self.__answer.lower():
                keywordInAnswer = True

        if keywordInAnswer == False:
            #If the keyword from the current flashcard is not in the answer then the question type SM is removed
            self.__possibleQuestionTypes.remove('SM')

        keywordInAnswer = False
        for x in keywords:
            if x in self.__answer.lower():
                keywordInAnswer = True

        if keywordInAnswer == False:
            #If the keyword from the matching flashcard is not in the answer then the question type SM is removed
            if 'SM' in self.__possibleQuestionTypes :#Checks to see if the question type has been removed already
                self.__possibleQuestionTypes.remove('SM')

    def getPossibleQuestionTypes(self):
        return self.__possibleQuestionTypes



class Stack:
     def __init__(self):
         self.items = []

     def isEmpty(self):
         return self.items == []

     def push(self, item):
         self.items.append(item)

     def pop(self):
         return self.items.pop()

     def peek(self):
         return self.items[len(self.items)-1]

     def size(self):
         return len(self.items)
     
     def shuffle(self):
        if self.size() > 1:
         random.shuffle(self.items)


class FlashcardDeck:
    def __init__(self):
        self.__flashcardDeck = Stack() #Composition relationship
        self.__usedFlashcards = Stack() 

    def __addToFlashcardDeck(self,flashcard):
        self.__flashcardDeck.push(flashcard)

    def __getFlashcardDeck(self):
        return self.__flashcardDeck

    def __addToUsedFlashcards(self,flashcard):
        self.__usedFlashcards.push(flashcard)

    def __getUsedFlashcards(self):
        return self.__usedFlashcards
    
    def __useFlashcard(self):#This function gets the next flashcard and moves it to the used flashcards stack
        flashcard = self.__flashcardDeck.pop()
        self.__addToUsedFlashcards(flashcard=flashcard)
        return flashcard

    def __undoFlashcardUse(self):#this function removes the flashcard from the used stack and pushes it onto flashcards stack
        flashcard = self.__usedFlashcards.pop()
        self.__addToFlashcardDeck(flashcard=flashcard)

    def __peekFlashcardDeck(self):
        return self.__flashcardDeck.peek()#Returns top item in flashcard stack
    def __peekUsedFlashcards(self):
        return self.__usedFlashcards.peek()#Returns top item in used flashcards stack

    def __shuffleDeck(self):
        self.__flashcardDeck.shuffle()#items in stack are shuffled randomly



class Quiz():
    def __init__(self,UserID,deckName,numberOfQuestions):
        self.__quizID = self.__setQuizID()
        self.__questions = Stack()#Composition relationship
        self.__completedQuestions = Stack()
        self.__numberOfQuestions = numberOfQuestions
        self.__deckName = deckName
        self.__userID = UserID
        self.__createQuiz()
        
    def __getQuizID(self):
        return self.__quizID

    def __setQuizID(self):
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(QuizID) FROM Quiz")
        #The quiz id is a primary key and is auto incremented
        #The quiz items are also not deleted
        #The next quiz id can be found by looking at the number of quizzes
        numberOfQuizIDs = cursor.fetchall()
        nextQuizID = int(numberOfQuizIDs[0][0]) + 1
        return nextQuizID

    def __nextQuestion(self):
        completedQuestion = self.__questions.pop()
        self.__completedQuestions.push(completedQuestion)
        #Next question is removed from questions stack and pushed onto completed questions stack
        return completedQuestion
    def __previewNextQuestion(self):
        return self.__questions.peek()
    def __getQuestions(self):
        return self.__questions
    def __getCompletedQuestions(self):
        return self.__completedQuestions
    
    def __returnFlashcardIds(self):
        
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("""SELECT Flashcard.FlashcardID
                        FROM Flashcard
                        JOIN FlashcardsDecksAndUserIDs ON FlashcardsDecksAndUserIDs.FlashcardID = Flashcard.FlashcardID
                        JOIN ParentFlashcardDeck ON ParentFlashcardDeck.ParentFlashcardDeckID = FlashcardsDecksAndUserIDs.ParentFlashcardDeckID
                        WHERE FlashcardsDecksAndUserIDs.UserID = ? AND ParentFlashcardDeck.FlashcardDeckName = ?
                    """, (self.__userID, self.__deckName,))

        flashcardIDs = cursor.fetchall()
        #Query returns the name of the deck to which the flashcards belong to
        if len(flashcardIDs) == 0:

            cursor.execute("""
                SELECT Flashcard.FlashcardID
                FROM Flashcard
                JOIN FlashcardsDecksAndUserIDs ON FlashcardsDecksAndUserIDs.FlashcardID = Flashcard.FlashcardID
                JOIN FlashcardDeck ON FlashcardDeck.FlashcardDeckID = FlashcardsDecksAndUserIDs.FlashcardDeckID
                WHERE FlashcardsDecksAndUserIDs.UserID = ?
                AND FlashcardDeck.FlashcardDeckName = ?
            """, (self.__userID, self.__deckName,))
            #Query returns the flashcardIDs and the keywords from the deck specified
            flashcardIDs = cursor.fetchall()

        connection.close()
        return flashcardIDs


    def __createQuiz(self):

        flashcardIDs = self.__returnFlashcardIds()
        
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("""  SELECT Question.QuestionID, Question.QuestionType, Question.Question, Question.Answer,Question.CorrectAnswer, Question.FlashcardID
                            FROM PastQuiz
                            JOIN QuizQuestions ON PastQuiz.QuizID = QuizQuestions.QuizID 
                            JOIN Question ON QuizQuestions.QuestionID = Question.QuestionID
                            WHERE PastQuiz.UserID = ?
                """,(self.__userID,))

        questionsDoneByUser = cursor.fetchall()
        questionsDoneByUser = list(dict.fromkeys(questionsDoneByUser))

        #Questions completed by the user are queried

        random.shuffle(flashcardIDs)#The flashcardIds are randomised as the quiz is randomly generated
        flashcardIDs=flashcardIDs[:int(self.__numberOfQuestions)]
        for flashcardID in flashcardIDs:

            cursor.execute("SELECT FlashcardQuestion,FlashcardAnswer,Keywords FROM Flashcard WHERE FlashcardID=?",(flashcardID[0],))
            questionAnswerAndKeywords = cursor.fetchall()
            #Query returs the details of a flashcard given the flashcardID

            flashcardObject = Flashcard(flashcardID[0],questionAnswerAndKeywords[0][0],questionAnswerAndKeywords[0][1],self.__userID)
            flashcardObject.__setKeywords(questionAnswerAndKeywords[0][2])
            #flashcard object is created and the keywords are set
            flashcardObject.__setPossibleQuestionTypes()
            #The possible question types for the flashcard are calculated
            questionTypes = flashcardObject.getPossibleQuestionTypes()
            #The possible question types are retuned
            random.shuffle(questionTypes)
            #The question types are randomised as the type of question should be random
            questionType=questionTypes[0]

            quizQuestionObject = QuizQuestion(questionType,flashcardObject,self.__deckName)
            self.__questions.push(quizQuestionObject)
            #Stack is updated with the question object created

            questionAlreadyExists = False
            questionIdOfDuplicateQuestion = None

            for question in questionsDoneByUser:
                questionIDOfQuestion = question[0]
                questionTypeOfQuestion = question[1]
                #when questions are stored in the database they are turned into strings before storing
                #Therefore array or a dictionary that is in a string needs to be converted back into an array or dictionary
                try:
                    questionFromQuestion = eval(question[2])
                except:
                    questionFromQuestion = question[2]

                try:
                    answerFromQuestion = eval(question[3])
                except:
                    answerFromQuestion = question[3]

                try:
                    correctAnswerFromQuestion = eval(question[4])
                except:
                    correctAnswerFromQuestion = question[4]

                if quizQuestionObject.getQuestionType() == questionTypeOfQuestion and quizQuestionObject.getQuestion() == questionFromQuestion and quizQuestionObject.getAnswer() == answerFromQuestion and quizQuestionObject.getCorrectAnswer() == correctAnswerFromQuestion:
                    questionAlreadyExists = True
                    questionIdOfDuplicateQuestion = int(questionIDOfQuestion)
                    #If the question that has been generated already exists in the database then the one stored in the database needs to be used instead

            if questionAlreadyExists == True:
                cursor.execute("INSERT INTO QuizQuestions(QuizID,QuestionID) values(?,?)",(self.__getQuizID(),questionIdOfDuplicateQuestion,))
                connection.commit()
                cursor.execute("INSERT INTO PastQuiz(UserID,QuizID) values(?,?)",(self.__userID,self.__getQuizID(),))
                connection.commit()
                #If question already exists in the database then the Question table is not updated
            else:
                #If the question created is new however, the Question table is updated
                cursor.execute("INSERT INTO Question(QuestionID,NumberOfTimesAnswered,NumberOfTimesAnsweredCorrectly,QuestionType,Question,Answer,CorrectAnswer,FlashcardID) values(?,?,?,?,?,?,?,?)",(quizQuestionObject.getQuestionID(),0,0,quizQuestionObject.getQuestionType(),str(quizQuestionObject.getQuestion()),str(quizQuestionObject.getAnswer()),str(quizQuestionObject.getCorrectAnswer()),flashcardObject.getFlashcardID(),))
                connection.commit()
                cursor.execute("INSERT INTO QuizQuestions(QuizID,QuestionID) values(?,?)",(self.__getQuizID(),quizQuestionObject.getQuestionID(),))
                connection.commit()
                cursor.execute("INSERT INTO PastQuiz(UserID,QuizID) values(?,?)",(self.__userID,self.__getQuizID(),))
                connection.commit()

        connection.close()



class QuizQuestion():
    def __init__(self,Type,Flashcard,deckName):
        self.__questionID = self.__setQuestionID()
        self.__type = Type
        self.__deckName = deckName
        self.__flashcard = Flashcard
        self.__questionToDisplay = None
        self.__answersToDisplay = None
        self.__correctAnswer = None
        self.__userID = self.__flashcard.getUserID()
        self.___flashcardID = self.__flashcard.getFlashcardID()
        self.__createQuestion()

    def getQuestionID(self):
        return self.__questionID
    
    def __setQuestionID(self):
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(QuestionID) FROM Question")
        numberOfQuestions = cursor.fetchall()
        nextQuestionID = int(numberOfQuestions[0][0]) + 1
        #The QuestionID id is a primary key and is auto incremented
        #The QuestionS items are also not deleted
        #The next QuestionID id can be found by looking at the number of quizzes
        return nextQuestionID
    

    def getFlashcardIDsAndKeywords(self):

            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()

            cursor.execute("""SELECT ParentFlashcardDeck.FlashcardDeckName
                            FROM FlashcardDeck
                            JOIN FlashcardsDecksAndUserIDs ON FlashcardsDecksAndUserIDs.FlashcardDeckID = FlashcardDeck.FlashcardDeckID
                            JOIN ParentFlashcardDeck ON ParentFlashcardDeck.ParentFlashcardDeckID = FlashcardsDecksAndUserIDs.ParentFlashcardDeckID
                            WHERE FlashcardDeck.FlashcardDeckName = ?
                            AND FlashcardsDecksAndUserIDs.UserID = ?""",
                        (self.__deckName, self.__userID,))
            #Query returns the name of the deck to which the flashcards belong to
            parentFlashcardDeckName = cursor.fetchall()
            parentFlashcardDeckName = list(dict.fromkeys(parentFlashcardDeckName))
            
            if len(parentFlashcardDeckName) == 0:
                deckName = self.__deckName
            else:
                deckName = parentFlashcardDeckName[0][0]

            cursor.execute("""  SELECT Flashcard.FlashcardID,Flashcard.Keywords
                                FROM Flashcard,FlashcardsDecksAndUserIDs,ParentFlashcardDeck
                                WHERE FlashcardsDecksAndUserIDs.UserID=?
                                AND FlashcardsDecksAndUserIDs.FlashcardID=Flashcard.FlashcardID
                                AND ParentFlashcardDeck.FlashcardDeckName=?
                                AND ParentFlashcardDeck.ParentFlashcardDeckID=FlashcardsDecksAndUserIDs.ParentFlashcardDeckID
            
            """,(self.__userID,deckName,))
            #Query returns the flashcardIDs and the keywords from the deck specified
            flashcardIDsAndKeywords = cursor.fetchall()
            connection.close()
            return flashcardIDsAndKeywords


    def __createQuestion(self):

        if self.__type == 'MC':

            self.__questionToDisplay=self.__flashcard.getQuestion()
            self.__correctAnswer=self.__flashcard.getAnswer()

            flashcardIDsAndKeywords = self.getFlashcardIDsAndKeywords()

            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()

            matchingFlashCards=[]

            for flashcardIDAndKeywords in flashcardIDsAndKeywords:
                matchCount=0
                for x in self.__flashcard.getKeywords().split():
                    if x in flashcardIDAndKeywords[1]:
                        matchCount=+1
                if flashcardIDAndKeywords[1] != self.__flashcard.getKeywords():
                    matchingFlashCards.append((flashcardIDAndKeywords,matchCount))

            #Matching flashcards are identifed by looking if the contain the same keywords
            #The match count represents the number of keywords that match between the two flashcards


            for x in reversed(range(len(matchingFlashCards))):

                string = matchingFlashCards[x][0][1]
                string = string.replace(' ','')
                if string.isnumeric() == True or matchingFlashCards[x][1] == 0:
                    matchingFlashCards.pop(x)
            #If the match count of a flashcard is 0 then the flashcard is removed from the array

            matchingFlashCards = list(dict.fromkeys(matchingFlashCards))
            matchingFlashCards = merge_sort_by_index(matchingFlashCards,1,True)
            #The flashcards are sorted by their match count giving higher priority to flashcards which have a higher match count
            answersToDisplay = [self.__correctAnswer]

            for x in range(len(matchingFlashCards)):
                if x<=2:
                    cursor.execute("SELECT FlashcardAnswer FROM Flashcard WHERE FlashcardID=?",(matchingFlashCards[x][0][0],))
                    answer = cursor.fetchall()
                    #The answer to the matching flashcard is queried with the corresponding Flashcard ID and added to the list
                    answersToDisplay.append(answer[0][0])

            self.__answersToDisplay = answersToDisplay
            connection.close()


        if self.__type == 'FB':
            self.__questionToDisplay=self.__flashcard.getQuestion()

            self.__answersToDisplay=self.__flashcard.getAnswer()

            keywordsArray = self.__flashcard.getKeywords().split()
            randomNum = random.randint(0,2)

            self.__correctAnswer=keywordsArray[randomNum]
            placeholder=''

            for x in self.__correctAnswer:
                placeholder = placeholder+'_'

            for x in self.__answersToDisplay.split():

                if removePunc(x.lower()) == self.__correctAnswer:
                    self.__answersToDisplay = self.__answersToDisplay.replace(x,placeholder)
                #If the word to fill in the blank with is in the question then it is replaced with a place holder

            for x in self.__questionToDisplay.split():
                if removePunc(x.lower()) == self.__correctAnswer:
                    self.__questionToDisplay = self.__questionToDisplay.replace(x,placeholder)
                #If the word to fill in the blank with is in the answer then it is replaced with a place holder


        if self.__type == 'QA':

            flashcardIDsAndKeywords = self.getFlashcardIDsAndKeywords()

            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()
            matchingFlashCards=[]

            for flashcardIDAndKeywords in flashcardIDsAndKeywords:
                matchCount=0
                for x in self.__flashcard.getKeywords().split():
                    if x in flashcardIDAndKeywords[1]:
                        matchCount=+1
                if flashcardIDAndKeywords[1] != self.__flashcard.getKeywords():
                    matchingFlashCards.append((flashcardIDAndKeywords,matchCount))

                #Matching flashcards are identifed by looking if the contain the same keywords
                #The match count represents the number of keywords that match between the two flashcards

        
            for x in reversed(range(len(matchingFlashCards))):

                string = matchingFlashCards[x][0][1]
                string = string.replace(' ','')
                if string.isnumeric() == True or matchingFlashCards[x][1] == 0:
                    matchingFlashCards.pop(x)
                #If the match count of a flashcard is 0 then the flashcard is removed from the array

            matchingFlashCards = list(dict.fromkeys(matchingFlashCards))
            matchingFlashCards = merge_sort_by_index(matchingFlashCards,1,True)
            #The flashcards are sorted by their match count giving higher priority to flashcards which have a higher match count
            answersToDisplay = [self.__flashcard.getAnswer()]
            questionsToDisplay = [self.__flashcard.getQuestion()]
            correctAnswer={}
            correctAnswer.update({self.__flashcard.getQuestion():self.__flashcard.getAnswer()})
            #The question and answer from the current flashcard are added to the correct answer dictionary

            for x in range(len(matchingFlashCards)):
                if x<=1:#Only takes 2 more matching flashcards
                    cursor.execute("SELECT FlashcardQuestion,FlashcardAnswer FROM Flashcard WHERE FlashcardID=?",(matchingFlashCards[x][0][0],))
                    questionAndAnswer = cursor.fetchall()
                    #The question and answer from the matching flashcard is queried
                    answersToDisplay.append(questionAndAnswer[0][1])
                    questionsToDisplay.append(questionAndAnswer[0][0])
                    correctAnswer.update({questionAndAnswer[0][0]:questionAndAnswer[0][1]})
                    #correct answer dictionary updated with another question and answer
            self.__answersToDisplay = answersToDisplay
            self.__questionToDisplay = questionsToDisplay
            random.shuffle(self.__answersToDisplay)#questions and answers shuffled so they are random
            random.shuffle(self.__questionToDisplay)
            self.__correctAnswer = correctAnswer
        
            connection.close()


        if self.__type == 'SM':

            self.__questionToDisplay=self.__flashcard.getQuestion()
            self.__correctAnswer=self.__flashcard.getAnswer()
            self.__answersToDisplay=self.__flashcard.getAnswer()
            flashcardIDsAndKeywords = self.getFlashcardIDsAndKeywords()

            matchingFlashCards=[]

            for flashcardIDAndKeywords in flashcardIDsAndKeywords:
                matchCount=0
                for x in self.__flashcard.getKeywords().split():

                    if x in flashcardIDAndKeywords[1]:
                        matchCount=+1

                if flashcardIDAndKeywords[1] != self.__flashcard.getKeywords():
                    matchingFlashCards.append((flashcardIDAndKeywords,matchCount))

                    #Matching flashcards are identifed by looking if the contain the same keywords
                    #The match count represents the number of keywords that match between the two flashcards

            for x in reversed(range(len(matchingFlashCards))):

                string = matchingFlashCards[x][0][1]
                string = string.replace(' ','')
                if string.isnumeric() == True or int(matchingFlashCards[x][1]) == 0:
                    matchingFlashCards.pop(x)
                #If the match count of a flashcard is 0 then the flashcard is removed from the array
            matchingFlashCards = list(dict.fromkeys(matchingFlashCards))
            matchingFlashCards = merge_sort_by_index(matchingFlashCards,1,True)
            #The flashcards are sorted by their match count giving higher priority to flashcards which have a higher match count

            keywords = []

            for x in matchingFlashCards:
                keywordsArray = x[0][1]
                keywordsArraySplit = keywordsArray.split()

                for i in keywordsArraySplit:
                    keywords.append(i)

            #Gets all the keywords from the flashcards which are similar to the current one and adds to keywords array
            keywords = list(dict.fromkeys(keywords))
            #Duplicate keywords are removed
            randomNum = random.randint(0,(len(keywords)-1))
            incorrectWord = keywords[randomNum]
            #A random keyword is chosen to be the mistake
            keywordsArray = self.__flashcard.getKeywords().split()
            randomNum = random.randint(0,2)
            randomKeywordFromQuestion = keywordsArray[randomNum]

            wordToReplace = randomKeywordFromQuestion
            #A random keyword from the question is chosen to be replaced with the mistake

            for x in range(len(self.__answersToDisplay.split())):
                if self.__answersToDisplay.lower().split()[x] == randomKeywordFromQuestion:
                    wordToReplace=self.__answersToDisplay.split()[x]

            while wordToReplace == incorrectWord:
                #In the case that the random words chosen are the same then it needs to repeat until different words are chosen

                randomNum = random.randint(0,(len(keywords)-1))
                incorrectWord = keywords[randomNum]
                keywordsArray = self.__flashcard.getKeywords().split()
                randomNum = random.randint(0,2)
                randomKeywordFromQuestion = keywordsArray[randomNum]
                wordToReplace = randomKeywordFromQuestion

                for x in range(len(self.__answersToDisplay.split())):
                    if self.__answersToDisplay.lower().split()[x] == randomKeywordFromQuestion:
                        wordToReplace=self.__answersToDisplay.split()[x]


            self.__answersToDisplay = self.__answersToDisplay.replace(wordToReplace,incorrectWord,1)
            #The question that is being displayed is altered so there is a mistake

    def getQuestionType(self):
        return self.__type
    def getQuestion(self):
        return self.__questionToDisplay
    def getAnswer(self):
        return self.__answersToDisplay
    def getCorrectAnswer(self):
        return self.__correctAnswer