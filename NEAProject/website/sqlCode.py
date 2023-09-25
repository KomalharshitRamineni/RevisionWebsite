import sqlite3

connection = sqlite3.connect("database.db",check_same_thread=False)
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS FlashcardDeck (
    FlashcardDeckID INTEGER PRIMARY KEY,
    FlashcardDeckName TEXT)
    """)

cursor.execute("""CREATE TABLE IF NOT EXISTS ParentFlashcardDeck (
    ParentFlashcardDeckID INTEGER PRIMARY KEY,
    FlashcardDeckName TEXT)
    """)

cursor.execute("""CREATE TABLE IF NOT EXISTS FlashcardsDecksAndUserIDs (
    FlashcardID INTEGER,
    UserID INTEGER,
    FlashcardDeckID INTEGER,
    ParentFlashcardDeckID,
    FOREIGN KEY(UserID) REFERENCES user(UserID),
    FOREIGN KEY(FlashcardID) REFERENCES Flashcard(FlashcardID),
    FOREIGN KEY(FlashcardDeckID) REFERENCES FlashcardDeck(FlashcardDeckID),
    FOREIGN KEY(ParentFlashcardDeckID) REFERENCES ParentFlashcardDeck(ParentFlashcardDeckID))
    """)


cursor.execute("""CREATE TABLE IF NOT EXISTS Flashcard (
    FlashcardID INTEGER PRIMARY KEY,
    FlashcardQuestion TEXT,
    FlashcardAnswer TEXT,
    Keywords TEXT)
    """)

cursor.execute("""CREATE TABLE IF NOT EXISTS User (
    UserID INTEGER PRIMARY KEY,
    Email TEXT UNIQUE,
    Password TEXT,
    FirstName TEXT,
    PasswordAttempts INTEGER,
    EmailConfirmed INTEGER)
    """)

cursor.execute("""CREATE TABLE IF NOT EXISTS Question ( 
    QuestionID INTEGER PRIMARY KEY,
    NumberOfTimesAnswered INTEGER,
    NumberOfTimesAnsweredCorrectly INTEGER,
    QuestionType TEXT,
    Question TEXT,
    Answer TEXT,
    CorrectAnswer TEXT,
    FlashcardID INTEGER,
    FOREIGN KEY(FlashcardID) REFERENCES Flashcard(FlashcardID))
    """)

cursor.execute("""CREATE TABLE IF NOT EXISTS Quiz ( 
    QuizID INTEGER PRIMARY KEY,
    NumberOfQuestions INTEGER,
    NumberOfQuestionsAnsweredCorrectly INTEGER,
    DeckName TEXT)
    """)

cursor.execute("""CREATE TABLE IF NOT EXISTS QuizQuestions ( 
    QuizID INTEGER,
    QuestionID,
    FOREIGN KEY(QuizID) REFERENCES Quiz(QuizID),
    FOREIGN KEY(QuestionID) REFERENCES Question(QuestionID))
    """)

cursor.execute("""CREATE TABLE IF NOT EXISTS PastQuiz ( 
    UserID INTEGER,
    QuizID INTEGER,
    FOREIGN KEY(UserID) REFERENCES user(UserID),
    FOREIGN KEY(QuizID) REFERENCES Quiz(QuizID))
    """)

connection.commit()
connection.close()
