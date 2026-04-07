from app import create_app, db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Crear la instancia de la app Flask
app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Crear las tablas de la base de datos
    app.run(debug=True)  # Ejecutar la aplicación