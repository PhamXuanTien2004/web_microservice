from flask import Flask, Blueprint, request, jsonify, g
from app.schemas.ProfileShema import ProfileSchema
from marshmallow import ValidationError
from app.services.UserService import UserService
from app.middlewares.jwt_middleware import jwt_required

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.route("/createUser", methods = ["POST"])
def createUser():
    # Nhận dữ liệ thô
    raw_data = request.get_json()

    # Validate + Clean data qua Schema
    schema = ProfileSchema()

    try: 
        clean_data = schema.load(raw_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    # Service: Save new user data

    try: 
        new_user = UserService.create_user(clean_data)

        # Show new user data
        return jsonify({
            "name": new_user.name,
            "email": new_user.email,
            "tel" : new_user.telphone,
            "role": new_user.role,
            "sensors": new_user.sensors,
            "created at": new_user.created_at
        }), 201
    
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
@user_bp.route('/profile', methods=['GET'])
@jwt_required
def getMyProfile():
    token_info = g.token_payload 
    user_data = UserService.findUserById(g.user_id)
    
    if user_data:
        return jsonify({
            "status": "success",
            "token_info": token_info.get("username"), 
            "data": user_data
        }), 200
    
