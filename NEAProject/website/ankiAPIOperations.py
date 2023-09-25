import json
import urllib.request
from .functions import *
def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']



def checkIfAnkiOpen(): #Sends a random request to the API to see if a response is recieved
    ankiOpen = False
    try:
        deckNames = invoke('deckNames')#If response is recieved then ankiOpen is set to True
        ankiOpen = True
    except:
        ankiOpen = False
    return ankiOpen
        


def returnDecksAvailable(): #This function gets parent decks that are available that the user has from the API

    deckNames = invoke('deckNames')
    filteredDeckNames=[]
    deckNames.remove('Default') #Anki has a deck named 'Default' for all users which needs to be removed

    filtered = False 
    #When response is recieved from the API all parent decks and child decks are returned in the same array
    #The purpose of this loop is to filter out the child deck names and only return the parent deck names

    while filtered == False:
        itemstoRemove = []

        filteredDeckNames.append(deckNames[0])
        deck = deckNames[0]
        for x in deckNames:
            if deck in x:
                itemstoRemove.append(x)

        for x in itemstoRemove:
            deckNames.remove(x)
        if checkIfDecknamesFiltered(deckNames) == True:
            filtered = True
    #If only parent decks remain then loop ends

    return filteredDeckNames



def returnChildDecks(parentDeckName): #This function gets the child decks of the given parent deck
    deckNames = invoke('deckNames')#All deck names are returned
    deckNames.remove('Default')
    childDecks = []

    for x in deckNames:
        if parentDeckName in x:
            childDecks.append(x) #Only child decks of the parent deck given are chosen

    childDecks.remove(parentDeckName) #The parent deck itself is removed from the array

    return childDecks



def returnDeckID(deckNameToImport):
    cards = invoke('deckNamesAndIds')#Requests for all deck names and their ids
    for key,value in cards.items():
        if key == deckNameToImport:
            return value            #Returns the Id of the deck name being searched for



def extractFlashcards(deckNameToImport):

    deckNameToImport = deckNameToImport.replace(' ','_')
    #API cannot handle spaces in deck name so need to replace with underscores

    cards = invoke('findCards', query = f'deck:{deckNameToImport}')
    #Requests for the flashcards that are associated with the deck name specified
    deckID = returnDeckID(deckNameToImport)
    #Returns the deck ID of the deck name given
    cardsInfo = (invoke('cardsInfo', cards = cards))
    #Returns information on flashcards such as card types
    refinedData = []
    for card in cardsInfo:
        if card.get('modelName') != "Image Occlusion Enhanced":
            refinedData.append(card)
    #If flashcard contains images then they are removed
    indexOfCardsToRemove = []
    questions = []
    answers = []

    counter = 0
    for card in refinedData:

        cardID = card.get('cardId')
        deckName = card.get('deckName')
        questionData = card.get('question')
        
        if checkIfNeedToRemoveFlashcard(questionData, 'Question') == True:
            indexOfCardsToRemove.append(counter)

        refinedQuestion = questionData[questionData.find('</style>') + 8:questionData.find('<div')-1]
        #Removes some of the HTML data which is the same for all flashcards that are from Anki
        refinedQuestion = removeHTMLCharacterEntities(refinedQuestion)
        #Removes any HTML character entities present in the flashcard
        refinedQuestion = removeExtraSpaces(removeHTML(refinedQuestion))
        #Removes all HTML to return just the question

        questionCard = (cardID,deckName,refinedQuestion)
        questions.append(questionCard)

        answerData = card.get('answer')
        filteredAnswer = answerData[answerData.find('<hr id=answer'):]

        if checkIfNeedToRemoveFlashcard(filteredAnswer, 'Answer') == True:
            indexOfCardsToRemove.append(counter)

        if checkIfContainsSpanTag(filteredAnswer) == True:
            removeSpanTagStart = filteredAnswer[filteredAnswer.find('<span styl'):]
            #Removes some of the HTML data which is the same for all flashcards that are from Anki
            refinedAnswer = removeSpanTagStart[removeSpanTagStart.find('>') + 1:]
            refinedAnswer = removeHTMLCharacterEntities(refinedAnswer)
            #Removes any HTML character entities present in the flashcard
        else:
            refinedAnswer = filteredAnswer
            refinedAnswer = removeHTMLCharacterEntities(refinedAnswer)
            #Removes any HTML character entities present in the flashcard

        refinedAnswer = removeExtraSpaces(removeHTML(refinedAnswer))
        #Removes all HTML to return just the answer
        answerCard = (cardID,deckName,refinedAnswer)
        answers.append(answerCard)
        counter+=1

    for i in range((len(questions))-1): #Checks if question is blank if so they will be removed
        if questions[i][2] == '':
            indexOfCardsToRemove.append(i)

    for i in range((len(answers))-1): #Checks if answer is blank if so they will be removed
        if answers[i][2] == '':
            indexOfCardsToRemove.append(i)


    indexOfCardsToRemove = list(dict.fromkeys(indexOfCardsToRemove)) # Removes Duplicates

    indexOfCardsToRemove = merge_sort(indexOfCardsToRemove,reverse=True)
    #Sorts all indexes and reverse is true so that when removing items the largest is removed first
    #Reversing list ensures that the index of the item to remove doesn't change


    for index in indexOfCardsToRemove:# Any flahscards that need to be removed are removed
        questions.pop(index)
        answers.pop(index)

    return extractKeywords(questions, answers, deckID)#Keywords are extracted and flashcards are returned
