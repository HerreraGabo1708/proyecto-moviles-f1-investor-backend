from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db, bcrypt
from app.models.usuario import Usuario

usuarios_bp = Blueprint('usuarios', __name__)


@usuarios_bp.route('/registro', methods=['POST'])
def registro():
    data = request.get_json()
    if not data or not all(k in data for k in ('nombre', 'correo', 'password')):
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    if Usuario.query.filter_by(correo=data['correo']).first():
        return jsonify({'error': 'El correo ya está registrado'}), 409

    hashed  = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    usuario = Usuario(
        nombre   = data['nombre'],
        correo   = data['correo'],
        password = hashed,
        capital  = data.get('capital', 1_000_000.0),
    )
    db.session.add(usuario)
    db.session.commit()
    return jsonify({'mensaje': 'Usuario registrado', 'usuario': usuario.to_dict()}), 201


@usuarios_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not all(k in data for k in ('correo', 'password')):
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    usuario = Usuario.query.filter_by(correo=data['correo']).first()
    if not usuario or not bcrypt.check_password_hash(usuario.password, data['password']):
        return jsonify({'error': 'Credenciales inválidas'}), 401

    token = create_access_token(identity=str(usuario.id))
    return jsonify({'token': token, 'usuario': usuario.to_dict()}), 200


@usuarios_bp.route('/perfil', methods=['GET'])
@jwt_required()
def perfil():
    uid     = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)
    return jsonify(usuario.to_dict()), 200


@usuarios_bp.route('/perfil', methods=['PUT'])
@jwt_required()
def actualizar_perfil():
    uid     = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)
    data    = request.get_json()

    if 'nombre' in data:
        usuario.nombre = data['nombre']
    if 'password' in data:
        usuario.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    db.session.commit()
    return jsonify({'mensaje': 'Perfil actualizado', 'usuario': usuario.to_dict()}), 200
