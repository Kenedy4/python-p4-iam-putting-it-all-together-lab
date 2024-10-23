from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_only = ('id', 'username', 'image_url', 'bio')

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship('Recipe', backref='user', lazy=True)

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hash is not a readable attribute.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    @validates('username')
    def validate_username(self, key, username):
        assert username != '', "Username must not be empty."
        return username


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    serialize_only = ('id', 'title', 'instructions', 'minutes_to_complete', 'user')

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  

    @validates('title', 'instructions')
    def validate_recipe(self, key, value):
        if key == 'instructions' and len(value) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        if key == 'title' and value == '':
            raise ValueError("Title cannot be empty.")
        return value
