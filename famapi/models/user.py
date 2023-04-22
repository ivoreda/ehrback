import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import (
    DateTime, String, ForeignKey, Column, Enum, MetaData, Integer, Boolean, LargeBinary, VARCHAR
)
import json
from famapi.settings.database import Base, SessionLocal
from bcrypt import hashpw, gensalt, checkpw

db = SessionLocal()
metadata = MetaData()

AccountType = (('Doctor', 'Doctor'),
               ('Patient', 'Patient'))

GenderType = (('Male', 'Male'),
              ('Female', 'Female'))


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    date_created = Column(VARCHAR(50), default=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    last_modified = Column(VARCHAR(50), default=datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S'))
    status = Column(Integer, default=0)  # 0:deactivated, 1:activated, 2:suspended, 3:deleted
    first_name = Column(VARCHAR(50))
    last_name = Column(VARCHAR(50))
    gender = Column(VARCHAR(50), Enum(*[g[0] for g in GenderType], name='gender_enum'), default="Male")
    phone_number = Column(VARCHAR(50))
    email = Column(VARCHAR(50), unique=True)
    password = Column(LargeBinary, nullable=False)
    is_logged_in = Column(Boolean, default=False)
    account_type = Column(VARCHAR(50), Enum(*[a[0] for a in AccountType], name='account_type_enum'))

    avatar = Column(VARCHAR(255))
    authenticated = Column(Boolean, default=False)

    country = Column(VARCHAR(50))
    country_code = Column(VARCHAR(50))
    state = Column(VARCHAR(50))
    city = Column(VARCHAR(50))
    about_me = Column(VARCHAR(255))

    # device_info = relationship("DeviceInfo", back_populates="user")

    def __init__(self, *args, **kwargs):
        """
        Constructor of the class
        :param args: list data
        :param kwargs: dict data
        """
        super(User, self).__init__(*args, **kwargs)

    def set_password(self, password):
        hashed_password = hashpw(password.encode("utf-8"), gensalt())
        self.password = hashed_password

    def verify_password(self, password):
        """ Validate a password
        """
        return checkpw(password.encode("utf-8"), self.password)

    def to_json(self):
        json_data = {
            'dateCreated': self.date_created,
            'lastModified': self.last_modified,
            'status': self.status,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'gender': self.gender,
            'phoneNumber': self.phone_number,
            'email': self.email,
            'isLoggedIn': self.is_logged_in,
            'accountType': self.account_type,
            'avatar': self.avatar,
            'authenticated': self.authenticated,
            'country': self.country,
            'country_code': self.country_code,
            'state': self.state,
            'city': self.city,
            'about_me': self.about_me
        }
        return json.dumps(json_data)