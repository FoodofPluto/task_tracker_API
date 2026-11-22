
from flask import Flask
from ..extensions import db, migrate
from .main import main_bp
from .auth import auth_bp
from .. import config

print("Loaded tasks.__init__, __name__:", __name__)



