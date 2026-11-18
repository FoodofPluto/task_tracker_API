
from flask import Flask
from .extensions import db, migrate
from .main import main_bp
from .auth import auth_bp
from task_tracker import config

print("Loaded tasks.__init__, __name__:", __name__)

def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)

    config_class = config.config_map[config_name]
    app.config.from_object(config_class)
    print("DB URI:", app.config["SQLALCHEMY_DATABASE_URI"])

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app



