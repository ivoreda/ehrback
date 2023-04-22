from time import time
from famapi.models.user import User
# from mongoengine.errors import DoesNotExist
from flask_jwt_extended import (
    create_access_token, create_refresh_token
)

from flask import current_app
from flask import jsonify
from flask_api import status
from famapi.settings.extensions import jwt


class Auth:
    """ Auth class
    """

    def __init__(self):
        """ Constructor
        """

    def register_user(self, data: dict) -> User:
        """ User registration
        """
        if data:
            try:
                user = User.objects.get(email=data.get("email"))
                if user:
                    raise ValueError(f"User already exists")
            except DoesNotExist:
                password = data.get("password")
                data.pop("password")
                user = User(**data)
                user.set_password(password)
                user.status = 1
                user.save()
                return user

    def valid_login(self, email: str, password: str):
        """ Login validation
        """
        if not email or not password:
            return jsonify(msg="Email and password are required."), status.HTTP_400_BAD_REQUEST
        try:
            user = User.objects.get(email=email)
        except DoesNotExist as err:
            return jsonify(msg="User with email doesn't exist."), \
                status.HTTP_400_BAD_REQUEST

        # checks if user is not deactivated
        if user.status == 0:
            return jsonify(msg="This account is deactivated."), status.HTTP_400_BAD_REQUEST

        if not user.verify_password(password):
            return jsonify(msg="Invalid email or password."), status.HTTP_400_BAD_REQUEST

        # login the user and update subscription last_logged_in time
        try:
            access_token = create_access_token(identity=str(user.id))
            user.authenticated = True
            user.save()
            response = jsonify(msg="logged in successfully", data=access_token)
            return response
        except Exception as err:
            return jsonify(msg="An error occurred while logging in.",
                           data=str(err)), status.HTTP_500_INTERNAL_SERVER_ERROR

    def get_reset_password_token(self, email: str, expires_in=600):
        """ Get reset password token
        """
        try:
            user = User.objects.get(email=email)

            if user:
                jwt.encode_key_loader()
                token = jwt.encode(
                    {'reset_password': email, 'exp': time() + expires_in},
                    current_app.config['SECRET_KEY'], algorithm='HS256'
                )
                return token
        except DoesNotExist as e:
            return jsonify(msg=str(e)), status.HTTP_404_NOT_FOUND

    def suspend_account(self, email: str) -> None:
        """ Suspend a user account """
        try:
            user = User.objects.get(email=email)
            user.update(set__status=2)
            user.authenticated = False
        except DoesNotExist:
            pass

    def delete_account(self, email: str) -> None:
        """ Delete a user account """
        try:
            user = User.objects.get(email=email)
            user.delete()
        except DoesNotExist:
            pass

    def deactivate_account(self, email: str) -> None:
        """ Deactivate a user account """
        try:
            user = User.objects.get(email=email)
            user.update(set__status=0)
        except DoesNotExist:
            pass

    def activate_account(self, email: str) -> None:
        """ Activate a user account """
        try:
            user = User.objects.get(email=email)
            user.update(set__status=1)
        except DoesNotExist:
            return None
