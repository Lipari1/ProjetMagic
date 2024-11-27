from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def getDb(): return db