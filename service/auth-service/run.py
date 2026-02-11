from app import create_app, db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # <--- Quan trọng: Tự động tạo bảng users trong MySQL
        print("Đã kết nối MySQL và khởi tạo bảng thành công!")
        
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )
