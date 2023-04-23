from datetime import datetime
from flask import request, jsonify, Blueprint
from flask_api import status
from famapi.models.appointment import Appointment
from flask_jwt_extended import (current_user, jwt_required)
import json
from sqlalchemy import exc
from famapi.settings.database import SessionLocal

db = SessionLocal()

bookings_bp = Blueprint('bookings', __name__)

@jwt_required()
@bookings_bp.route('/appointments', methods=["POST"])
def create_appointment():
    """ Registers a new user
    : request_body: contains json formatted data:
       patient_id, doctor_id, appointment_date,
       patient_id, doctor_id, appointment_date, appointment_time, status
    :return:
    """

    try:
        data = request.get_json()
        doctor_id = data["doctor_id"]
        appointment_date = data["appointment_date"]
        check_appointment = db.query(Appointment).filter(Appointment.doctor_id == doctor_id,
                                                         Appointment.appointment_date == appointment_date).first()
        if not check_appointment:
            new_appointment = Appointment(**data)
            db.add(new_appointment)
            db.commit()
            db.refresh(new_appointment)
            return jsonify(appointment=json.loads(new_appointment.to_json())), status.HTTP_200_OK
        return jsonify(msg=f"No free booking for doctor wih id {doctor_id} "
                           f"on {appointment_date}"), status.HTTP_400_BAD_REQUEST
    except Exception as e:
        # raise e
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR

@jwt_required()
@bookings_bp.route('/appointments/doctor', methods=["GET"])
def get_dr_appointments():
    try:
        doctor_id = request.args.get("doctor_id")
        dr_appointments = db.query(Appointment).filter(Appointment.doctor_id == doctor_id).first()
        data = [json.loads(appointment.to_json()) for appointment in dr_appointments]
        return jsonify(dr_appointment=data), status.HTTP_200_OK
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR

@jwt_required()
@bookings_bp.route('/appointments/patient', methods=["GET"])
def get_patient_appointments():
    try:
        patient_id = request.args.get("patient_id")
        patient_appointments = db.query(Appointment).filter(Appointment.patient_id == patient_id).first()
        data = [json.loads(appointment.to_json()) for appointment in patient_appointments]
        return jsonify(patients_appointment=data), status.HTTP_200_OK
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR

@jwt_required()
@bookings_bp.route('/appointments', methods=["GET"])
def get_all_appointments():
    try:
        appointments = db.query(Appointment).filter().first()
        data = [json.loads(appointment.to_json()) for appointment in appointments]
        return jsonify(patients_appointment=data), status.HTTP_200_OK
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR


@jwt_required()
@bookings_bp.route('/appointments/expired', methods=["DELETE"])
def delete_past_appointments():
    try:
        past_appointments = db.query(Appointment).query.filter(Appointment.appointment_date < datetime.now()).all()
        for appointment in past_appointments:
            db.delete(appointment)
        db.commit()
        return jsonify(msg='Past appointments successfully deleted'), status.HTTP_200_OK
    except Exception as e:
        return jsonify(msg=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR
