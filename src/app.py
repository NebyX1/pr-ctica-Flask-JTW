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
from models import db, User
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


# @app.route('/user/<int:user_id>', methods=['DELETE'])
# def delete_user(user_id):
#     del user[user_id]
#     json_text = jsonify(user)
#     return 



# Acá se termina de trabajar, todo lo de abajo no se toca

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
