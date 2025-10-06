from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
import bcrypt
import jwt
import os
from datetime import timedelta


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)    
    firstName = db.Column(db.String(100), nullable=True)
    lastName = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    links = db.Column(ARRAY(db.String), default=list)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set the password"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        self.password = hashed.decode('utf-8')
    
    def check_password(self, password):
        """Check if the provided password matches the hashed password"""
        password_bytes = password.encode('utf-8')
        hashed_bytes = self.password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    def generate_token(self):
        """Generate JWT token for the user"""
        secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
        payload = {
            'user_id': str(self.id),
            'email': self.email,
            'exp': datetime.now(timezone.utc) + timedelta(hours=24),  # Token expires in 24 hours
            'iat': datetime.now(timezone.utc)
        }
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    @staticmethod
    def verify_token(token):
        """Verify JWT token and return user data"""
        try:
            secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None  # Token has expired
        except jwt.InvalidTokenError:
            return None  # Invalid token
    
    def to_dict(self):
        return {
            'id': self.id,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'email': self.email,
            'image': self.image,
            'links': self.links,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Platform(db.Model):
    __tablename__ = 'platforms'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)   
    name = db.Column(db.String(100), nullable=False)
    lightIcon = db.Column(db.String(255), nullable=False)
    darkIcon = db.Column(db.String(255), nullable=False)
    previewColor = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f'<Platform {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'lightIcon': self.lightIcon,
            'darkIcon': self.darkIcon,
            'previewColor': self.previewColor
        }