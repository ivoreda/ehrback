from time import time
from famapi.models.user import User
from sqlalchemy import exc
from flask_jwt_extended import (
    create_access_token, create_refresh_token
)

from flask import current_app
from flask import jsonify
from flask_api import status
from famapi.settings.extensions import jwt
from famapi.settings.database import SessionLocal

db = SessionLocal()


class Auth:
    """ Auth class
    """

    def __init__(self):
        """ Constructor
        """
        pass

    def register_user(self, data: dict) -> User:
        """ User registration
        """
        print("data here", data)
        if data:
            try:
                user = db.query(User).filter(User.email == data.get("email")).first()
                if user:
                    raise ValueError(f"User already exists")

                password = data.get("password")
                data.pop("password")
                user = User(**data)
                user.set_password(password)
                user.status = 1

                db.add(user)
                db.commit()
                db.refresh(user)
                return user
            except Exception as e:
                raise e

    def valid_login(self, email: str, password: str):
        """ Login validation
        """
        if not email or not password:
            return jsonify(msg="Email and password are required."), status.HTTP_400_BAD_REQUEST
        try:
            user = db.query(User).filter(User.email == email).first()
        except exc.NoResultFound as err:
            return jsonify(msg="User with email doesn't exist."), \
                status.HTTP_400_BAD_REQUEST

        if user.status == 0:
            return jsonify(msg="This account is deactivated."), status.HTTP_400_BAD_REQUEST

        if not user.verify_password(password):
            return jsonify(msg="Invalid email or password."), status.HTTP_400_BAD_REQUEST

        # login the user and update subscription last_logged_in time
        try:
            access_token = create_access_token(identity=str(user.id))
            user.authenticated = True

            db.add(user)
            db.commit()
            response = jsonify(msg="logged in successfully", data=access_token)
            return response
        except Exception as err:
            return jsonify(msg="An error occurred while logging in.",
                           data=str(err)), status.HTTP_500_INTERNAL_SERVER_ERROR

    def get_reset_password_token(self, email: str, expires_in=600):
        """ Get reset password token
        """
        try:
            user = db.query(User).filter(User.email == email).first()

            if user:
                jwt.encode_key_loader()
                token = jwt.encode(
                    {'reset_password': email, 'exp': time() + expires_in},
                    current_app.config['SECRET_KEY'], algorithm='HS256'
                )
                return token
        except exc.NoResultFound as e:
            return jsonify(msg=str(e)), status.HTTP_404_NOT_FOUND

    def suspend_account(self, email: str) -> None:
        """ Suspend a user account """
        try:
            user = db.query(User).filter(User.email == email).first()
            user.status = 2
            user.authenticated = False
            db.add(user)
            db.commit()
        except exc.NoResultFound:
            pass

    def delete_account(self, email: str) -> None:
        """ Delete a user account """
        try:
            user = db.query(User).filter(User.email == email).first()
            db.delete(user)
            db.commit()
        except exc.NoResultFound:
            pass

    def deactivate_account(self, email: str) -> None:
        """ Deactivate a user account """
        try:
            user = db.query(User).filter(User.email == email).first()
            user.status = 0
            db.add(user)
            db.commit()
        except exc.NoResultFound:
            pass

    def activate_account(self, email: str) -> None:
        """ Activate a user account """
        try:
            user = db.query(User).filter(User.email == email).first()
            user.status = 1
            db.add(user)
            db.commit()
        except exc.NoResultFound:
            return None
