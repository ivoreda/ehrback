import connexion
from famapi.settings.config import Config, TestConfig
from famapi.settings.extensions import jwt, storage
from famapi.blueprints.authentication.user_auth import auth_bp
from famapi.blueprints.appointment.bookings import bookings_bp
from famapi.blueprints.health_record.records import records_bp
from famapi.blueprints.messaging.message import messages_bp
from flask_cors import CORS
from mongoengine import connect
import os


def create_app():
    options = {'swagger_ui': True,
               'swagger_url': '/ui',
               'strict_validation': True,
               'validate_responses': True}

    connexion_app = connexion.FlaskApp(__name__, specification_dir="famapi/openapi", options=options)

    connexion_app.add_api("api.yaml")
    app = connexion_app.app
    CORS(app)
    app.config.from_object(Config)
    jwt.init_app(app)


    # add blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(bookings_bp)
    app.register_blueprint(records_bp)
    app.register_blueprint(messages_bp)

    return app
