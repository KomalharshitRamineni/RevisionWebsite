import json
import urllib.request
import numpy as np



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


def removePunc(string):
    symbols = "!\"#$%&()*+-./:;<=>?@[\]^_`{|}~,"
    for x in string:
        for y in symbols:
            if x == y:
                string = string.replace(x,'')
    

    return string



def checkIfAnkiOpen():
    AnkiOpen = False
    try:
        DeckNames = invoke('deckNames')
        AnkiOpen = True
    except:
        AnkiOpen = False
    return AnkiOpen
        


def removeHTMLCharacterEntities(string):
    HTMLCharacterEntities ={
        '&nbsp;': ' ',
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        '&quot;': '"',
        '&apos;': "'",
        '&cent;': "¢",
        '&pound;': '£',
        '&yen;': '¥',
        '&euro;': '€'

    }   

    for CharacterEntity, Value in HTMLCharacterEntities.items():
        if CharacterEntity in string:
            string = string.replace(CharacterEntity,Value)
            
    return string




def checkIfNeedToRemoveFlashcard(string, QuestionType):
    #create an array of items to remove
    
    removeFlashcard = False
    ItemsToCheckFor = ['<img','Draw','<table']

    for item in ItemsToCheckFor:
        if item == 'Draw' and QuestionType =='Question' and item in string:
            removeFlashcard = True
        else:
            if item != 'Draw' and item in string:
                removeFlashcard = True
    return removeFlashcard



def checkIfContainsSpanTag(string):
    ContainsSpanTag = False
    SpanTag = '<span'
    if SpanTag in string:
        ContainsSpanTag = True
    return ContainsSpanTag


def removeExtraSpaces(string):
    splitString = string.split() #Python has an inbuilt split funtion which removes all spaces
    removedSpace = ''
    for x in splitString:
        if removedSpace == '':
            removedSpace = removedSpace + x
        else:
            removedSpace = removedSpace + ' ' + x
    return removedSpace




def removeHTML(string):
    tagOpen = False
    count = 0
    removed = False
    while removed == False:
        if count <= len(string)-1:

            if string[count] == '<':
                tagOpen = True
                startTag = count

            if tagOpen == True and string[count] == '>':
                endTag = count+1
                htmlTag = string[startTag:endTag]
                string = string.replace(htmlTag,' ')
                tagOpen = False
                count = 0
        else:
            removed = True

        count = count + 1

    return string

#inital code design however if string happens to contian both < and > then it will consider it a tag and remove it so cannot be used 

def processCard(string):

    string = string.lower()

    stopwords = ['describe','explain','define','eg','g','b','e','i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
    symbols = "!\"#$%&()*+-./:;<=>?@[\]^_`{|}~,"

    stopwordsRemoved = ""
    
    for word in string.split():
        if word not in stopwords:
            stopwordsRemoved = stopwordsRemoved + " " + word

    for symbol in symbols:
        for word in stopwordsRemoved:
            if word == symbol:
                stopwordsRemoved = stopwordsRemoved.replace(word,' ')
    
    symbolsRemoved = ""
    
    for x in stopwordsRemoved.split():
        if x not in stopwords:
            symbolsRemoved = symbolsRemoved + " " + x

    return symbolsRemoved



def take_second(elem):
    return elem[1]


def CheckIfDecknamesFiltered(DeckNames):
    filterd = True
    for x in range(len(DeckNames)-1):
        if DeckNames[x] in DeckNames[x+1]:
            filterd = False
    return filterd




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



def extractKeywords(Questions,Answers, DeckID):
    ExtractedData = []
    for x in range(len(Questions)-1):

        keywords = generateKeywords(Questions[x][2],Answers[x][2])

        CardData = {
        
        "cardID": int(Questions[x][0]),
        "deckID": DeckID,
        "deckName":Questions[x][1],
        "question": Questions[x][2],
        "answer": Answers[x][2],
        "keywords": keywords
        

        }
        ExtractedData.append(CardData)

    return ExtractedData


def generateKeywords(Question, Answer):


    ProcessedAnswerCard = processCard(Answer).split()
    ProcesesedQuestionCard = processCard(Question).split()


    DF = {}
    tokens = ProcessedAnswerCard

    for w in tokens:
        DF.update({w:tokens.count(w)})

    tokens = ProcesesedQuestionCard
    for w in tokens:
        DF.update({w:tokens.count(w)})

    ProcessedAnswerCard = Answer.split()     
    ProcesesedQuestionCard = Question.split()

    KeywordsForCard = []

    for i in DF:
        TFA = ProcessedAnswerCard.count(i) / len(ProcessedAnswerCard)
        TFQ = ProcesesedQuestionCard.count(i)/ len(ProcesesedQuestionCard)
        TF = (TFA + TFQ)

        IDF = np.log(DF.get(i)/2)

        tupleofcard = (i,TF*IDF)
        KeywordsForCard.append(tupleofcard)


    KeywordsForCard = sorted(KeywordsForCard,key=take_second,reverse=True)
    TopKeywords = []
    for j in KeywordsForCard[:3]:
        TopKeywords.append(j[0])

    keywords = ""
    for m in TopKeywords:
        keywords = keywords + ' ' +m

    return(keywords)






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

    indexOfCardsToRemove.sort(reverse=True)        # reverse list so that index doesn't change when looped thruough


    for index in indexOfCardsToRemove:
        Questions.pop(index)
        Answers.pop(index)

    return extractKeywords(Questions, Answers, DeckID)



#Remove draw cards and check if duplicate cards
#combine some funcions use meaningful variable names