from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

# Esta clase nos permite traer la información de todos los usuarios
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(250) , nullable=False)
    password = db.Column(db.String(250) , nullable=False)
    email = db.Column(db.String(250), unique= True, nullable=False)
    
    def __repr__(self):
        return '<User %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_name": self.user_name,
            "email": self.email,
        }


# Esta clase nos permite importar todos los personajes de Star Wars

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_name = db.Column(db.String(250))
    eye_color = db.Column(db.String(250))
    gender = db.Column(db.String(250))
    hair_color = db.Column(db.String(250))
    height = db.Column(db.Integer)
    skin_color = db.Column(db.String(250))

    def __repr__(self):
        return '<Character %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "character_name": self.character_name,
            "eye_color": self.eye_color,
            "gender": self.gender,
            "hair_color": self.hair_color,
            "height": self.height,
            "skin_color": self.skin_color,
        }