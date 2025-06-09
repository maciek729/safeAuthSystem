class Config:
    SECRET_KEY = 'supersecretkey'
    DATABASE_PATH = 'database.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False