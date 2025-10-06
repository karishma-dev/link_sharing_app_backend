from src.models.models import db

def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()

def get_db():
    """Get the database instance - much simpler now!"""
    return db