import connexion
from famapi.settings.config import Config, TestConfig
from famapi.settings.extensions import jwt, storage
from famapi.blueprints.authentication.user_auth import auth_bp

from flask_cors import CORS
from mongoengine import connect
import os


def create_app():
    options = {'swagger_ui': True,
               'swagger_url': '/ui',
               'strict_validation': True,
               'validate_responses': True}

    connexion_app = connexion.FlaskApp(__name__, specification_dir="api/openapi", options=options)

    connexion_app.add_api("api.yaml")
    app = connexion_app.app
    CORS(app)
    app.config.from_object(Config)
    jwt.init_app(app)
    # storage.init_app(app)  # initialize google storage
    connect(host=os.environ.get('MONGODB_URI'))

    # add blueprints
    app.register_blueprint(tracker_usage_bp, url_prefix='/tracker')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(sub_bp)
    app.register_blueprint(notification_bp, url_prefix='/notifications')
    app.register_blueprint(payment_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(bookmark_bp)
    app.register_blueprint(rating_bp)
    app.register_blueprint(note_bp)
    app.register_blueprint(assessment_bp)

    return app
