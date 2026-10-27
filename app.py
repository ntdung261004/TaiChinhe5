import os
from flask import Flask
from flask_migrate import Migrate
from models import db

# Import các Blueprints
from routes.main_routes import main_bp
from routes.api_routes import api_bp

app = Flask(__name__)
app.secret_key = 'taichinh_e5_secret_key'

# Cấu hình Database
basedir = os.path.abspath(os.path.dirname(__name__))
db_path = os.path.join(basedir, 'database')
if not os.path.exists(db_path):
    os.makedirs(db_path)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(db_path, 'luong_trungdoan.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Khởi tạo DB & Migrate
db.init_app(app)
migrate = Migrate(app, db)

# Đăng ký các Routes
app.register_blueprint(main_bp)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)