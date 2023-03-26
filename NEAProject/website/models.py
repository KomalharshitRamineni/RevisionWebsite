from flask_login import UserMixin
from .functions import generateKeywords,take_second,removePunc,merge_sort_by_index
import random
import sqlite3
class User(UserMixin):
    
    def __init__(self, id, firstname, password, email):
        self._id = id
        self._firstname = firstname
        self._password = password
        self._email = email


    def get_id(self):
        return self._id
    
    def get_firstname(self):
        return self._firstname
    
    def get_password(self):
        return self._password
    
    def get_email(self):
        return self._email


class Flashcard():
    def __init__(self,FlashcardID,Question,Answer,UserID):
        self.FlashcardID = FlashcardID
        self.UserIDBelongsTo = UserID
        self.Question = Question
        self.Answer = Answer
        self.Keywords =  ''
        self.PossibleQuestionTypes = ['MC','FB','QA','SM']
        #self.setPossibleQuestionTypes()

    def setKeywords(self,Keywords):#this is so that if keywords have already been calculated then no need to recalculate
        self.Keywords = Keywords

    def generateKeywords(self):
        Keywords = generateKeywords(self.Question,self.Answer)
        self.setKeywords(Keywords)
        
    def getQuestion(self):
        return self.Question
    def getAnswer(self):
        return self.Answer
    def getKeywords(self):
        return self.Keywords
    def getUserID(self):
        return self.UserIDBelongsTo
    def getFlashcardID(self):
        return self.FlashcardID

    def setPossibleQuestionTypes(self):
        
        string = self.Keywords
        string = string.replace(' ','')
        if string.isnumeric() == True:
            self.PossibleQuestionTypes.remove('MC')
            self.PossibleQuestionTypes.remove('QA')



        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()


        cursor.execute("""  SELECT ParentFlashcardDeck.FlashcardDeckName
                            FROM ParentFlashcardDeck,FlashcardsDecksAndUserIDs,Flashcard
                            WHERE ParentFlashcardDeck.ParentFlashcardDeckID=FlashcardsDecksAndUserIDs.ParentFlashcardDeckID
                            AND FlashcardsDecksAndUserIDs.UserID=?
                            AND Flashcard.FlashcardID=?
                            AND Flashcard.FlashcardID=FlashcardsDecksAndUserIDs.FlashcardID
                            
                            """,(self.UserIDBelongsTo,self.FlashcardID,))
        
        DeckName = cursor.fetchall()
        DeckName = list(dict.fromkeys(DeckName))


        
        cursor.execute("""  SELECT Flashcard.FlashcardID,Flashcard.Keywords
                            FROM Flashcard,FlashcardsDecksAndUserIDs,ParentFlashcardDeck
                            WHERE FlashcardsDecksAndUserIDs.UserID=?
                            AND FlashcardsDecksAndUserIDs.FlashcardID=Flashcard.FlashcardID
                            AND ParentFlashcardDeck.FlashcardDeckName=?
                            AND ParentFlashcardDeck.ParentFlashcardDeckID=FlashcardsDecksAndUserIDs.ParentFlashcardDeckID
        
        """,(self.UserIDBelongsTo,DeckName[0][0],))
        
        FlashcardIDsAndKeywords = cursor.fetchall()


        matchingFlashCards=[]

        for FlashcardIDAndKeywords in FlashcardIDsAndKeywords:
            matchCount=0
            for x in self.Keywords.split():

                if x in FlashcardIDAndKeywords[1]:
                    matchCount=+1
            if FlashcardIDAndKeywords[1] != self.getKeywords():
                matchingFlashCards.append((FlashcardIDAndKeywords,matchCount))



        for x in reversed(range(len(matchingFlashCards))):

            string = matchingFlashCards[x][0][1]
            string = string.replace(' ','')
            if string.isnumeric() == True or matchingFlashCards[x][1] == 0:
                matchingFlashCards.pop(x)

        matchingFlashCards = list(dict.fromkeys(matchingFlashCards))

        #matchingFlashCards.sort(key=take_second)
        matchingFlashCards = merge_sort_by_index(matchingFlashCards,1,False)

        



        if len(matchingFlashCards) <=3:
            
            self.PossibleQuestionTypes.remove('MC')

        matchingFlashCards=[]

        for FlashcardIDAndKeywords in FlashcardIDsAndKeywords:
            matchCount=0
            for x in self.Keywords.split():
                if x in FlashcardIDAndKeywords[1]:
                    matchCount=+1


            if FlashcardIDAndKeywords[1] != self.Keywords:
                matchingFlashCards.append((FlashcardIDAndKeywords,matchCount))

        for x in reversed(range(len(matchingFlashCards))):


            string = matchingFlashCards[x][0][1]
            string = string.replace(' ','')
            if string.isnumeric() == True or matchingFlashCards[x][1] == 0:
                matchingFlashCards.pop(x)

        matchingFlashCards = list(dict.fromkeys(matchingFlashCards))
        matchingFlashCards = merge_sort_by_index(matchingFlashCards,1,False)
        #matchingFlashCards.sort(key=take_second)


        if len(matchingFlashCards) <=1:
            self.PossibleQuestionTypes.remove('QA')


        keywords = []

        for x in matchingFlashCards:
            keywordsArray = x[0][1]
            keywordsArraySplit = keywordsArray.split()

            for i in keywordsArraySplit:
                keywords.append(i)

        keywords = list(dict.fromkeys(keywords))
        if len(keywords) == 0:
            self.PossibleQuestionTypes.remove('SM')


        keywordInAnswer = False
        for x in self.Keywords.split():
            if x in self.Answer.lower():
                keywordInAnswer = True

        if keywordInAnswer == False:

            self.PossibleQuestionTypes.remove('SM')

        keywordInAnswer = False
        for x in keywords:
            if x in self.Answer.lower():
                keywordInAnswer = True

        if keywordInAnswer == False:

            if 'SM' in self.PossibleQuestionTypes:
                self.PossibleQuestionTypes.remove('SM')






    def getPossibleQuestionTypes(self):
        return self.PossibleQuestionTypes



#Check if keywords are numbers - limmited to fill in the blank or spot the mistake
#Otherwise can be any







#question types = fill in the blanks,multiple choice,spot mistake,match question to answer



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


class FlashcardDeck:#composition relationship
    def __init__(self):
        self.FlashcardDeck = Stack()
        self.UsedFlashcards = Stack() 

    def AddToFlashcardDeck(self,flashcard):
        self.FlashcardDeck.push(flashcard)

    def GetFlashcardDeck(self):
        return self.FlashcardDeck

    def AddToUsedFlashcards(self,flashcard):
        self.UsedFlashcards.push(flashcard)

    def GetUsedFlashcards(self):
        return self.UsedFlashcards
    
    def UseFlashcard(self):
        flashcard = self.FlashcardDeck.pop()
        self.AddToUsedFlashcards(flashcard=flashcard)
        return flashcard

    def UndoFlashcardUse(self):
        flashcard = self.UsedFlashcards.pop()
        self.AddToFlashcardDeck(flashcard=flashcard)

    def PeekFlashcardDeck(self):
        return self.FlashcardDeck.peek()
    def PeekUsedFlashcards(self):
        return self.UsedFlashcards.peek()

    def ShuffleDeck(self):
        self.FlashcardDeck.shuffle()


class Quiz():
    def __init__(self,UserID,DeckName,NumberOfQuestions):
        self.QuizID = self.setQuizID()
        self.Questions = Stack()
        self.CompletedQuestions = Stack()
        self.NumberOfQuestions = NumberOfQuestions
        self.DeckName = DeckName
        self.UserID = UserID
        self.createQuiz()
        
    def getQuizID(self):
        return self.QuizID

    def setQuizID(self):
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(QuizID) FROM Quiz")
        NumberOfQuizIDs = cursor.fetchall()#
        NextQuizID = int(NumberOfQuizIDs[0][0]) + 1
        return NextQuizID

    def NextQuestion(self):
        completedQuestion = self.Questions.pop()
        self.CompletedQuestions.push(completedQuestion)
        return completedQuestion
    def PreviewNextQuestion(self):
        return self.Questions.peek()
    def getQuestions(self):
        return self.Questions
    def getCompletedQuestions(self):
        return self.CompletedQuestions
    
    def returnFlashcardIds(self):
        
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("""  SELECT Flashcard.FlashcardID
                            FROM Flashcard,FlashcardsDecksAndUserIDs,ParentFlashcardDeck
                            WHERE FlashcardsDecksAndUserIDs.UserID=?
                            AND FlashcardsDecksAndUserIDs.FlashcardID=Flashcard.FlashcardID
                            AND ParentFlashcardDeck.FlashcardDeckName=?
                            AND ParentFlashcardDeck.ParentFlashcardDeckID=FlashcardsDecksAndUserIDs.ParentFlashcardDeckID
        
        """,(self.UserID,self.DeckName,))


        FlashcardIDs = cursor.fetchall()

        if len(FlashcardIDs) == 0:
            cursor.execute("""  SELECT Flashcard.FlashcardID
                    FROM Flashcard,FlashcardsDecksAndUserIDs,FlashcardDeck
                    WHERE FlashcardsDecksAndUserIDs.UserID=?
                    AND FlashcardsDecksAndUserIDs.FlashcardID=Flashcard.FlashcardID
                    AND FlashcardDeck.FlashcardDeckName=?
                    AND FlashcardDeck.FlashcardDeckID=FlashcardsDecksAndUserIDs.FlashcardDeckID""",(self.UserID,self.DeckName,))#Checks if parent deck
            FlashcardIDs = cursor.fetchall()

        connection.close()
        return FlashcardIDs


    def createQuiz(self):#check if deck is parent or child, for now default to parent

        FlashcardIDs = self.returnFlashcardIds()
        

        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("""  SELECT Question.QuestionID,Question.QuestionType,Question.Question,Question.Answer,Question.CorrectAnswer,Question.FlashcardID
                            FROM QuizQuestions,PastQuiz,Question
                            WHERE PastQuiz.UserID=?
                            AND PastQuiz.QuizID=QuizQuestions.QuizID 
                            AND QuizQuestions.QuestionID=Question.QuestionID
        """,(self.UserID,))
        QuestionsDoneByUser = cursor.fetchall()
        QuestionsDoneByUser = list(dict.fromkeys(QuestionsDoneByUser))





        random.shuffle(FlashcardIDs)
        FlashcardIDs=FlashcardIDs[:int(self.NumberOfQuestions)]
        for FlashcardID in FlashcardIDs:


            cursor.execute("SELECT FlashcardQuestion,FlashcardAnswer,Keywords FROM Flashcard WHERE FlashcardID=?",(FlashcardID[0],))
            QuestionAnswerAndKeywords = cursor.fetchall()

            FlashcardObject = Flashcard(FlashcardID[0],QuestionAnswerAndKeywords[0][0],QuestionAnswerAndKeywords[0][1],self.UserID)
            FlashcardObject.setKeywords(QuestionAnswerAndKeywords[0][2])
            FlashcardObject.setPossibleQuestionTypes()
            QuestionTypes = FlashcardObject.getPossibleQuestionTypes()
            random.shuffle(QuestionTypes)
            QuestionType=QuestionTypes[0]

            
            QuizQuestionObject = QuizQuestion(QuestionType,FlashcardObject,self.DeckName)
            self.Questions.push(QuizQuestionObject)

#check here
            QuestionAlreadyExists = False

            QuestionIdOfDuplicateQuestion = None

            for Question in QuestionsDoneByUser:
                QuestionIDOfQuestion = Question[0]
                QuestionTypeOfQuestion = Question[1]
   
                try:
                    QuestionFromQuestion = eval(Question[2])
                except:
                    QuestionFromQuestion = Question[2]

                try:
                    AnswerFromQuestion = eval(Question[3])
                except:
                    AnswerFromQuestion = Question[3]

                try:
                    CorrectAnswerFromQuestion = eval(Question[4])
                except:
                    CorrectAnswerFromQuestion = Question[4]

                #FlashcardIdOfQuestion = Question[5]

                if QuizQuestionObject.getQuestionType() == QuestionTypeOfQuestion and QuizQuestionObject.getQuestion() == QuestionFromQuestion and QuizQuestionObject.getAnswer() == AnswerFromQuestion and QuizQuestionObject.getCorrectAnswer() == CorrectAnswerFromQuestion:
                    QuestionAlreadyExists = True
                    QuestionIdOfDuplicateQuestion = int(QuestionIDOfQuestion)


            if QuestionAlreadyExists == True:
                cursor.execute("INSERT INTO QuizQuestions(QuizID,QuestionID) values(?,?)",(self.getQuizID(),QuestionIdOfDuplicateQuestion,))
                connection.commit()
                cursor.execute("INSERT INTO PastQuiz(UserID,QuizID) values(?,?)",(self.UserID,self.getQuizID(),))
                connection.commit()

            else:

                cursor.execute("INSERT INTO Question(QuestionID,NumberOfTimesAnswered,NumberOfTimesAnsweredCorrectly,QuestionType,Question,Answer,CorrectAnswer,FlashcardID) values(?,?,?,?,?,?,?,?)",(QuizQuestionObject.getQuestionID(),0,0,QuizQuestionObject.getQuestionType(),str(QuizQuestionObject.getQuestion()),str(QuizQuestionObject.getAnswer()),str(QuizQuestionObject.getCorrectAnswer()),FlashcardObject.getFlashcardID(),))
                connection.commit()
                cursor.execute("INSERT INTO QuizQuestions(QuizID,QuestionID) values(?,?)",(self.getQuizID(),QuizQuestionObject.getQuestionID(),))
                connection.commit()
                cursor.execute("INSERT INTO PastQuiz(UserID,QuizID) values(?,?)",(self.UserID,self.getQuizID(),))
                connection.commit()

        connection.close()#link userID at other side


class QuizQuestion():
    def __init__(self,Type,Flashcard,DeckName):
        self.QuestionID = self.setQuestionID()
        self.type = Type
        self.DeckName = DeckName
        self.Flashcard = Flashcard
        self.questionToDisplay = None
        self.answersToDisplay = None
        self.correctAnswer = None
        self.UserID = self.Flashcard.getUserID()
        self.FlashcardID = self.Flashcard.getFlashcardID()
        self.createQuestion()

    def getQuestionID(self):
        return self.QuestionID
    
    def setQuestionID(self):
        connection = sqlite3.connect("database.db",check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(QuestionID) FROM Question")
        NumberOfQuestions = cursor.fetchall()
        NextQuestionID = int(NumberOfQuestions[0][0]) + 1
        return NextQuestionID


    def getFlashcardIDsAndKeywords(self):


            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()

            cursor.execute("""  SELECT ParentFlashcardDeck.FlashcardDeckName
                                FROM ParentFlashcardDeck,FlashcardsDecksAndUserIDs,FlashcardDeck
                                WHERE FlashcardDeck.FlashcardDeckName =?
                                AND FlashcardsDecksAndUserIDs.UserID=?
                                AND FlashcardsDecksAndUserIDs.FlashcardDeckID = FlashcardDeck.FlashcardDeckID
                                AND ParentFlashcardDeck.ParentFlashcardDeckID=FlashcardsDecksAndUserIDs.ParentFlashcardDeckID

                        """,(self.DeckName,self.UserID,))
            
            ParentFlashcardDeckName = cursor.fetchall()
            ParentFlashcardDeckName = list(dict.fromkeys(ParentFlashcardDeckName))
            
            if len(ParentFlashcardDeckName) == 0:
                DeckName = self.DeckName
            else:
                DeckName = ParentFlashcardDeckName[0][0]

            

            cursor.execute("""  SELECT Flashcard.FlashcardID,Flashcard.Keywords
                                FROM Flashcard,FlashcardsDecksAndUserIDs,ParentFlashcardDeck
                                WHERE FlashcardsDecksAndUserIDs.UserID=?
                                AND FlashcardsDecksAndUserIDs.FlashcardID=Flashcard.FlashcardID
                                AND ParentFlashcardDeck.FlashcardDeckName=?
                                AND ParentFlashcardDeck.ParentFlashcardDeckID=FlashcardsDecksAndUserIDs.ParentFlashcardDeckID
            
            """,(self.UserID,DeckName,))
            
            FlashcardIDsAndKeywords = cursor.fetchall()
            connection.close()
            return FlashcardIDsAndKeywords


#Fix ParentFalshcard Deckname

    def createQuestion(self):

        if self.type == 'MC':

            self.questionToDisplay=self.Flashcard.getQuestion()
            self.correctAnswer=self.Flashcard.getAnswer()


            FlashcardIDsAndKeywords = self.getFlashcardIDsAndKeywords()


            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()

            matchingFlashCards=[]

            for FlashcardIDAndKeywords in FlashcardIDsAndKeywords:
                matchCount=0
                for x in self.Flashcard.getKeywords().split():
                    if x in FlashcardIDAndKeywords[1]:
                        matchCount=+1
                if FlashcardIDAndKeywords[1] != self.Flashcard.getKeywords():
                    matchingFlashCards.append((FlashcardIDAndKeywords,matchCount))

            for x in reversed(range(len(matchingFlashCards))):

                string = matchingFlashCards[x][0][1]
                string = string.replace(' ','')
                if string.isnumeric() == True or matchingFlashCards[x][1] == 0:
                    matchingFlashCards.pop(x)

            matchingFlashCards = list(dict.fromkeys(matchingFlashCards))
            #matchingFlashCards.sort(key=take_second)
            matchingFlashCards = merge_sort_by_index(matchingFlashCards,1,False)
            AnswersToDisplay = [self.correctAnswer]

            for x in range(len(matchingFlashCards)):
                if x<=2:
                    cursor.execute("SELECT FlashcardAnswer FROM Flashcard WHERE FlashcardID=?",(matchingFlashCards[x][0][0],))
                    answer = cursor.fetchall()

                    AnswersToDisplay.append(answer[0][0])

            self.answersToDisplay = AnswersToDisplay
            connection.close()




        if self.type == 'FB':
            self.questionToDisplay=self.Flashcard.getQuestion()

            self.answersToDisplay=self.Flashcard.getAnswer()

            KeywordsArray = self.Flashcard.getKeywords().split()
            randomNum = random.randint(0,2)

            self.correctAnswer=KeywordsArray[randomNum]
            placeholder=''

            for x in self.correctAnswer:
                placeholder = placeholder+'_'


            for x in self.answersToDisplay.split():

                if removePunc(x.lower()) == self.correctAnswer:
                    
                    self.answersToDisplay = self.answersToDisplay.replace(x,placeholder)

            for x in self.questionToDisplay.split():
                if removePunc(x.lower()) == self.correctAnswer:
                    self.questionToDisplay = self.questionToDisplay.replace(x,placeholder)




        if self.type == 'QA':


            FlashcardIDsAndKeywords = self.getFlashcardIDsAndKeywords()


            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()
            matchingFlashCards=[]

            for FlashcardIDAndKeywords in FlashcardIDsAndKeywords:
                matchCount=0
                for x in self.Flashcard.getKeywords().split():
                    if x in FlashcardIDAndKeywords[1]:
                        matchCount=+1
                if FlashcardIDAndKeywords[1] != self.Flashcard.getKeywords():
                    matchingFlashCards.append((FlashcardIDAndKeywords,matchCount))

            for x in reversed(range(len(matchingFlashCards))):


                string = matchingFlashCards[x][0][1]
                string = string.replace(' ','')
                if string.isnumeric() == True or matchingFlashCards[x][1] == 0:
                    matchingFlashCards.pop(x)

            matchingFlashCards = list(dict.fromkeys(matchingFlashCards))
            matchingFlashCards = merge_sort_by_index(matchingFlashCards,1,False)
            #matchingFlashCards.sort(key=take_second)#sort by taking highst matching score
            AnswersToDisplay = [self.Flashcard.getAnswer()]
            QuestionsToDisplay = [self.Flashcard.getQuestion()]
            correctAnswer={}
            correctAnswer.update({self.Flashcard.getQuestion():self.Flashcard.getAnswer()})
            for x in range(len(matchingFlashCards)):
                if x<=1:
                    cursor.execute("SELECT FlashcardQuestion,FlashcardAnswer FROM Flashcard WHERE FlashcardID=?",(matchingFlashCards[x][0][0],))
                    QuestionAndAnswer = cursor.fetchall()

                    AnswersToDisplay.append(QuestionAndAnswer[0][1])
                    QuestionsToDisplay.append(QuestionAndAnswer[0][0])
                    correctAnswer.update({QuestionAndAnswer[0][0]:QuestionAndAnswer[0][1]})

            self.answersToDisplay = AnswersToDisplay
            self.questionToDisplay = QuestionsToDisplay
            random.shuffle(self.answersToDisplay)
            random.shuffle(self.questionToDisplay)
            self.correctAnswer = correctAnswer
        
            connection.close()

        

        if self.type == 'SM':

            self.questionToDisplay=self.Flashcard.getQuestion()
            self.correctAnswer=self.Flashcard.getAnswer()
            self.answersToDisplay=self.Flashcard.getAnswer()
            FlashcardIDsAndKeywords = self.getFlashcardIDsAndKeywords()


            matchingFlashCards=[]

            for FlashcardIDAndKeywords in FlashcardIDsAndKeywords:

                matchCount=0

                for x in self.Flashcard.getKeywords().split():

                    if x in FlashcardIDAndKeywords[1]:
                        matchCount=+1

                if FlashcardIDAndKeywords[1] != self.Flashcard.getKeywords():
                    matchingFlashCards.append((FlashcardIDAndKeywords,matchCount))

            for x in reversed(range(len(matchingFlashCards))):

                string = matchingFlashCards[x][0][1]
                string = string.replace(' ','')
                if string.isnumeric() == True or int(matchingFlashCards[x][1]) == 0:
                    matchingFlashCards.pop(x)

            matchingFlashCards = list(dict.fromkeys(matchingFlashCards))
            matchingFlashCards = merge_sort_by_index(matchingFlashCards,1,False)
            #matchingFlashCards.sort(key=take_second)

            keywords = []

            for x in matchingFlashCards:
                keywordsArray = x[0][1]
                keywordsArraySplit = keywordsArray.split()

                for i in keywordsArraySplit:
                    keywords.append(i)

            keywords = list(dict.fromkeys(keywords))

            randomNum = random.randint(0,(len(keywords)-1))
            incorrectWord = keywords[randomNum]

            KeywordsArray = self.Flashcard.getKeywords().split()
            randomNum = random.randint(0,2)
            randomKeywordFromQuestion = KeywordsArray[randomNum]

            wordToReplace = randomKeywordFromQuestion

            for x in range(len(self.answersToDisplay.split())):
                if self.answersToDisplay.lower().split()[x] == randomKeywordFromQuestion:
                    wordToReplace=self.answersToDisplay.split()[x]

            while wordToReplace == incorrectWord:
                randomNum = random.randint(0,(len(keywords)-1))
                incorrectWord = keywords[randomNum]
                KeywordsArray = self.Flashcard.getKeywords().split()
                randomNum = random.randint(0,2)
                randomKeywordFromQuestion = KeywordsArray[randomNum]
                wordToReplace = randomKeywordFromQuestion

                for x in range(len(self.answersToDisplay.split())):
                    if self.answersToDisplay.lower().split()[x] == randomKeywordFromQuestion:
                        wordToReplace=self.answersToDisplay.split()[x]

            self.answersToDisplay = self.answersToDisplay.replace(wordToReplace,incorrectWord,1)



    def getQuestionType(self):
        return self.type
    def getQuestion(self):
        return self.questionToDisplay
    def getAnswer(self):
        return self.answersToDisplay
    def getCorrectAnswer(self):
        return self.correctAnswer