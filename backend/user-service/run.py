# backend\user-service\run.py

from app import create_app, db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("User Service đã kết nối MySQL và khởi tạp bảng thành công")

    app.run(host= "0.0.0.0", port = 5002, debug = True)