import datetime
from sqlalchemy import (
    DateTime, ForeignKey, Column, Enum, MetaData, Integer, VARCHAR, Time
)
from famapi.settings.database import Base, SessionLocal
import json


db = SessionLocal()
metadata = MetaData()

SENDER = (('Patient', 'Patient'),
          ('Doctor', 'Doctor'))


class Message(Base):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey("user.id"))
    message_content = Column(VARCHAR(255))
    sender_type = Column(VARCHAR(20), Enum(*[a[0] for a in SENDER], name='sender_enum'))
    created_at = Column(DateTime, default=datetime.datetime.now())

    def to_json(self):
        json_data = {
            'id': self.id,
            'sender_id': self.sender_id,
            'doctor_id': self.doctor_id,
            'message_content': self.message_content,
            'sender_type': self.sender_type,
            'created_at': self.created_at
        }
        return json.dumps(json_data)
