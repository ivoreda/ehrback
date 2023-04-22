from flask_mail import Mail
from flask_jwt_extended import JWTManager, decode_token
from flask_cors import CORS
from flask_googlestorage import GoogleStorage, Bucket

files = Bucket("files")
storage = GoogleStorage(files)
mail = Mail()
jwt = JWTManager()
Cors_app = CORS()



def security_handler(token):
    return decode_token(token)
