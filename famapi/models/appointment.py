import datetime
from sqlalchemy import (
    DateTime, ForeignKey, Column, Enum, MetaData, Integer, VARCHAR, Time
)
from famapi.settings.database import Base, SessionLocal
import json


db = SessionLocal()
metadata = MetaData()

STATUS = (('Requested', 'Requested'),
          ('Approved', 'Approved'),
          ('Cancelled', 'Cancelled'))


class Appointment(Base):
    __tablename__ = 'appointment'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("user.id"))
    doctor_id = Column(Integer, ForeignKey("user.id"))
    appointment_date = Column(DateTime, default=datetime.datetime.now())
    appointment_time = Column(Time)
    status = Column(VARCHAR(20), Enum(*[a[0] for a in STATUS], name='status_enum'))
    created_at = Column(DateTime, default=datetime.datetime.now())

    def to_json(self):
        json_data = {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'status': self.status,
            'appointment_date': self.appointment_date,
            'appointment_time': self.appointment_time,
            'created_at': self.created_at
        }
        return json.dumps(json_data)

