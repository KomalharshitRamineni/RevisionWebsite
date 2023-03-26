
import numpy as np




def returnBestAndWorstScores(Quizzes,ParentDeck,SubDecksInParentDeck):
    BestScore = 0
    WorstScore = 1
    BestQuiz = []
    WorstQuiz = []
    
    for x in Quizzes:
        score = x[2]#check if score parent deck = 

        if x[0] == ParentDeck:
            if score>=BestScore:
                BestScore=score
            if score<=WorstScore:
                WorstScore=score


    for x in Quizzes:
        score = x[2]
        if score == BestScore:
            if x[1][3] in SubDecksInParentDeck and len(BestQuiz) == 0:#ensures that if same score than only one
                BestQuiz.append(x)

        elif score == WorstScore:
            if x[1][3] in SubDecksInParentDeck and len(WorstQuiz) == 0:
                WorstQuiz.append(x)

                
    if len(BestQuiz) == 0:
        BestQuiz = None
    elif len(WorstQuiz) == 0:
        WorstQuiz =None

    BestAndWorstQuiz = [BestQuiz,WorstQuiz]
    return BestAndWorstQuiz







def merge_sort(arr, reverse):#Reverse=True or False
    if len(arr) <= 1:
        return arr

    # Split the array into two halves
    mid = len(arr) // 2
    left = arr[:mid]
    right = arr[mid:]

    # Recursively sort the two halves
    left_sorted = merge_sort(left, reverse)
    right_sorted = merge_sort(right, reverse)

    # Merge the two sorted halves in the requested order
    result = []
    i, j = 0, 0
    while i < len(left_sorted) and j < len(right_sorted):
        if (not reverse and left_sorted[i] <= right_sorted[j]) or (reverse and left_sorted[i] >= right_sorted[j]):
            result.append(left_sorted[i])
            i += 1
        else:
            result.append(right_sorted[j])
            j += 1

    # Add any remaining elements from the left or right halves
    result += left_sorted[i:]
    result += right_sorted[j:]

    return result


def merge_sort_by_index(arr, index,reverse):
    if len(arr) <= 1:
        return arr

    # Split the array into two halves
    mid = len(arr) // 2
    left = arr[:mid]
    right = arr[mid:]

    # Recursively sort the two halves
    left_sorted = merge_sort_by_index(left, index,reverse)
    right_sorted = merge_sort_by_index(right, index,reverse)

    # Merge the two sorted halves based on the specified index
    result = []
    i, j = 0, 0
    while i < len(left_sorted) and j < len(right_sorted):
        if (not reverse and left_sorted[i][index] <= right_sorted[j][index]) or (reverse and left_sorted[i][index] >= right_sorted[j][index]):
            result.append(left_sorted[i])
            i += 1
        else:
            result.append(right_sorted[j])
            j += 1


    # Add any remaining elements from the left or right halves
    result += left_sorted[i:]
    result += right_sorted[j:]

    return result



def removePunc(string):
    symbols = "!\"#$%&()*+-./:;<=>?@[\]^_`{|}~,"
    for x in string:
        for y in symbols:
            if x == y:
                string = string.replace(x,'')
    

    return string



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


    KeywordsForCard = merge_sort_by_index(KeywordsForCard,1,True)


    #KeywordsForCard = sorted(KeywordsForCard,key=take_second,reverse=True)



    TopKeywords = []
    for j in KeywordsForCard[:3]:
        TopKeywords.append(j[0])

    keywords = ""
    for m in TopKeywords:
        keywords = keywords + ' ' +m

    return(keywords)