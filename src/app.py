"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Characters, Planets, Vehicles, Favourites
import json
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


# Acá empezamos a trabajar, todo el resto sobre esta línea no se toca

@app.route('/user', methods=['GET'])
def handle_allusers():
    allusers = User.query.all()
    results = list(map(lambda item: item.serialize(),allusers))
    return jsonify(results), 200


@app.route('/user/<int:user_id>', methods=['GET'])
def handle_one_user(user_id):
    oneuser = User.query.filter_by(id=user_id).first()
    if oneuser is None:
        return jsonify({"msg":"usuario no existente"}), 404
    else:
        return jsonify(oneuser.serialize()), 200

@app.route('/user', methods=['POST'])
def add_user():
    request_body = request.data
    decoded_object = json.loads(request_body)
    get_email = User.query.filter_by(email=decoded_object["email"]).first()
    if get_email is None:
        new_user = User(user_name=decoded_object["user_name"], email=decoded_object["email"], password=decoded_object["password"])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg":"usuario creado exitosamente"}), 200
    else:
        return jsonify({"msg":"el email ya existe"}), 400

#Acá van todas las funciones que convocan a todos los elementos dentro de cada categoría

@app.route('/characters', methods=['GET'])
def handle_characters():
    all_characters = Characters.query.all()
    results = list(map(lambda item: item.serialize(),all_characters))
    return jsonify(results), 200

@app.route('/planets', methods=['GET'])
def handle_planet():
    all_planets = Planets.query.all()
    results = list(map(lambda item: item.serialize(),all_planets))
    return jsonify(results), 200

@app.route('/vehicles', methods=['GET'])
def handle_vehicle():
    all_vehicles = Vehicles.query.all()
    results = list(map(lambda item: item.serialize(),all_vehicles))
    return jsonify(results), 200

@app.route('/favourites', methods=['GET'])
def handle_favourites():
    all_favourites = Favourites.query.all()
    results = list(map(lambda item: item.serialize(),all_favourites))
    return jsonify(results), 200

#Acá van todas las funciones que devuelven los elementos individuales

@app.route('/characters/<int:character_id>', methods=['GET'])
def handle_one_character(character_id):
    one_character = Characters.query.filter_by(id=character_id).first()
    if one_character is None:
        return jsonify({"msg":"planeta no existente"}), 404
    else:
        return jsonify(one_character.serialize()), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def handle_one_planet(planet_id):
    one_planet = Planets.query.filter_by(id=planet_id).first()
    if one_planet is None:
        return jsonify({"msg":"planeta no existente"}), 404
    else:
        return jsonify(one_planet.serialize()), 200

@app.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def handle_one_vehicle(vehicle_id):
    one_vehicle = Vehicles.query.filter_by(id=vehicle_id).first()
    if one_vehicle is None:
        return jsonify({"msg":"vehículo no existente"}), 404
    else:
        return jsonify(one_vehicle.serialize()), 200


#Acá van las consultas anidadas de personajes, vehículos y planetas dependiendo del user

@app.route('/favorite/character/<int:user_id>/<int:character_id>', methods=['POST'])
def add_NewFavCharacter(user_id, character_id):
	# Aquí verificamos si el usuario ingresado existe
	userFav = Favourites.query.filter_by(id=user_id).first() 
	if userFav:
		characterId = Favourites.query.filter_by(id=character_id).first()
		if characterId:
			response_body = {"msg": "El personaje seleccionado ya está en la lista de favoritos"}
			return jsonify(response_body), 404
		else:
			NewCharacter = Favourites(id_user = user_id, id_character = character_id)
			db.session.add(NewCharacter)
			db.session.commit()
			response_body = {"msg":"Se ha agregado el personaje a Favoritos"}
			return jsonify(response_body), 200
	else:
		response_body = {"msg":"El usuario no existe"}
		return jsonify(response_body), 404


@app.route('/favorite/planets/<int:user_id>/<int:planet_id>', methods=['POST'])
def add_NewFavPlanets(user_id, planet_id):
	# Aquí verificamos si el usuario ingresado existe
	userFav = Favourites.query.filter_by(id=user_id).first() 
	if userFav:
		planetId = Favourites.query.filter_by(id=planet_id).first()
		if planetId:
			response_body = {"msg": "El planeta seleccionado ya está en la lista de favoritos"}
			return jsonify(response_body), 404
		else:
			NewPlanet = Favourites(id_user = user_id, id_planet = planet_id)
			db.session.add(NewPlanet)
			db.session.commit()
			response_body = {"msg":"Se ha agregado el planeta a Favoritos"}
			return jsonify(response_body), 200
	else:
		response_body = {"msg":"El usuario no existe"}
		return jsonify(response_body), 404


@app.route('/favorite/vehicles/<int:user_id>/<int:vehicle_id>', methods=['POST'])
def add_NewFavVehicle(user_id, vehicle_id):
	# Aquí verificamos si el usuario ingresado existe
	userFav = Favourites.query.filter_by(id=user_id).first() 
	if userFav:
		vehicleId = Favourites.query.filter_by(id=vehicle_id).first()
		if vehicleId:
			response_body = {"msg": "El vehículo seleccionado ya está en la lista de favoritos"}
			return jsonify(response_body), 404
		else:
			NewVehicle = Favourites(id_user = user_id, id_vehicle = vehicle_id)
			db.session.add(NewVehicle)
			db.session.commit()
			response_body = {"msg":"Se ha agregado el vehículo a Favoritos"}
			return jsonify(response_body), 200
	else:
		response_body = {"msg":"El usuario no existe"}
		return jsonify(response_body), 404


#Acá van las funciones necesarias para borrar personajes, vehículos y planetas de favoritos

@app.route('/favorite/character/<int:user_id>/<int:character_id>', methods=['DELETE'])
def borrarCharacterFav(user_id, character_id):
	# Aquí verificamos si el usuario ingresado existe
	userFav = Favourites.query.filter_by(id=user_id).first() 
	if userFav is None:
		response_body = {"msg": "El usuario ingresado no existe"}
		return jsonify(response_body), 404
	#Aquí verificamos si el personaje ya esté ingresado en favoritos
	favCharacter = Favourites.query.filter_by(id=character_id).first() 
	if favCharacter is None:
		response_body = {"msg": "El personaje ingresado no existe dentro de favoritos"}
		return jsonify(response_body), 404
	#Aquí le indicamos que debe borrar al personaje seleccionado
	exFavCharacter = Favourites.query.filter_by(id=user_id).filter_by(id=character_id).first()
	db.session.delete(exFavCharacter)
	db.session.commit()
	response_body = {"msg": "El personaje seleccionado fue borrado con exito"}
	return jsonify(response_body), 200


@app.route('/favorite/planets/<int:user_id>/<int:planet_id>', methods=['DELETE'])
def borrarPlanetFav(user_id, planet_id):
	# Aquí verificamos si el usuario ingresado existe
	userFav = Favourites.query.filter_by(id=user_id).first() 
	if userFav is None:
		response_body = {"msg": "El usuario ingresado no existe"}
		return jsonify(response_body), 404
	#Aquí verificamos si el planeta ya esté ingresado en favoritos
	favPlanet = Favourites.query.filter_by(id=planet_id).first() 
	if favPlanet is None:
		response_body = {"msg": "El planeta ingresado no existe dentro de favoritos"}
		return jsonify(response_body), 404
	#Aquí le indicamos que debe borrar al planeta seleccionado
	exFavPlanet = Favourites.query.filter_by(id=user_id).filter_by(id=planet_id).first()
	db.session.delete(exFavPlanet)
	db.session.commit()
	response_body = {"msg": "El planeta seleccionado fue borrado con exito"}
	return jsonify(response_body), 200


@app.route('/favorite/vehicles/<int:user_id>/<int:vehicle_id>', methods=['DELETE'])
def borrarVehicleFav(user_id, vehicle_id):
	# Aquí verificamos si el usuario ingresado existe
	userFav = Favourites.query.filter_by(id=user_id).first() 
	if userFav is None:
		response_body = {"msg": "El usuario ingresado no existe"}
		return jsonify(response_body), 404
	#Aquí verificamos si el planeta ya esté ingresado en favoritos
	favVehicle = Favourites.query.filter_by(id=vehicle_id).first() 
	if favVehicle is None:
		response_body = {"msg": "El vehículo ingresado no existe dentro de favoritos"}
		return jsonify(response_body), 404
	#Aquí le indicamos que debe borrar al planeta seleccionado
	exFavVehicle = Favourites.query.filter_by(id=user_id).filter_by(id=vehicle_id).first()
	db.session.delete(exFavVehicle)
	db.session.commit()
	response_body = {"msg": "El vehículo seleccionado fue borrado con exito"}
	return jsonify(response_body), 200

# Acá se termina de trabajar, todo lo de abajo no se toca

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
