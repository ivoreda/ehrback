import datetime
from sqlalchemy import (
    DateTime, ForeignKey, Column, Text, Date, MetaData, Integer
)
from famapi.settings.database import Base, SessionLocal
import json

db = SessionLocal()
metadata = MetaData()


class Health_Records(Base):
    __tablename__ = 'health_records'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("user.id"))
    doctor_id = Column(Integer, ForeignKey("user.id"))
    record_date = Column(Date)
    appointment_id = Column(Integer, ForeignKey("appointment.id"))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S'))

    def to_json(self):
        json_data = {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'record_date': self.record_date,
            'appointment_id': self.appointment_id,
            'description': self.description,
            'created_at': self.created_at
        }
        return json.dumps(json_data)
