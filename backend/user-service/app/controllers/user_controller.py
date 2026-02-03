from flask import Blueprint, request, jsonify, g
from app.schemas.ProfileShema import ProfileSchema
from marshmallow import ValidationError
from app.services.UserService import UserService
from app.middlewares.jwt_middleware import jwt_required

user_bp = Blueprint("user", __name__)

@user_bp.route("/internal/users", methods=["POST"])
def createUser():
    # Lấy dữ liệu thô
    raw_data = request.get_json()
    if not isinstance(raw_data, dict):
        return jsonify({"error": "Invalid payload"}), 400
    
    # Làm sạch các chuỗi trong dữ liệu thô
    # Chỉ strip toàn bộ chuỗi; chỉ lowercase cho các trường email/username
    for key, value in list(raw_data.items()):
        if isinstance(value, str):
            cleaned = value.strip()
            if key.lower() in ('email', 'username'):
                cleaned = cleaned.lower()
            raw_data[key] = cleaned

    # Kiểm tra xem có user_id không
    user_id = raw_data.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing user_id from Auth Service"}), 400 

    schema = ProfileSchema()

    try: 
        # Validate dữ liệu đã làm sạch
        clean_data = schema.load(raw_data)
        # đảm bảo id là int nếu có
        try:
            clean_data['id'] = int(user_id)
        except Exception:
            clean_data['id'] = user_id

        # Kiểm tra role = admin thì sensors và topic = null
        #          role = user  thì nhận sensors và topic

        if clean_data.get('role') == 'admin':
            clean_data['sensors'] = None
            clean_data['topic'] = None

        # Gọi Service
        new_user = UserService.create_user(clean_data)

        # Trả về respone
        return jsonify({
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "tel": new_user.telphone,  
            "role": new_user.role,
            "sensors": new_user.sensors,
            "topic": new_user.topic,
            "created_at": new_user.created_at.isoformat() if hasattr(new_user.created_at, 'isoformat') else new_user.created_at
        }), 201
    
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500

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
                "sensors": user_data.sensors,
                "topic": user_data.topic
            }
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Unauthorized access", "error": str(e)}), 401