from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.equipo import Equipo

equipos_bp = Blueprint('equipos', __name__)


@equipos_bp.route('/', methods=['GET'])
@jwt_required()
def listar():
    temporada = request.args.get('temporada', type=int)
    activo = request.args.get('activo')
    jolpica_id = request.args.get('jolpica_id')
    search = request.args.get('search', '').strip()
    orden = request.args.get('orden', 'media')

    query = Equipo.query

    if temporada:
        query = query.filter_by(temporada=temporada)

    if jolpica_id:
        query = query.filter_by(jolpica_id=jolpica_id)

    if activo is not None:
        activo_bool = activo.lower() in ('true', '1', 'yes', 'si')
        query = query.filter_by(activo=activo_bool)

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Equipo.nombre.ilike(like),
                Equipo.nacionalidad.ilike(like)
            )
        )

    if orden == 'valor_mercado':
        query = query.order_by(Equipo.valor_mercado.desc())
    elif orden == 'nombre':
        query = query.order_by(Equipo.nombre.asc())
    elif orden == 'presupuesto':
        query = query.order_by(Equipo.presupuesto.desc())
    elif orden == 'temporada':
        query = query.order_by(Equipo.temporada.desc())
    else:
        query = query.order_by(Equipo.media.desc())

    equipos = query.all()

    return jsonify([equipo.to_dict() for equipo in equipos]), 200


@equipos_bp.route('/<int:equipo_id>', methods=['GET'])
@jwt_required()
def detalle(equipo_id):
    equipo = Equipo.query.get_or_404(equipo_id)
    return jsonify(equipo.to_dict()), 200


@equipos_bp.route('/jolpica/<string:jolpica_id>', methods=['GET'])
@jwt_required()
def detalle_por_jolpica_id(jolpica_id):
    equipo = Equipo.query.filter_by(jolpica_id=jolpica_id).first()

    if not equipo:
        return jsonify({
            'mensaje': 'Equipo no encontrado'
        }), 404

    return jsonify(equipo.to_dict()), 200


@equipos_bp.route('/', methods=['POST'])
@jwt_required()
def crear():
    data = request.get_json() or {}

    campos_permitidos = (
        'nombre',
        'jolpica_id',
        'nacionalidad',
        'temporada',
        'activo',
        'rendimiento_coche',
        'aerodinamica',
        'motor',
        'fiabilidad',
        'estrategia',
        'desarrollo',
        'media',
        'valor_mercado',
        'presupuesto',
        'imagen'
    )

    equipo_data = {
        campo: data[campo]
        for campo in campos_permitidos
        if campo in data
    }

    if 'nombre' not in equipo_data or not equipo_data['nombre']:
        return jsonify({
            'mensaje': 'El nombre del equipo es obligatorio'
        }), 400

    if 'jolpica_id' in equipo_data and equipo_data['jolpica_id']:
        existente = Equipo.query.filter_by(
            jolpica_id=equipo_data['jolpica_id']
        ).first()

        if existente:
            return jsonify({
                'mensaje': 'Ya existe un equipo con ese jolpica_id',
                'equipo': existente.to_dict()
            }), 409

    equipo = Equipo(**equipo_data)

    if hasattr(equipo, 'actualizar_media'):
        equipo.actualizar_media()

    db.session.add(equipo)
    db.session.commit()

    return jsonify(equipo.to_dict()), 201


@equipos_bp.route('/<int:equipo_id>', methods=['PUT'])
@jwt_required()
def actualizar(equipo_id):
    equipo = Equipo.query.get_or_404(equipo_id)
    data = request.get_json() or {}

    campos_actualizables = (
        'nombre',
        'jolpica_id',
        'nacionalidad',
        'temporada',
        'activo',
        'rendimiento_coche',
        'aerodinamica',
        'motor',
        'fiabilidad',
        'estrategia',
        'desarrollo',
        'media',
        'valor_mercado',
        'presupuesto',
        'imagen'
    )

    if 'jolpica_id' in data and data['jolpica_id']:
        existente = Equipo.query.filter(
            Equipo.jolpica_id == data['jolpica_id'],
            Equipo.id != equipo.id
        ).first()

        if existente:
            return jsonify({
                'mensaje': 'Ya existe otro equipo con ese jolpica_id'
            }), 409

    for campo in campos_actualizables:
        if campo in data:
            setattr(equipo, campo, data[campo])

    if hasattr(equipo, 'actualizar_media'):
        equipo.actualizar_media()

    db.session.commit()

    return jsonify(equipo.to_dict()), 200


@equipos_bp.route('/<int:equipo_id>', methods=['DELETE'])
@jwt_required()
def eliminar(equipo_id):
    equipo = Equipo.query.get_or_404(equipo_id)

    soft_delete = request.args.get('soft', 'true').lower() in ('true', '1', 'yes', 'si')

    if soft_delete:
        equipo.activo = False
        db.session.commit()

        return jsonify({
            'mensaje': 'Equipo desactivado correctamente',
            'equipo': equipo.to_dict()
        }), 200

    db.session.delete(equipo)
    db.session.commit()

    return jsonify({
        'mensaje': 'Equipo eliminado permanentemente'
    }), 200


@equipos_bp.route('/<int:equipo_id>/activar', methods=['PATCH'])
@jwt_required()
def activar(equipo_id):
    equipo = Equipo.query.get_or_404(equipo_id)

    equipo.activo = True
    db.session.commit()

    return jsonify({
        'mensaje': 'Equipo activado correctamente',
        'equipo': equipo.to_dict()
    }), 200