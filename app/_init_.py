from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config

# Crear la instancia de la base de datos y de la migración
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Cargar la configuración

    # Inicializar la base de datos y migración
    db.init_app(app)
    migrate.init_app(app, db)

    return app