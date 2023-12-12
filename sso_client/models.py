from flask_sqlalchemy import SQLAlchemy


db: SQLAlchemy = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(40), nullable=False) # 來源
    source_id = db.Column(db.Integer, nullable=False) # 來源 ID
    rand_string = db.Column(db.String, nullable=True) # 隨機字串