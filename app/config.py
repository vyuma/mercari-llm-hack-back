import os

# Base directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Database configuration
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
