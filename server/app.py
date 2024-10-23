#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
# from server.resources.recipe_index import RecipeIndex

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        image_url = data.get('image_url')
        bio = data.get('bio')

        if not username or not password:
            return {'error': 'Username and password are required.'}, 422

        user = User(username=username, bio=bio, image_url=image_url)
        user.password_hash = password

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Username already exists.'}, 422

        session['user_id'] = user.id
        return {
            'id': user.id,
            'username': user.username,
            'image_url': user.image_url,
            'bio': user.bio
        }, 201


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        user = db.session.get(User, user_id)
        if user:
            return user.to_dict(only=('id', 'username', 'image_url', 'bio')), 200
        return {'error': 'User not found'}, 404


class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()  # Fix the incorrect .session usage
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(only=('id', 'username', 'image_url', 'bio')), 200  # Return correct data
        return {'error': 'Invalid username or password'}, 401



# class Logout(Resource):
#     def delete(self):
#         if 'user_id' in session:
#             session.pop('user_id', None)
#             return {}, 204
#         return {'error': 'Unauthorized'}, 401
class Logout(Resource):
    def delete(self):
        if session.get('user_id') is None:
            return {'error': 'Unauthorized'}, 401  # Return 401 when no active session
        session.pop('user_id', None)
        return {}, 204



class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        recipes = Recipe.query.filter_by(user_id=user_id).all()
        return [recipe.to_dict() for recipe in recipes], 200

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        data = request.get_json()

        try:
            recipe = Recipe(
                title=data.get('title'),
                instructions=data.get('instructions'),
                minutes_to_complete=data.get('minutes_to_complete'),
                user_id=user_id
            )

            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201

        except ValueError as e:
            db.session.rollback()
            return {'error': str(e)}, 422


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)