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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    # Relationship to user links
    user_links = db.relationship('UserLink', backref='user_link_user', lazy=True)

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
            'is_admin': self.is_admin,  # Include admin status in token
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
            'id': str(self.id),
            'firstName': self.firstName,
            'lastName': self.lastName,
            'email': self.email,
            'image': self.image,
            'is_admin': self.is_admin,  # Include admin status
            'links': [link.to_dict() for link in self.user_links] if self.user_links else [],
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
    
    # Relationship to user links
    user_links = db.relationship('UserLink', backref='user_link_platform', lazy=True)
    
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
    
class UserLink(db.Model):
    __tablename__ = 'user_links'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    platform_id = db.Column(UUID(as_uuid=True), db.ForeignKey('platforms.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<UserLink user={self.user_id} platform={self.platform_id}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'platform_id': str(self.platform_id),
            'url': self.url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'platform': self.user_link_platform.to_dict() if self.user_link_platform else None
        }