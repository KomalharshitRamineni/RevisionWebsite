import json
import urllib.request
from .functions import merge_sort,extractKeywords,removeHTMLCharacterEntities,CheckIfDecknamesFiltered,removeExtraSpaces,removeHTML,checkIfNeedToRemoveFlashcard,checkIfContainsSpanTag


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




def checkIfAnkiOpen():
    AnkiOpen = False
    try:
        DeckNames = invoke('deckNames')
        AnkiOpen = True
    except:
        AnkiOpen = False
    return AnkiOpen
        


def returnDecksAvailable():

    DeckNames = invoke('deckNames')
    FilteredDeckNames=[]
    DeckNames.remove('Default')


    filtered = False
    while filtered == False:
        itemstoRemove = []

        FilteredDeckNames.append(DeckNames[0])
        Deck = DeckNames[0]
        for x in DeckNames:
            if Deck in x:
                itemstoRemove.append(x)

        for x in itemstoRemove:
            DeckNames.remove(x)
        if CheckIfDecknamesFiltered(DeckNames) == True:
            filtered = True

    return FilteredDeckNames


def returnChildDecks(ParentDeckName):
    DeckNames = invoke('deckNames')
    DeckNames.remove('Default')
    ChildDecks = []

    for x in DeckNames:
        if ParentDeckName in x:
            ChildDecks.append(x)

    ChildDecks.remove(ParentDeckName)

    return ChildDecks





def returnDeckID(deckNameToImport):
    Cards = invoke('deckNamesAndIds')
    for key,value in Cards.items():
        if key == deckNameToImport:
            return value










def extractFlashcards(deckNameToImport):


    #API cannot handle spaces in deck name so need to replace with underscores
    deckNameToImport = deckNameToImport.replace(' ','_')



    Cards = invoke('findCards', query = f'deck:{deckNameToImport}')
    DeckID = returnDeckID(deckNameToImport)


    CardsInfo = (invoke('cardsInfo', cards = Cards))
    RefinedData = []
    for Card in CardsInfo:
        if Card.get('modelName') != "Image Occlusion Enhanced":
            RefinedData.append(Card)


    indexOfCardsToRemove = []
    Questions = []
    Answers = []

    counter = 0
    for Card in RefinedData:

        
        cardID = Card.get('cardId')
        DeckName = Card.get('deckName')
        QuestionData = Card.get('question')
        
        if checkIfNeedToRemoveFlashcard(QuestionData, 'Question') == True:
            indexOfCardsToRemove.append(counter)

        RefinedQuestion = QuestionData[QuestionData.find('</style>') + 8:QuestionData.find('<div')-1]#Removes extra information about the card
        RefinedQuestion = removeHTMLCharacterEntities(RefinedQuestion)
        RefinedQuestion = removeExtraSpaces(removeHTML(RefinedQuestion))

        QuestionCard = (cardID,DeckName,RefinedQuestion)
        Questions.append(QuestionCard)


        AnswerData = Card.get('answer')
        FilteredAnswer = AnswerData[AnswerData.find('<hr id=answer'):]

        if checkIfNeedToRemoveFlashcard(FilteredAnswer, 'Answer') == True:
            indexOfCardsToRemove.append(counter)


        if checkIfContainsSpanTag(FilteredAnswer) == True:
            RemoveSpanTagStart = FilteredAnswer[FilteredAnswer.find('<span styl'):]
            RefinedAnswer = RemoveSpanTagStart[RemoveSpanTagStart.find('>') + 1:]
            RefinedAnswer = removeHTMLCharacterEntities(RefinedAnswer)
        else:
            RefinedAnswer = FilteredAnswer
            RefinedAnswer = removeHTMLCharacterEntities(RefinedAnswer)


        RefinedAnswer = removeExtraSpaces(removeHTML(RefinedAnswer))
        AnswerCard = (cardID,DeckName,RefinedAnswer)
        Answers.append(AnswerCard)
        counter+=1

        

    for i in range((len(Questions))-1): #Checks if cards are blank
        if Questions[i][2] == '':
            indexOfCardsToRemove.append(i)

    for i in range((len(Answers))-1):
        if Answers[i][2] == '':
            indexOfCardsToRemove.append(i)


    indexOfCardsToRemove = list(dict.fromkeys(indexOfCardsToRemove)) # Removes Duplicates

    indexOfCardsToRemove = merge_sort(indexOfCardsToRemove,reverse=True)

    #indexOfCardsToRemove.sort(reverse=True)        # reverse list so that index doesn't change when looped thruough


    for index in indexOfCardsToRemove:
        Questions.pop(index)
        Answers.pop(index)

    return extractKeywords(Questions, Answers, DeckID)



#Remove draw cards and check if duplicate cards
#combine some funcions use meaningful variable names