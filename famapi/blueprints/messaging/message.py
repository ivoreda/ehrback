from flask import request, jsonify, Blueprint
from flask_api import status
from famapi.models.message import Message
from famapi.models.user import User
from flask_jwt_extended import (current_user, jwt_required)
import json
from sqlalchemy import exc
from famapi.settings.database import SessionLocal

db = SessionLocal()

messages_bp = Blueprint('message', __name__)


@jwt_required()
@messages_bp.route('/messages', methods=["POST"])
def create_message():
    """ Registers a new user
    : request_body: contains json formatted data:
        message_content
    :return:
    """

    try:
        data = request.get_json()
        user = db.query(User).filter(User.id == current_user.id).first()

        if user:
            data["sender_id"] = current_user.id
            data["sender_type"] = user.account_type
            new_message = Message(**data)
            db.add(new_message)
            db.commit()
            db.refresh(new_message)
            return jsonify(new_message=json.loads(new_message.to_json())), status.HTTP_200_OK
        return jsonify(msg="Please Ensure you are logged in", error="User record doesnt exist"), \
            status.HTTP_400_BAD_REQUEST
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR


@jwt_required()
@messages_bp.route('/appointments/sender', methods=["GET"])
def get_user_sent_messages():
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if user:
            messages = db.query(Message).filter(Message.sender_id == current_user.id).all()

            data = [json.loads(message.to_json()) for message in messages]
            return jsonify(messages=data), status.HTTP_200_OK
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR

@jwt_required()
@messages_bp.route('/appointments/receiver', methods=["GET"])
def get_user_received_messages():
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if user:
            messages = db.query(Message).filter(Message.receiver_id == current_user.id).all()

            data = [json.loads(message.to_json()) for message in messages]
            return jsonify(messages=data), status.HTTP_200_OK
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR


@jwt_required()
@messages_bp.route('/messages/sent', methods=["GET"])
def get_all_sent_messages():
    try:
        messages = db.query(Message).filter(Message.sender_id.isnot(None)).all()
        data = [json.loads(message.to_json()) for message in messages]
        return jsonify(messages=data), status.HTTP_200_OK
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR

@jwt_required()
@messages_bp.route('/messages/received', methods=["GET"])
def get_all_received_messages():
    try:
        messages = db.query(Message).filter(Message.receiver_id.isnot(None)).all()
        data = [json.loads(message.to_json()) for message in messages]
        return jsonify(messages=data), status.HTTP_200_OK
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR


# @jwt_required()
# @messages_bp.route('/messages/<message_id>', methods=["DELETE"])
# def delete_message_by_id(message_id):
#     try:
#         message = db.query(Message).filter(Message.id == message_id)
#         db.delete(message)
#         db.commit()
#         return jsonify(message=json.loads(message.to_json())), status.HTTP_200_OK
#
#     except Exception as e:
#         return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR


@messages_bp.route('/messages/<message_id>', methods=["DELETE"])
def delete_message_by_id(message_id):
    try:
        message = db.query(Message).filter(Message.id == message_id)
        db.delete(message)
        db.commit()
        return jsonify(msg='Message has been successfully deleted'), status.HTTP_200_OK

    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR


@messages_bp.route('/messages/<message_id>', methods=["GET"])
def get_message_by_id(message_id):
    try:
        message = db.query(Message).filter(Message.id == message_id)
        return jsonify(message=json.loads(message.to_json())), status.HTTP_200_OK
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR
