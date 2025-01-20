class Config:
    SECRET_KEY = 'josephleon'  # Change this to a strong, random value for production
    SQLALCHEMY_DATABASE_URI = 'sqlite:///contacts.db'  # SQLite database file
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True  # Set to False in production
