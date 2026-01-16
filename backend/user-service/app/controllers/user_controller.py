from flask import Flask, Blueprint, request, jsonify, g
from app.schemas.ProfileShema import ProfileSchema
from marshmallow import ValidationError
from app.services.UserService import UserService
from app.middlewares.jwt_middleware import jwt_required

user_bp = Blueprint("user", __name__)

@user_bp.route("/internal/users", methods = ["POST"])
def createUser():
    # Nhận dữ liệ thô
    raw_data = request.get_json()

    user_id = raw_data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "Missing user_id from Auth Service"}), 400 

    # Validate + Clean data qua Schema
    schema = ProfileSchema()

    try: 
        clean_data = schema.load(raw_data)

        clean_data['id'] = user_id
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    # Service: Save new user data

    try: 
        new_user = UserService.create_user(clean_data)

        # Show new user data
        return jsonify({
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "tel" : new_user.telphone,
            "role": new_user.role,
            "sensors": new_user.sensors,
            "created at": new_user.created_at
        }), 201
    
    except ValidationError as err:
        # Lỗi logic (trùng email, phone...) -> Trả về 400 để Auth Service biết mà Rollback
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        # Lỗi hệ thống -> Trả về 500
        return jsonify({"error": str(e)}), 500
@user_bp.route('/profile', methods=['GET'])
@jwt_required
def getMyProfile():
    user_data = UserService.findUserById(g.user_id)
    
    if user_data:
        return jsonify({
            "status": "success", 
            "data": user_data 
        }), 200
    return jsonify({"error": "User not found"}), 404
    
