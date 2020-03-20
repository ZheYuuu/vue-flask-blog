from flask import Flask
from config import Config
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # enable CORS
    CORS(app)
    # Init FlaskAlchemy
    db.init_app(app)
    # Init FlaskMigrate
    migrate.init_app(app, db)

    # register blueprint
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

from app import models
from app.api import users,ping