from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app import db, bcrypt
from app.models.usuario import Usuario

usuarios_bp = Blueprint('usuarios', __name__)


def _obtener_data_json():
    return request.get_json(silent=True) or {}


def _normalizar_texto(valor):
    return str(valor or '').strip()


def _normalizar_correo(valor):
    return str(valor or '').strip().lower()


@usuarios_bp.route('/registro', methods=['POST'])
def registro():
    data = _obtener_data_json()

    nombre = _normalizar_texto(data.get('nombre'))
    correo = _normalizar_correo(data.get('correo'))
    password = _normalizar_texto(data.get('password'))

    if not nombre or not correo or not password:
        return jsonify({
            'exitoso': False,
            'mensaje': 'Debe ingresar nombre, correo y contraseña.'
        }), 400

    if len(password) < 6:
        return jsonify({
            'exitoso': False,
            'mensaje': 'La contraseña debe tener al menos 6 caracteres.'
        }), 400

    usuario_existente = Usuario.query.filter_by(correo=correo).first()

    if usuario_existente:
        return jsonify({
            'exitoso': False,
            'mensaje': 'El correo ya está registrado.'
        }), 409

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    usuario = Usuario(
        nombre=nombre,
        correo=correo,
        password=password_hash,
        capital=data.get('capital', 1_000_000.0),
    )

    db.session.add(usuario)
    db.session.commit()

    token = create_access_token(identity=str(usuario.id))

    return jsonify({
        'exitoso': True,
        'mensaje': 'Usuario registrado correctamente.',
        'token': token,
        'usuario': usuario.to_dict()
    }), 201


@usuarios_bp.route('/login', methods=['POST'])
def login():
    data = _obtener_data_json()

    correo = _normalizar_correo(data.get('correo'))
    password = _normalizar_texto(data.get('password'))

    if not correo or not password:
        return jsonify({
            'exitoso': False,
            'mensaje': 'Debe ingresar correo y contraseña.'
        }), 400

    usuario = Usuario.query.filter_by(correo=correo).first()

    if not usuario or not bcrypt.check_password_hash(usuario.password, password):
        return jsonify({
            'exitoso': False,
            'mensaje': 'Credenciales inválidas.'
        }), 401

    token = create_access_token(identity=str(usuario.id))

    return jsonify({
        'exitoso': True,
        'mensaje': 'Inicio de sesión exitoso.',
        'token': token,
        'usuario': usuario.to_dict()
    }), 200


@usuarios_bp.route('/perfil', methods=['GET'])
@jwt_required()
def perfil():
    uid = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)

    return jsonify({
        'exitoso': True,
        'usuario': usuario.to_dict()
    }), 200


@usuarios_bp.route('/perfil', methods=['PUT'])
@jwt_required()
def actualizar_perfil():
    uid = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)
    data = _obtener_data_json()

    nombre = _normalizar_texto(data.get('nombre'))

    if not nombre:
        return jsonify({
            'exitoso': False,
            'mensaje': 'El nombre es requerido.'
        }), 400

    usuario.nombre = nombre

    db.session.commit()

    return jsonify({
        'exitoso': True,
        'mensaje': 'Perfil actualizado correctamente.',
        'usuario': usuario.to_dict()
    }), 200


@usuarios_bp.route('/cambiar-password', methods=['PUT'])
@jwt_required()
def cambiar_password():
    uid = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)
    data = _obtener_data_json()

    password_actual = _normalizar_texto(data.get('password_actual'))
    password_nuevo = _normalizar_texto(data.get('password_nuevo'))

    if not password_actual or not password_nuevo:
        return jsonify({
            'exitoso': False,
            'mensaje': 'Debe ingresar la contraseña actual y la nueva contraseña.'
        }), 400

    if not bcrypt.check_password_hash(usuario.password, password_actual):
        return jsonify({
            'exitoso': False,
            'mensaje': 'La contraseña actual es incorrecta.'
        }), 401

    if len(password_nuevo) < 6:
        return jsonify({
            'exitoso': False,
            'mensaje': 'La nueva contraseña debe tener al menos 6 caracteres.'
        }), 400

    usuario.password = bcrypt.generate_password_hash(password_nuevo).decode('utf-8')

    db.session.commit()

    return jsonify({
        'exitoso': True,
        'mensaje': 'Contraseña actualizada correctamente.'
    }), 200