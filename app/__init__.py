from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS

db      = SQLAlchemy()
jwt     = JWTManager()
bcrypt  = Bcrypt()


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    from app.routes.usuarios    import usuarios_bp
    from app.routes.pilotos     import pilotos_bp
    from app.routes.equipos     import equipos_bp
    from app.routes.monoplazas  import monoplazas_bp
    from app.routes.circuitos   import circuitos_bp
    from app.routes.carreras    import carreras_bp
    from app.routes.inversiones import inversiones_bp
    from app.routes.mejoras     import mejoras_bp
    from app.routes.temporadas  import temporadas_bp
    from app.routes.dashboard   import dashboard_bp

    app.register_blueprint(usuarios_bp,    url_prefix='/api/usuarios')
    app.register_blueprint(pilotos_bp,     url_prefix='/api/pilotos')
    app.register_blueprint(equipos_bp,     url_prefix='/api/equipos')
    app.register_blueprint(monoplazas_bp,  url_prefix='/api/monoplazas')
    app.register_blueprint(circuitos_bp,   url_prefix='/api/circuitos')
    app.register_blueprint(carreras_bp,    url_prefix='/api/carreras')
    app.register_blueprint(inversiones_bp, url_prefix='/api/inversiones')
    app.register_blueprint(mejoras_bp,     url_prefix='/api/mejoras')
    app.register_blueprint(temporadas_bp,  url_prefix='/api/temporadas')
    app.register_blueprint(dashboard_bp,   url_prefix='/api/dashboard')

    return app
