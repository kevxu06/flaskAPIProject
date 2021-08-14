import os

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import UserRegister, User, UserLogin, TokenRefresh, UserLogout
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from db import db
from blocklist import BLOCKLIST

uri = os.getenv("DATABASE_URL")  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = uri

app.config["SQLALCHEMY_TRACK_NOTIFICATIONS"] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

api = Api(app)
app.secret_key = 'secret'

jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(_decrypted_header, _decrypted_body):
    return _decrypted_body['jti'] in BLOCKLIST

@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:
        return {'is_admin': True}
    return {'is_admin': False}

@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'description': 'The token has expired',
        'error': 'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'description': 'Signature verification failed.',
                    'error': 'invalid_token'}), 401

@jwt.unauthorized_loader
def unauthorized_loader_callback(error):
    return jsonify({'description': 'Request does not contain an access token.',
                    'error': 'authorization_required'}), 401

@jwt.needs_fresh_token_loader
def needs_fresh_token_loader_callback(_decrypted_header, _decrypted_body):
    return jsonify({'description': 'The token is not fresh.',
                    'error': 'fresh_token_required'}), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({'description': 'The token has been revoked.',
                    'error': 'token_revoked'}), 401



api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(TokenRefresh, '/refresh')

if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)
