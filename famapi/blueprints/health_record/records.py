from flask import request, jsonify, Blueprint
from flask_api import status
from famapi.models.health_record import Health_Records
from famapi.models.appointment import Appointment
from famapi.models.user import User
from flask_jwt_extended import (current_user, jwt_required)
import json
import datetime
from sqlalchemy import exc
from famapi.settings.database import SessionLocal

db = SessionLocal()

records_bp = Blueprint('record', __name__)


@jwt_required()
@records_bp.route('/health_records', methods=["POST"])
def create_record():
    """ Create a new health record
    : request_body: contains json formatted data:
    patient_id, doctor_id, appointment_id, description
    :return:
    """

    try:
        data = request.get_json()
        patient_id = data["patient_id"]
        doctor_id = data["doctor_id"]
        check_appointment = db.query(Appointment).filter(Appointment.doctor_id == doctor_id,
                                                         Appointment.patient_id == patient_id).first()

        if check_appointment:
            data["record_date"] = datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')
            new_record = Health_Records(**data)
            db.add(new_record)
            db.commit()
            db.refresh(new_record)
            return jsonify(new_message=json.loads(new_record.to_json())), status.HTTP_200_OK
        return jsonify(error="Appointment record doesnt exist"), \
            status.HTTP_400_BAD_REQUEST
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR


@records_bp.route('/health_records/<patient_id>', methods=["GET"])
def get_patient_records(patient_id):
    try:
        patient_records = db.query(Health_Records).filter(Health_Records.patient_id == patient_id).all()

        data = [json.loads(record.to_json()) for record in patient_records]
        return jsonify(patient_records=data), status.HTTP_200_OK
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR


@jwt_required()
@records_bp.route('/health_records/<doctor_id>', methods=["GET"])
def get_dr_records(doctor_id):
    try:
        doctor_records = db.query(Health_Records).filter(Health_Records.doctor_id == doctor_id).all()
        data = [json.loads(record.to_json()) for record in doctor_records]
        return jsonify(dr_records=data), status.HTTP_200_OK
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR


@jwt_required()
def get_all_records():
    try:
        records = db.query(Health_Records).all()
        data = [json.loads(record.to_json()) for record in records]
        return jsonify(records=data), status.HTTP_200_OK
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR

