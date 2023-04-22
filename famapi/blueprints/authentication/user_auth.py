from famapi.services.auth import Auth
from typing import Union
from flask import request, jsonify, Blueprint
from flask_api import status
from famapi.models.user import User
from flask import current_app
from famapi.services.email import Email


from flask_jwt_extended import (current_user, get_jti, jwt_required, get_jwt, unset_jwt_cookies,
                                unset_access_cookies, unset_refresh_cookies)
import json
from datetime import datetime
from famapi.settings.extensions import jwt
# from mongoengine import errors
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

AUTH = Auth()

auth_bp = Blueprint('user_auth', __name__)


@auth_bp.route('/register', methods=["POST"])
def register_user() -> Union[str, tuple]:  #
    """ Registers a new user
    : request_body: contains json formatted data:
        firstName, lastName, phoneNumber, email, password, accountType
    :return:
    """

    data = request.get_json()
    try:
        new_user = AUTH.register_user(data)
        if new_user:
            new_user.save()
            response_data = json.loads(new_user.to_json())
            del response_data["password"]
            return jsonify(msg="Registration successful", data=response_data), status.HTTP_201_CREATED

    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_400_BAD_REQUEST


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login user
    : request-body: email, password
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    return AUTH.valid_login(email, password)


@jwt_required()
@auth_bp.route("/logout", methods=["GET"])
def logout():
    """
    Logout the current user
    """
    try:
        user = current_user

        user.authenticated = False
        user.isLoggedIn = False
        user.save()

        response = jsonify(msg="logged out successfully")
        unset_jwt_cookies(response)

        return response, status.HTTP_200_OK
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR


# # change to send_reset_password_link():

@auth_bp.route("/send_reset_password_link", methods=["GET"])
def send_reset_password_link():
    """ Reset password
        request_body: email
        :returns payload
    """
    email = request.args.get("email")
    if email:
        try:
            with current_app.app_context():
                serializer = URLSafeTimedSerializer(current_app.config['JWT_SECRET_KEY'])
            token = serializer.dumps(email, salt='password-reset')

            # reset_url = f'{request.url}/auth/newpassword?email={email}&reset_token={token}'
            reset_url = f"{current_app.config['TEST_DEV_EMAIL']}/auth/newpassword?email={email}&reset_token={token}"
            new_email = Email(subject="Reset Your Password")
            return new_email.send_email_for_password_reset(recipients=email, data=reset_url)
        except Exception as e:
            return jsonify(msg=str(e)), status.HTTP_400_BAD_REQUEST
    return jsonify(msg="Email field missing")


# Endpoint to update password after reset link is clicked
@jwt_required()
@auth_bp.route("/reset_password", methods=["GET", "PUT"])
def reset_password():
    """
    reset users password
    :return:
    """
    try:
        password = request.json.get('password')
        confirm_password = request.json.get('confirm_password')
        reset_token = request.args.get('reset_token')
        with current_app.app_context():
            serializer = URLSafeTimedSerializer(current_app.config['JWT_SECRET_KEY'])
        email = serializer.loads(reset_token, salt='password-reset', max_age=3600)
        if reset_token and password and confirm_password:
            user = User.objects.get(email=email)
            if user:
                if password == confirm_password:
                    user.set_password(password)
                    user.save()
                    return jsonify(msg="Password Successfully Updated"), status.HTTP_200_OK
                else:
                    return jsonify(msg="Passwords do not match"), status.HTTP_400_BAD_REQUEST
            else:
                return jsonify(msg="User with credentials doesnt exist"), status.HTTP_400_BAD_REQUEST
        else:
            return jsonify(msg="Reset token or password missing"), status.HTTP_400_BAD_REQUEST
    except SignatureExpired:
        return jsonify(msg="Token has expired"), status.HTTP_400_BAD_REQUEST
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR


@jwt_required()
@auth_bp.route("/user", methods=["GET"])
def get_user():
    try:
        data = request.args
        email = data.get("email")
        user = User.objects.get(email=email)
        response_data = json.loads(user.to_json())

        del response_data["password"]
        return jsonify(data=response_data), status.HTTP_200_OK
    # except errors.DoesNotExist:
    #     return jsonify(error="User does not exist"), status.HTTP_400_BAD_REQUEST
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR


@jwt_required()
@auth_bp.route("/user", methods=["POST"])
def update_user():
    """
    updates a user records
    request-body: email, update: firstName, lastName,
    phoneNumber, gender, country, country_code, state, city, about_me
    :return: user info formatted data
    """
    try:
        data = request.get_json()
        email = data.get("email")
        user_account = User.objects.get(email=email)

        user_account.firstName = data.get("firstName")
        user_account.lastName = data.get("lastName")
        user_account.phoneNumber = data.get("phoneNumber")
        user_account.gender = data.get("gender")
        user_account.country = data.get("country")
        user_account.country_code = data.get("country_code")
        user_account.state = data.get("state")
        user_account.about_me = data.get("about_me")
        user_account.city = data.get("city")
        user_account.save()

        response_data = json.loads(user_account.to_json())

        del response_data["password"]

        return jsonify(data=response_data,
                       msg="Account has been updated successfully"), \
            status.HTTP_200_OK
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR


@jwt_required()
@auth_bp.route("/user/update_password", methods=["PUT"])
def update_password():
    """
    update a user password
    request body: old_password, new_password
    :return: a confirmation message
    """

    try:
        data = request.get_json()
        old_password = data.get("old_password")
        new_password = data["new_password"]

        user = User.objects.filter(id=current_user.id).first()
        if user.verify_password(old_password):
            user.set_password(new_password)
            return jsonify(msg="Password successfully updated"), status.HTTP_200_OK
    except Exception as e:
        return jsonify(error=str(e)), status.HTTP_400_BAD_REQUEST


@jwt_required()
@auth_bp.route("/delete_account", methods=["GET"])
def delete_account():
    try:
        email = request.args.get("email")
        AUTH.delete_account(email)
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR


@jwt_required()
@auth_bp.route("/suspend_account", methods=["PUT"])
def suspend_account():
    try:
        email = request.args.get("email")
        AUTH.suspend_account(email)
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR


@jwt_required()
@auth_bp.route("/deactivate_account", methods=["PUT"])
def deactivate_account():
    try:
        email = request.args.get("email")
        AUTH.deactivate_account(email)
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR


@jwt_required()
@auth_bp.route("/activate_account", methods=["PUT"])
def activate_account():
    try:
        email = request.args.get("email")
        AUTH.activate_account(email)
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR
