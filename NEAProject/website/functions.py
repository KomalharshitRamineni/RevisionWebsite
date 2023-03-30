import numpy as np

def returnBestAndWorstScores(Quizzes,ParentDeck,SubDecksInParentDeck):
    #Quizzes done by the user are passed in as a parameter
    BestScore = 0
    WorstScore = 1
    BestQuiz = []
    WorstQuiz = []
    
    for x in Quizzes:
        score = x[2]
    
    #If quiz completed was from a parent deck then, the quiz data is not used in the process of giving the user feedback

        if x[0] == ParentDeck:
            if score>=BestScore:
                BestScore=score
            if score<=WorstScore:
                WorstScore=score

    for x in Quizzes:
        score = x[2]
        if score == BestScore:
            if x[1][3] in SubDecksInParentDeck and len(BestQuiz) == 0:
                #If user has multiple quizzes with the same score then only first one is chosen
                BestQuiz.append(x)

        elif score == WorstScore:
            if x[1][3] in SubDecksInParentDeck and len(WorstQuiz) == 0:
                #If user has multiple quizzes with the same score then only first one is chosen
                WorstQuiz.append(x)

    if len(BestQuiz) == 0:#If there are no quizzes then None is returned
        BestQuiz = None
    elif len(WorstQuiz) == 0:
        WorstQuiz =None

    BestAndWorstQuiz = [BestQuiz,WorstQuiz]
    return BestAndWorstQuiz



def merge_sort(itemsArray, reverse):#Reverse=True or False
    if len(itemsArray) <= 1:
        return itemsArray

    # Split the array into two halves
    midpoint = len(itemsArray) // 2
    left = itemsArray[:midpoint]
    right = itemsArray[midpoint:]
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



def merge_sort_by_index(itemsArray, index,reverse):
    if len(itemsArray) <= 1:
        return itemsArray

    # Split the array into two halves
    midpoint = len(itemsArray) // 2
    left = itemsArray[:midpoint]
    right = itemsArray[midpoint:]

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
    #if string contains any symbol from symbols then it is removed
    for x in string:
        for y in symbols:
            if x == y:
                string = string.replace(x,'')
    
    return string



def extractKeywords(Questions,Answers, DeckID):
    ExtractedData = []
    #array of questions and answers are passed in as parameters
    for x in range(len(Questions)-1):

        keywords = generateKeywords(Questions[x][2],Answers[x][2])
        #keywords are generated for each question and answer in the arrays
        CardData = {
        
        "cardID": int(Questions[x][0]),
        "deckID": DeckID,
        "deckName":Questions[x][1],
        "question": Questions[x][2],
        "answer": Answers[x][2],
        "keywords": keywords
        
        }
        #data stored in a dictionary which are stored in an array

        ExtractedData.append(CardData)

    return ExtractedData
    #Array of dictionaries returned


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
    #If the string contains a HTML character entity then it is removed
    for CharacterEntity, Value in HTMLCharacterEntities.items():
        if CharacterEntity in string:
            string = string.replace(CharacterEntity,Value)
            
    return string



def checkIfNeedToRemoveFlashcard(string, QuestionType):
    
    removeFlashcard = False
    ItemsToCheckFor = ['<img','Draw','<table']
    #The content of the flashcards being imported from Anki is checked
    #If the flashcard contains an image or a table or if the flashcard requires the user to draw, it needs to be removed

    for item in ItemsToCheckFor:
        if item == 'Draw' and QuestionType =='Question' and item in string:
            removeFlashcard = True
        else:
            if item != 'Draw' and item in string:
                removeFlashcard = True

    return removeFlashcard
    #Returns a boolean value 


def checkIfContainsSpanTag(string):
    #Checks if string has a span html tag
    ContainsSpanTag = False
    SpanTag = '<span'
    if SpanTag in string:
        ContainsSpanTag = True
    return ContainsSpanTag
    #Returns a boolean value

def removeExtraSpaces(string):
    #Function removes any extra spaces in the string 
    splitString = string.split()
    removedSpace = ''
    for x in splitString:
        if removedSpace == '':
            removedSpace = removedSpace + x
        else:
            removedSpace = removedSpace + ' ' + x
    return removedSpace
    #Returns string with removed spaces


def removeHTML(string):
    #Function Removes all HTML tags
    tagOpen = False
    count = 0
    removed = False
    #Loop keeps iterating until no HTML tags are left in the string
    while removed == False:
        if count <= len(string)-1:

            if string[count] == '<': #The start of the HTML tag is identified
                tagOpen = True
                startTag = count

            if tagOpen == True and string[count] == '>': #The end of the HTML tag is identified
                #Once the end of the tag has been identifed then the HTML tag is the content between the start and end
                endTag = count+1
                htmlTag = string[startTag:endTag]
                string = string.replace(htmlTag,' ')#HTML tag is removed
                tagOpen = False
                count = 0
        else:
            removed = True #If no HTML tags are remaining the loop breaks
        count = count + 1

    return string
    #Returns string with removed HTML tags



def processCard(string):
    #cards are processed so that keywords can be extracted
    string = string.lower()

    stopwords = ['describe','explain','define','eg','g','b','e','i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
    symbols = "!\"#$%&()*+-./:;<=>?@[\]^_`{|}~,"

    #Stopwords are common words which need to be removed before extracting keywords
    #Symbols are not words and therfore need to be removed before extracting keywords

    stopwordsRemoved = ""
    
    for word in string.split():
        if word not in stopwords:
            stopwordsRemoved = stopwordsRemoved + " " + word #Stopwords are removed

    for symbol in symbols:
        for word in stopwordsRemoved:
            if word == symbol:
                stopwordsRemoved = stopwordsRemoved.replace(word,' ')
    
    symbolsRemoved = ""
    
    for x in stopwordsRemoved.split():
        if x not in stopwords:
            symbolsRemoved = symbolsRemoved + " " + x #Symbols are removed

    return symbolsRemoved
    #Returns processed string without any symbols of stopwords



def checkIfDecknamesFiltered(DeckNames):
    #Checks whether array only contains parent deck name
    filterd = True
    for x in range(len(DeckNames)-1):
        if DeckNames[x] in DeckNames[x+1]:
            filterd = False
    return filterd
    #Returns boolean value



def generateKeywords(Question, Answer):
    #This function applies the TF-IDF algorithm to extract the keywords

    ProcessedAnswerCard = processCard(Answer).split()
    ProcesesedQuestionCard = processCard(Question).split()

    #Flashcards are processed - all stopwords and symobls are removed
    #And flashcards are split into tokens

    #Create a dictionary of terms and their frequency
    DF = {}
    tokens = ProcessedAnswerCard

    for w in tokens:
        DF.update({w:tokens.count(w)})

    tokens = ProcesesedQuestionCard
    for w in tokens:
        DF.update({w:tokens.count(w)})

    #Create a list of tuples containing keywords and their importance
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
    #Sort keywords by their TF-IDF value, ordered in reverse as largest values are taken

    TopKeywords = []
    for j in KeywordsForCard[:3]:#Top three keywords are taken
        TopKeywords.append(j[0])

    keywords = ""
    for m in TopKeywords:
        keywords = keywords + ' ' + m

    return(keywords)
