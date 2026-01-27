from flask import Blueprint, request, jsonify, g
from app.schemas.ProfileShema import ProfileSchema
from marshmallow import ValidationError
from app.services.UserService import UserService
from app.middlewares.jwt_middleware import jwt_required

user_bp = Blueprint("user", __name__)

@user_bp.route("/internal/users", methods=["POST"])
def createUser():
    raw_data = request.get_json()
    user_id = raw_data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "Missing user_id from Auth Service"}), 400 

    schema = ProfileSchema()

    try: 
        # 1. Validate + Clean data
        clean_data = schema.load(raw_data)
        clean_data['id'] = user_id

        # 2. Chuẩn hóa Role về chữ thường (lowercase)
        if 'role' in clean_data:
            clean_data['role'] = clean_data['role'].strip().lower()

        # 3. Service: Save new user data
        new_user = UserService.create_user(clean_data)

        return jsonify({
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "tel": new_user.telphone,  
            "role": new_user.role,
            "sensors": new_user.sensors,
            "created_at": new_user.created_at.isoformat() if hasattr(new_user.created_at, 'isoformat') else new_user.created_at
        }), 201
    
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@user_bp.route('/profile', methods=['GET'])
@jwt_required
def getMyProfile():
    try:
        # g.user_id được set từ jwt_middleware
        user_data = UserService.findUserById(g.user_id)
        
        if not user_data:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "status": "success", 
            "data": {
                "id": user_data.id,
                "name": user_data.name,
                "email": user_data.email,
                "role": user_data.role,
                "sensors": user_data.sensors
            }
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Unauthorized access", "error": str(e)}), 401