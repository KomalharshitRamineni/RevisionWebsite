from flask_login import UserMixin
from .AnkiOperations import generateKeywords
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
        self.getPossibleQuestionTypes()

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

    def getPossibleQuestionTypes(self):
        
        string = self.Keywords
        string = string.replace(' ','')
        if string.isnumeric() == True:
            self.PossibleQuestionTypes.remove('MC')
            self.PossibleQuestionTypes.remove('QA')



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
    def __init__(self):
        self.Questions = Stack()
        self.CompletedQuestions = Stack()


        






class QuizQuestion():
    def __init__(self,Type,Flashcard):
        self.type = Type
        self.Flashcard = Flashcard
        self.questionToDisplay = None
        self.answersToDisplay = None
        self.correctAnswer = None
        self.UserID = self.Flashcard.getUserID()
        self.FlashcardID = self.Flashcard.getFlashcardID()


    def createQuestion(self):

        if self.type == 'MC':

            self.questionToDisplay=self.Flashcard.getQuestion()
            self.correctAnswer=self.Flashcard.getAnswer()

            connection = sqlite3.connect("database.db",check_same_thread=False)
            cursor = connection.cursor()#get all flashcards, owned by user then filter down to flashcards with matching keywords

            cursor.execute("""  SELECT Flashcard.FlashcardID,Flashcard.Keywords
                                FROM Flashcard,FlashcardsDecksAndUserIDs
                                WHERE FlashcardsDecksAndUserIDs.UserID=?
                                AND FlashcardsDecksAndUserIDs.FlashcardID=Flashcard.FlashcardID
            
            """,(self.UserID,))
            
            matchingFlashCards=[]

            FlashcardIDsAndKeywords = cursor.fetchall()
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
            matchingFlashCards.sort()#sort by taking highst matching score
            AnswersToDisplay = [self.correctAnswer]#randomise this array
            #IdsOfMatchingFlashcards = []
            for x in range(len(matchingFlashCards)):
                if x<=2:
                    cursor.execute("SELECT FlashcardAnswer FROM Flashcard WHERE FlashcardID=?",(matchingFlashCards[x][0][0],))
                    answer = cursor.fetchall()

                    AnswersToDisplay.append(answer[0][0])
                    #IdsOfMatchingFlashcards.append(matchingFlashCards[x][0][0])

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

            self.answersToDisplay = self.answersToDisplay.replace(self.correctAnswer,placeholder)

        if self.type == 'QA':
            #return 2 more flashcards with similar keywords and create

            #in questionsToDisplay store an array of questions, same with answers to display
            #in correct answer store dictionary with key as question and value as answer
            pass

        if self.type == 'SM':#spot the mistake
            pass

    def getQuestionType(self):
        return self.type

    def getQuestion(self):
        return self.questionToDisplay
    def getAnswer(self):
        return self.answersToDisplay