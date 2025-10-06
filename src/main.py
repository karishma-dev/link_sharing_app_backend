import sys
import os
# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from src.database.db import init_db
from src.models.models import db
from dotenv import load_dotenv
from src.routers.auth import auth_blueprint
from src.routers.users import users_blueprint
from src.routers.platform import platforms_blueprint
from src.routers.admin import admin_blueprint

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # SQLAlchemy configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database - much simpler now!
    init_db(app)

    @app.route("/", methods=['GET'])
    def home():
        return "hello world!"

    app.register_blueprint(auth_blueprint, url_prefix="/api/auth")
    app.register_blueprint(users_blueprint, url_prefix='/api/users')
    app.register_blueprint(platforms_blueprint, url_prefix='/api/platforms')
    app.register_blueprint(admin_blueprint, url_prefix='/api/admin')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(port=5001, debug=True, use_reloader=False, threaded=True)