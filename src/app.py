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
# from models import Person
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager

app = Flask(__name__)
app.url_map.strict_slashes = False


# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)


db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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
    results = list(map(lambda item: item.serialize(), allusers))
    return jsonify(results), 200


@app.route('/user/<int:user_id>', methods=['GET'])
def handle_one_user(user_id):
    oneuser = User.query.filter_by(id=user_id).first()
    if oneuser is None:
        return jsonify({"msg": "usuario no existente"}), 404
    else:
        return jsonify(oneuser.serialize()), 200


@app.route('/user', methods=['POST'])
def add_user():
    request_body = request.data
    decoded_object = json.loads(request_body)
    get_email = User.query.filter_by(email=decoded_object["email"]).first()
    if get_email is None:
        new_user = User(user_name=decoded_object["user_name"],
                        email=decoded_object["email"], password=decoded_object["password"])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "usuario creado exitosamente"}), 200
    else:
        return jsonify({"msg": "el email ya existe"}), 400
# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.


@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    get_user = User.query.filter_by(email=email).first()
    if get_user is None:
        print("no hay ningún usuario")
    else:
        print("hay al menos un usuario")

    if email != get_user.email or password != get_user.password:
        return jsonify({"msg": "Bad email or password"}), 401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)
# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    get_user = User.query.filter_by(email=current_user).first()
    print(get_user.serialize())
    return jsonify(logged_in_as=current_user), 200


# Acá van todas las funciones que convocan a todos los elementos dentro de cada categoría

@app.route('/characters', methods=['GET'])
def handle_characters():
    all_characters = Characters.query.all()
    results = list(map(lambda item: item.serialize(), all_characters))
    return jsonify(results), 200


@app.route('/planets', methods=['GET'])
def handle_planet():
    all_planets = Planets.query.all()
    results = list(map(lambda item: item.serialize(), all_planets))
    return jsonify(results), 200


@app.route('/vehicles', methods=['GET'])
def handle_vehicle():
    all_vehicles = Vehicles.query.all()
    results = list(map(lambda item: item.serialize(), all_vehicles))
    return jsonify(results), 200


@app.route('/favourites', methods=['GET'])
def handle_favourites():
    all_favourites = Favourites.query.all()
    results = list(map(lambda item: item.serialize(), all_favourites))
    return jsonify(results), 200

# Acá van todas las funciones que devuelven los elementos individuales


@app.route('/characters/<int:character_id>', methods=['GET'])
def handle_one_character(character_id):
    one_character = Characters.query.filter_by(id=character_id).first()
    if one_character is None:
        return jsonify({"msg": "planeta no existente"}), 404
    else:
        return jsonify(one_character.serialize()), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def handle_one_planet(planet_id):
    one_planet = Planets.query.filter_by(id=planet_id).first()
    if one_planet is None:
        return jsonify({"msg": "planeta no existente"}), 404
    else:
        return jsonify(one_planet.serialize()), 200


@app.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def handle_one_vehicle(vehicle_id):
    one_vehicle = Vehicles.query.filter_by(id=vehicle_id).first()
    if one_vehicle is None:
        return jsonify({"msg": "vehículo no existente"}), 404
    else:
        return jsonify(one_vehicle.serialize()), 200


# Acá van las consultas anidadas de personajes, vehículos y planetas dependiendo del user

@app.route('/favourites/characters/<int:user_ID>/<int:character_ID>', methods=['POST'])
def add_NewFavCharacter(user_ID, character_ID):
    # Aquí verificamos si el usuario ingresado existe
    character = Favourites.query.filter_by(
        character_id=character_ID, user_id=user_ID).first()
    if character is None:
        existe = Characters.query.filter_by(id=character_ID).first()
        if existe is None:
            response_body = {"msg": "El personaje no existe"}
            return jsonify(response_body), 404
        else:
            user = User.query.filter_by(id=user_ID).first()
            if user is None:
                response_body = {"msg": "El usuario no existe"}
                return jsonify(response_body), 404
            else:
                favorito = Favourites(
                    character_id=character_ID, user_id=user_ID)
                db.session.add(favorito)
                db.session.commit()
                response_body = {
                    "msg": "Se ha agregado el personaje a favoritos"}
                return jsonify(response_body), 200
    else:
        response_body = {"msg": "El personaje ya está agregado"}
        return jsonify(response_body), 404


@app.route('/favourites/planets/<int:user_ID>/<int:planet_ID>', methods=['POST'])
def add_NewFavPlanets(user_ID, planet_ID):
    # Aquí verificamos si el usuario ingresado existe
    planet = Favourites.query.filter_by(
        planet_id=planet_ID, user_id=user_ID).first()
    if planet is None:
        existe = Planets.query.filter_by(id=planet_ID).first()
        if existe is None:
            response_body = {"msg": "El planeta no existe"}
            return jsonify(response_body), 404
        else:
            user = User.query.filter_by(id=user_ID).first()
            if user is None:
                response_body = {"msg": "El usuario no existe"}
                return jsonify(response_body), 404
            else:
                favorito = Favourites(planet_id=planet_ID, user_id=user_ID)
                db.session.add(favorito)
                db.session.commit()
                response_body = {
                    "msg": "Se ha agregado el planeta a favoritos"}
                return jsonify(response_body), 200
    else:
        response_body = {"msg": "El planeta ya está agregado"}
        return jsonify(response_body), 404


@app.route('/favourites/vehicles/<int:user_ID>/<int:vehicle_ID>', methods=['POST'])
def add_NewFavVehicle(user_ID, vehicle_ID):
    vehicle = Favourites.query.filter_by(
        vehicle_id=vehicle_ID, user_id=user_ID).first()
    if vehicle is None:
        existe = Vehicles.query.filter_by(id=vehicle_ID).first()
        if existe is None:
            response_body = {"msg": "El vehículo no existe"}
            return jsonify(response_body), 404
        else:
            user = User.query.filter_by(id=user_ID).first()
            if user is None:
                response_body = {"msg": "El usuario no existe"}
                return jsonify(response_body), 404
            else:
                favorito = Favourites(vehicle_id=vehicle_ID, user_id=user_ID)
                db.session.add(favorito)
                db.session.commit()
                response_body = {
                    "msg": "Se ha agregado el vehículo a favoritos"}
                return jsonify(response_body), 200
    else:
        response_body = {"msg": "El vehículo ya está agregado"}
        return jsonify(response_body), 404


# Acá van las funciones necesarias para borrar personajes, vehículos y planetas de favoritos

@app.route('/favourites/characters/<int:user_ID>/<int:character_ID>', methods=['DELETE'])
def borrar_Character_Fav(user_ID, character_ID):
    # Aquí verificamos si el usuario ingresado existe
    user = User.query.filter_by(id=user_ID).first()
    if user is None:
        response_body = {"msg": "El usuario ingresado no existe"}
        return jsonify(response_body), 404
    # Aquí verificamos si el personaje ya esté ingresado en favoritos
    personaje = Characters.query.filter_by(id=character_ID).first()
    if personaje is None:
        response_body = {
            "msg": "El personaje ingresado no existe dentro de favoritos"}
        return jsonify(response_body), 404
    # Aquí le indicamos que debe borrar al personaje seleccionado
    borrar_personaje = Favourites.query.filter_by(
        user_id=user_ID).filter_by(character_id=character_ID).first()
    if borrar_personaje is None:
        response_body = {
            "msg": "El personaje ingresado no existe dentro de favoritos"}
        return jsonify(response_body), 404
    else:
        db.session.delete(borrar_personaje)
        db.session.commit()
        response_body = {
            "msg": "El personaje seleccionado fue borrado con exito"}
        return jsonify(response_body), 200


@app.route('/favourites/planets/<int:user_ID>/<int:planet_ID>', methods=['DELETE'])
def borrar_Planet_Fav(user_ID, planet_ID):
    # Aquí verificamos si el usuario ingresado existe
    user = User.query.filter_by(id=user_ID).first()
    if user is None:
        response_body = {"msg": "El usuario ingresado no existe"}
        return jsonify(response_body), 404
    # Aquí verificamos si el planeta ya esté ingresado en favoritos
    planeta = Planets.query.filter_by(id=planet_ID).first()
    if planeta is None:
        response_body = {
            "msg": "El planeta ingresado no existe dentro de favoritos"}
        return jsonify(response_body), 404
    # Aquí le indicamos que debe borrar al planeta seleccionado
    borrar_planeta = Favourites.query.filter_by(
        user_id=user_ID).filter_by(planet_id=planet_ID).first()
    if borrar_planeta is None:
        response_body = {
            "msg": "El planeta ingresado no existe dentro de favoritos"}
        return jsonify(response_body), 404
    else:
        db.session.delete(borrar_planeta)
        db.session.commit()
        response_body = {
            "msg": "El planeta seleccionado fue borrado con exito"}
        return jsonify(response_body), 200


@app.route('/favourites/vehicles/<int:user_ID>/<int:vehicle_ID>', methods=['DELETE'])
def borrar_Vehicle_Fav(user_ID, vehicle_ID):
    # Aquí verificamos si el usuario ingresado existe
    user = User.query.filter_by(id=user_ID).first()
    if user is None:
        response_body = {"msg": "El vehículo ingresado no existe"}
        return jsonify(response_body), 404
    # Aquí verificamos si el vehículo ya esté ingresado en favoritos
    vehiculo = Vehicles.query.filter_by(id=vehicle_ID).first()
    if vehiculo is None:
        response_body = {
            "msg": "El vehículo ingresado no existe dentro de favoritos"}
        return jsonify(response_body), 404

    # Aquí le indicamos que debe borrar el vehículo seleccionado
    borrar_vehiculo = Favourites.query.filter_by(
        user_id=user_ID).filter_by(vehicle_id=vehicle_ID).first()
    if borrar_vehiculo is None:
        response_body = {
            "msg": "El vehículo ingresado no existe dentro de favoritos"}
        return jsonify(response_body), 404
    else:
        db.session.delete(borrar_vehiculo)
        db.session.commit()
        response_body = {
            "msg": "El planeta seleccionado fue borrado con exito"}
        return jsonify(response_body), 200

# Acá se termina de trabajar, todo lo de abajo no se toca


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
