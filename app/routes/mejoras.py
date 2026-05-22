from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.usuario import Usuario
from app.models.equipo import Equipo
from app.models.mejora import Mejora

mejoras_bp = Blueprint('mejoras', __name__)

TIPOS_VALIDOS = {
    'motor',
    'aerodinamica',
    'fiabilidad',
    'estrategia',
    'desarrollo',
    'rendimiento_coche'
}


def _parse_float(value, default=None):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


@mejoras_bp.route('/', methods=['GET'])
@jwt_required()
def listar():
    equipo_id = request.args.get('equipo_id', type=int)
    temporada_id = request.args.get('temporada_id', type=int)
    estado = request.args.get('estado')
    aplicada = request.args.get('aplicada')
    tipo = request.args.get('tipo')
    orden = request.args.get('orden', 'fecha_desc')

    query = Mejora.query

    if equipo_id:
        query = query.filter_by(equipo_id=equipo_id)

    if temporada_id:
        query = query.filter_by(temporada_id=temporada_id)

    if estado:
        query = query.filter_by(estado=estado)

    if tipo:
        query = query.filter_by(tipo=tipo)

    if aplicada is not None:
        aplicada_bool = aplicada.lower() in ('true', '1', 'yes', 'si')
        query = query.filter_by(aplicada=aplicada_bool)

    if orden == 'fecha_asc':
        query = query.order_by(Mejora.fecha.asc())
    elif orden == 'costo':
        query = query.order_by(Mejora.costo.desc())
    elif orden == 'valor_agregado':
        query = query.order_by(Mejora.valor_agregado.desc())
    else:
        query = query.order_by(Mejora.fecha.desc())

    mejoras = query.all()

    return jsonify([mejora.to_dict() for mejora in mejoras]), 200


@mejoras_bp.route('/<int:mejora_id>', methods=['GET'])
@jwt_required()
def detalle(mejora_id):
    mejora = Mejora.query.get_or_404(mejora_id)
    return jsonify(mejora.to_dict()), 200


@mejoras_bp.route('/', methods=['POST'])
@jwt_required()
def aplicar():
    uid = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)
    data = request.get_json() or {}

    equipo_id = data.get('equipo_id')
    temporada_id = data.get('temporada_id')
    tipo = data.get('tipo')
    valor_agregado = _parse_float(data.get('valor_agregado', 5.0), 5.0)
    costo = _parse_float(data.get('costo', 10_000.0), 10_000.0)

    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    aplicar_ahora = data.get('aplicar_ahora', True)

    if not equipo_id:
        return jsonify({
            'error': 'equipo_id es obligatorio'
        }), 400

    if tipo not in TIPOS_VALIDOS:
        return jsonify({
            'error': f'Tipo invalido. Opciones: {sorted(TIPOS_VALIDOS)}'
        }), 400

    if valor_agregado <= 0:
        return jsonify({
            'error': 'valor_agregado debe ser mayor a cero'
        }), 400

    if costo <= 0:
        return jsonify({
            'error': 'costo debe ser mayor a cero'
        }), 400

    equipo = Equipo.query.get_or_404(equipo_id)

    if not usuario.tiene_capital_suficiente(costo):
        return jsonify({
            'error': 'Capital insuficiente',
            'capital_actual': usuario.capital,
            'costo': costo
        }), 400

    try:
        usuario.debitar_capital(costo)

        mejora = Mejora.crear_mejora(
            equipo_id=equipo_id,
            tipo=tipo,
            valor_agregado=valor_agregado,
            costo=costo,
            temporada_id=temporada_id,
            nombre=nombre,
            descripcion=descripcion
        )

        db.session.add(mejora)
        db.session.flush()

        if aplicar_ahora:
            mejora.aplicar()

        db.session.commit()

        return jsonify({
            'mensaje': 'Mejora aplicada correctamente' if aplicar_ahora else 'Mejora registrada correctamente',
            'capital_restante': usuario.capital,
            'equipo': equipo.to_dict(),
            'mejora': mejora.to_dict()
        }), 201

    except ValueError as error:
        db.session.rollback()

        return jsonify({
            'error': str(error)
        }), 400

    except Exception as error:
        db.session.rollback()

        return jsonify({
            'error': 'Error procesando la mejora',
            'detalle': str(error)
        }), 500


@mejoras_bp.route('/equipo/<int:equipo_id>', methods=['GET'])
@jwt_required()
def historial(equipo_id):
    estado = request.args.get('estado')

    query = Mejora.query.filter_by(equipo_id=equipo_id)

    if estado:
        query = query.filter_by(estado=estado)

    mejoras = query.order_by(Mejora.fecha.desc()).all()

    return jsonify([mejora.to_dict() for mejora in mejoras]), 200


@mejoras_bp.route('/<int:mejora_id>/aplicar', methods=['PATCH'])
@jwt_required()
def aplicar_pendiente(mejora_id):
    mejora = Mejora.query.get_or_404(mejora_id)

    try:
        mejora.aplicar()
        db.session.commit()

        return jsonify({
            'mensaje': 'Mejora aplicada correctamente',
            'mejora': mejora.to_dict(),
            'equipo': mejora.equipo.to_dict() if mejora.equipo else None
        }), 200

    except ValueError as error:
        db.session.rollback()

        return jsonify({
            'error': str(error)
        }), 400


@mejoras_bp.route('/<int:mejora_id>/cancelar', methods=['PATCH'])
@jwt_required()
def cancelar(mejora_id):
    mejora = Mejora.query.get_or_404(mejora_id)

    try:
        mejora.cancelar()
        db.session.commit()

        return jsonify({
            'mensaje': 'Mejora cancelada correctamente',
            'mejora': mejora.to_dict()
        }), 200

    except ValueError as error:
        db.session.rollback()

        return jsonify({
            'error': str(error)
        }), 400


@mejoras_bp.route('/<int:mejora_id>', methods=['DELETE'])
@jwt_required()
def eliminar(mejora_id):
    mejora = Mejora.query.get_or_404(mejora_id)

    if mejora.aplicada:
        return jsonify({
            'error': 'No se puede eliminar una mejora ya aplicada'
        }), 400

    db.session.delete(mejora)
    db.session.commit()

    return jsonify({
        'mensaje': 'Mejora eliminada correctamente'
    }), 200