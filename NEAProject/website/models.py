from flask_login import UserMixin
from .AnkiOperations import generateKeywords
import random
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
    def __init__(self,Question,Answer):
        self.Question = Question
        self.Answer = Answer
        self.Keywords =  ''

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