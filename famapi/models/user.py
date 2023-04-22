import datetime
from mongoengine import *
from bcrypt import hashpw, gensalt, checkpw
from bson.binary import Binary

AccountType = (('Doctor', 'Doctor'),
               ('Patient', 'Patient'))

GenderType = (('Male', 'Male'),
              ('Female', 'Female'))


# is_authenticated(), is_active(), is_anonymous(), get_id()
class User(Document):
    dateCreated = StringField(default=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    lastModified = StringField(default=datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S'))
    status = IntField(default=0)  # 0:deactivated, 1:activated, 2:suspended, 3:deleted
    firstName = StringField()
    lastName = StringField()
    gender = StringField(choices=GenderType, default="Male")
    phoneNumber = StringField()
    # phone_number = StringField(required=True, regex=re.compile(r'^\d{11}$'))
    email = EmailField(required=True, unique=True)
    password = BinaryField(required=True)
    isLoggedIn = BooleanField(default=False)
    deviceInfo = ListField()  # [{deviceMacNumber:'386773874', timeLoggedIn:'894093', timeLoggedOut:'48995498',
    reset_token = StringField()
    accountType = StringField(choices=AccountType)

    avatar = FileField()
    authenticated = BooleanField(default=False)
    # deviceName:'iphone14'},{...}]
    # brought in from profile, location
    country = StringField()
    country_code = StringField()
    state = StringField()
    city = StringField()
    about_me = StringField()


    def __init__(self, *args, **kwargs):
        """
        Constructor cf class
        :param args: list data
        :param kwargs: dict data
        """
        super(User, self).__init__(*args, **kwargs)

    def set_password(self, password):
        hashed_password = hashpw(password.encode("utf-8"), gensalt())
        self.password = Binary(hashed_password)

    def verify_password(self, password):
        """ Validate a password
        """
        return checkpw(password.encode("utf-8"), self.password)
