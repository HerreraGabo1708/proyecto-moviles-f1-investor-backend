import os

class Config:
    # Configuración de la base de datos con MySQL
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql://user:root@localhost/bd_f1_simulator')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Evitar advertencias innecesarias

    # Clave secreta para proteger las sesiones de la aplicación
    SECRET_KEY = os.getenv('SECRET_KEY', 'mi_clave_secreta')  # Debes cambiar esta clave en producción

    # Configuración para el entorno de desarrollo
    DEBUG = os.getenv('DEBUG', True)  # Establecer a False en producción

    # Otras configuraciones si las necesitas
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'mi_clave_jwt_secreta')
    UPLOAD_FOLDER = 'uploads'  # Carpeta para almacenar imágenes de pilotos, por ejemplo
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}  # Tipos de imágenes permitidas