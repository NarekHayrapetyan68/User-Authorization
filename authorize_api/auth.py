from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
)
from models import verify_user, get_user_by_email, create_user
from app import redis_client
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
