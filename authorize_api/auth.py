from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
)
from models import verify_user, get_user_by_email, create_user
from app import redis_client, jwt
from validators import is_valid_email

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/register', methods=['POST'])
def register():
    email = request.json.get('email')
    password = request.json.get('password')

    if not is_valid_email(email):
        return jsonify({"msg": "Email is not valid"}), 400

    if get_user_by_email(email):
        return jsonify({"msg": "Email already exists"}), 400

    create_user(email, password)
    return jsonify({"msg": "User created successfully"}), 201


@auth_blueprint.route('/login', methods=['GET'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    if not verify_user(email, password):
        return jsonify({"msg": "Bad email or password"}), 401

    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)

    return jsonify(access_token=access_token, refresh_token=refresh_token)


@jwt_required()
def logout():
    jti = get_jwt()['jti']
    redis_client.set(jti, "", ex=3600)  # Expires in 1 hour
    return jsonify({"msg": "Access token has been revoked"}), 200


@auth_blueprint.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify(access_token=access_token)


@auth_blueprint.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    user = get_user_by_email(current_user)
    if user:
        return jsonify(email=user.email)
    return jsonify({"msg": "User not found"}), 404

def is_token_revoked(jwt_payload):
    jti = jwt_payload['jti']
    token_in_redis = redis_client.get(jti)
    return token_in_redis is not None

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return is_token_revoked(jwt_payload)