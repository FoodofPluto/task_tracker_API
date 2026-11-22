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
    print("create_app called, app:", app.name)
    migrate.init_app(app, db)

    with app.app_context():
        print("DB URL at startup:", db.engine.url)

    from . import models  # noqa: F401
    from .tasks.main import main_bp
    from .tasks.auth import auth_bp
    from .tasks.auth import tasks_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)

    return app
