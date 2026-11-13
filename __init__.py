from flask import Flask
from . import config
from .extensions import db, migrate
from dotenv import load_dotenv

load_dotenv()

def create_app(config_name: str) -> Flask:
    app = Flask(__name__)

    config_object = getattr(config, config_name)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)

    from .tasks import tasks_bp
    app.register_blueprint(tasks_bp)
    
    from . import models  # noqa: F401

    return app