from flask import Flask
from auth import auth_bp, User, hash_password
from user_management import user_mgmt_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_mgmt_bp)
    
    return app
