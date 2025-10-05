import asyncio
from flask import Flask
from src.database.db import db_manager
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")

    with app.app_context():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(db_manager.connect())

    def sync_disconnect(exc=None):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(db_manager.disconnect())

    app.teardown_appcontext(sync_disconnect)

    @app.route("/", methods=['GET'])
    def home():
        return "hello world!"

    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(port='5001',debug=True)