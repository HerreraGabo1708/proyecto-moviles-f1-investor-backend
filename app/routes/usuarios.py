from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app import db, bcrypt
from app.models.usuario import Usuario
from app.models.inversion import Inversion
from app.models.portfolio import Portfolio

usuarios_bp = Blueprint('usuarios', __name__)


@usuarios_bp.route('/registro', methods=['POST'])
def registro():
    data = request.get_json() or {}

    campos_requeridos = ('nombre', 'correo', 'password')

    if not all(campo in data and data[campo] for campo in campos_requeridos):
        return jsonify({
            'error': 'Faltan campos requeridos: nombre, correo y password'
        }), 400

    if Usuario.query.filter_by(correo=data['correo']).first():
        return jsonify({
            'error': 'El correo ya esta registrado'
        }), 409

    username = data.get('username')

    if username and Usuario.query.filter_by(username=username).first():
        return jsonify({
            'error': 'El username ya esta registrado'
        }), 409

    capital_inicial = float(data.get('capital_inicial', data.get('capital', 1_000_000.0)))

    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    usuario = Usuario(
        nombre=data['nombre'],
        username=username,
        correo=data['correo'],
        password=hashed,

        capital_inicial=capital_inicial,
        capital=capital_inicial,

        rol=data.get('rol', 'jugador'),
        activo=True
    )

    db.session.add(usuario)
    db.session.commit()

    return jsonify({
        'mensaje': 'Usuario registrado correctamente',
        'usuario': usuario.to_dict()
    }), 201


@usuarios_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    if not all(campo in data and data[campo] for campo in ('correo', 'password')):
        return jsonify({
            'error': 'Faltan campos requeridos: correo y password'
        }), 400

    usuario = Usuario.query.filter_by(correo=data['correo']).first()

    if not usuario or not bcrypt.check_password_hash(usuario.password, data['password']):
        return jsonify({
            'error': 'Credenciales invalidas'
        }), 401

    if not usuario.activo:
        return jsonify({
            'error': 'El usuario esta inactivo'
        }), 403

    usuario.actualizar_ultimo_acceso()
    db.session.commit()

    token = create_access_token(identity=str(usuario.id))

    return jsonify({
        'token': token,
        'usuario': usuario.to_dict()
    }), 200


@usuarios_bp.route('/perfil', methods=['GET'])
@jwt_required()
def perfil():
    uid = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)

    return jsonify(usuario.to_dict()), 200


@usuarios_bp.route('/perfil', methods=['PUT'])
@jwt_required()
def actualizar_perfil():
    uid = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)
    data = request.get_json() or {}

    if 'nombre' in data:
        usuario.nombre = data['nombre']

    if 'username' in data:
        nuevo_username = data['username']

        if nuevo_username:
            existente = Usuario.query.filter(
                Usuario.username == nuevo_username,
                Usuario.id != usuario.id
            ).first()

            if existente:
                return jsonify({
                    'error': 'El username ya esta registrado'
                }), 409

        usuario.username = nuevo_username

    if 'correo' in data:
        nuevo_correo = data['correo']

        existente = Usuario.query.filter(
            Usuario.correo == nuevo_correo,
            Usuario.id != usuario.id
        ).first()

        if existente:
            return jsonify({
                'error': 'El correo ya esta registrado'
            }), 409

        usuario.correo = nuevo_correo

    if 'password' in data and data['password']:
        usuario.password = bcrypt.generate_password_hash(
            data['password']
        ).decode('utf-8')

    db.session.commit()

    return jsonify({
        'mensaje': 'Perfil actualizado correctamente',
        'usuario': usuario.to_dict()
    }), 200


@usuarios_bp.route('/perfil/financiero', methods=['GET'])
@jwt_required()
def perfil_financiero():
    uid = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)

    inversiones = Inversion.query.filter_by(usuario_id=uid).all()
    portfolio = Portfolio.query.filter_by(usuario_id=uid, activo=True).all()

    total_compras = sum(
        inversion.monto
        for inversion in inversiones
        if inversion.tipo_operacion == 'compra'
    )

    total_ventas = sum(
        inversion.monto
        for inversion in inversiones
        if inversion.tipo_operacion == 'venta'
    )

    valor_portfolio = sum(
        item.valor_actual_total()
        for item in portfolio
    )

    patrimonio_total = round(usuario.capital + valor_portfolio, 2)
    ganancia_neta = round(patrimonio_total - usuario.capital_inicial, 2)

    rendimiento_porcentaje = 0.0

    if usuario.capital_inicial > 0:
        rendimiento_porcentaje = round(
            (ganancia_neta / usuario.capital_inicial) * 100,
            2
        )

    return jsonify({
        'usuario_id': usuario.id,
        'nombre': usuario.nombre,
        'username': usuario.username,
        'correo': usuario.correo,

        'capital_inicial': usuario.capital_inicial,
        'capital_actual': usuario.capital,
        'valor_portfolio': round(valor_portfolio, 2),
        'patrimonio_total': patrimonio_total,

        'ganancia_neta': ganancia_neta,
        'rendimiento_porcentaje': rendimiento_porcentaje,

        'total_compras': round(total_compras, 2),
        'total_ventas': round(total_ventas, 2),
        'cantidad_inversiones': len(inversiones),
        'cantidad_activos_portfolio': len(portfolio),
    }), 200


@usuarios_bp.route('/capital', methods=['PATCH'])
@jwt_required()
def actualizar_capital():
    uid = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)
    data = request.get_json() or {}

    if 'capital' not in data:
        return jsonify({
            'error': 'capital es obligatorio'
        }), 400

    try:
        nuevo_capital = float(data['capital'])
    except (ValueError, TypeError):
        return jsonify({
            'error': 'capital debe ser numerico'
        }), 400

    if nuevo_capital < 0:
        return jsonify({
            'error': 'capital no puede ser negativo'
        }), 400

    usuario.capital = nuevo_capital
    db.session.commit()

    return jsonify({
        'mensaje': 'Capital actualizado correctamente',
        'usuario': usuario.to_dict()
    }), 200


@usuarios_bp.route('/desactivar', methods=['PATCH'])
@jwt_required()
def desactivar_cuenta():
    uid = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)

    usuario.activo = False
    db.session.commit()

    return jsonify({
        'mensaje': 'Cuenta desactivada correctamente'
    }), 200