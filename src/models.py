from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

# Esta clase nos permite traer la información de todos los usuarios
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(250) , nullable=False)
    password = db.Column(db.String(250) , nullable=False)
    email = db.Column(db.String(250), unique= True, nullable=False)
    favourites = db.relationship('Favourites', backref='user', lazy=True)
    
    def __repr__(self):
        return '<User %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_name": self.user_name,
            "email": self.email,
        }


# Esta clase nos permite importar todos los personajes de Star Wars

class Characters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_name = db.Column(db.String(250))
    eye_color = db.Column(db.String(250))
    gender = db.Column(db.String(250))
    hair_color = db.Column(db.String(250))
    height = db.Column(db.Integer)
    skin_color = db.Column(db.String(250))
    favourites = db.relationship('Favourites', backref='characters', lazy=True)

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
        
class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    planet_name = db.Column(db.String(250))
    climate = db.Column(db.String(250))
    population = db.Column(db.Integer)
    orbital_period = db.Column(db.Integer)
    rotation_period = db.Column(db.Integer)
    diameter = db.Column(db.Integer)
    favourites = db.relationship('Favourites', backref='planets', lazy=True)
    
    def __repr__(self):
        return '<Character %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "planet_name": self.planet_name,
            "climate": self.climate,
            "population": self.population,
            "orbital_period": self.orbital_period,
            "rotation_period": self.rotation_period,
            "diameter": self.diameter,
        }


class Vehicles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_name = db.Column(db.String(250))
    cargo_capacity = db.Column(db.Integer)
    consumables = db.Column(db.String(250))
    cost_in_credits = db.Column(db.Integer)
    crew_capacity = db.Column(db.Integer)
    manufacturer = db.Column(db.String(250))
    favourites = db.relationship('Favourites', backref='vehicles', lazy=True)

    def __repr__(self):
        return '<Vehicle %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "vehicle_name": self.vehicle_name,
            "cargo_capacity": self.cargo_capacity,
            "consumables": self.consumables,
            "cost_in_credits": self.cost_in_credits,
            "crew_capacity": self.crew_capacity,
            "manufacturer": self.manufacturer,
        }


class Favourites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))

    def __repr__(self):
        return '<Favourites %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "character_id": self.character_id,
            "vehicle_id": self.vehicle_id,
        }