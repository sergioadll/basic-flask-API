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
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
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



@app.route('/user', methods=['GET'])
def get_users():

    users = User.query.all()
    serialized_users = list(map(lambda user: user.serialize(), users))

    return jsonify(serialized_users), 200



@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):

    user = User.query.get(id)
    serialized_user = user.serialize()
    return jsonify(serialized_user), 200



@app.route('/user', methods=['POST'])
def create_user():

    payload = request.get_json()

    new_user = User(email=payload['email'], password=payload['password'])

    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.serialize()), 200



@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):

    user = User.query.get(id)
    body = request.get_json()
    print('user',user)

    user.email = body['email']
    user.password = body['password']
    print('updated user',user)

    db.session.commit()

    return jsonify(user.serialize()), 200



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
