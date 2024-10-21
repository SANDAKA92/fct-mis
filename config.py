import os

class Config:
    SECRET_KEY = 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///umis.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

