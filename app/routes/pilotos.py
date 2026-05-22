from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.piloto import Piloto

pilotos_bp = Blueprint('pilotos', __name__)


@pilotos_bp.route('/', methods=['GET'])
@jwt_required()
def listar():
    equipo_id = request.args.get('equipo_id', type=int)
    temporada = request.args.get('temporada', type=int)
    activo = request.args.get('activo')
    jolpica_id = request.args.get('jolpica_id')
    search = request.args.get('search', '').strip()
    orden = request.args.get('orden', 'media')

    query = Piloto.query

    if equipo_id:
        query = query.filter_by(equipo_id=equipo_id)

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
                Piloto.nombre.ilike(like),
                Piloto.codigo.ilike(like),
                Piloto.nacionalidad.ilike(like)
            )
        )

    if orden == 'valor_mercado':
        query = query.order_by(Piloto.valor_mercado.desc())
    elif orden == 'forma_actual':
        query = query.order_by(Piloto.forma_actual.desc())
    elif orden == 'nombre':
        query = query.order_by(Piloto.nombre.asc())
    elif orden == 'temporada':
        query = query.order_by(Piloto.temporada.desc())
    else:
        query = query.order_by(Piloto.media.desc())

    pilotos = query.all()

    return jsonify([piloto.to_dict() for piloto in pilotos]), 200


@pilotos_bp.route('/<int:piloto_id>', methods=['GET'])
@jwt_required()
def detalle(piloto_id):
    piloto = Piloto.query.get_or_404(piloto_id)
    return jsonify(piloto.to_dict()), 200


@pilotos_bp.route('/jolpica/<string:jolpica_id>', methods=['GET'])
@jwt_required()
def detalle_por_jolpica_id(jolpica_id):
    piloto = Piloto.query.filter_by(jolpica_id=jolpica_id).first()

    if not piloto:
        return jsonify({
            'mensaje': 'Piloto no encontrado'
        }), 404

    return jsonify(piloto.to_dict()), 200


@pilotos_bp.route('/', methods=['POST'])
@jwt_required()
def crear():
    data = request.get_json() or {}

    campos_permitidos = (
        'nombre',
        'numero',
        'edad',
        'equipo_id',
        'jolpica_id',
        'codigo',
        'nacionalidad',
        'fecha_nacimiento',
        'temporada',
        'activo',
        'skill',
        'consistencia',
        'racecraft',
        'experiencia',
        'potencial',
        'media',
        'valor_mercado',
        'forma_actual',
        'foto'
    )

    piloto_data = {
        campo: data[campo]
        for campo in campos_permitidos
        if campo in data
    }

    if 'nombre' not in piloto_data or not piloto_data['nombre']:
        return jsonify({
            'mensaje': 'El nombre del piloto es obligatorio'
        }), 400

    if 'jolpica_id' in piloto_data and piloto_data['jolpica_id']:
        existente = Piloto.query.filter_by(
            jolpica_id=piloto_data['jolpica_id']
        ).first()

        if existente:
            return jsonify({
                'mensaje': 'Ya existe un piloto con ese jolpica_id',
                'piloto': existente.to_dict()
            }), 409

    piloto = Piloto(**piloto_data)

    if hasattr(piloto, 'actualizar_media'):
        piloto.actualizar_media()

    db.session.add(piloto)
    db.session.commit()

    return jsonify(piloto.to_dict()), 201


@pilotos_bp.route('/<int:piloto_id>', methods=['PUT'])
@jwt_required()
def actualizar(piloto_id):
    piloto = Piloto.query.get_or_404(piloto_id)
    data = request.get_json() or {}

    campos_actualizables = (
        'nombre',
        'numero',
        'edad',
        'equipo_id',
        'jolpica_id',
        'codigo',
        'nacionalidad',
        'fecha_nacimiento',
        'temporada',
        'activo',
        'skill',
        'consistencia',
        'racecraft',
        'experiencia',
        'potencial',
        'media',
        'valor_mercado',
        'forma_actual',
        'foto'
    )

    if 'jolpica_id' in data and data['jolpica_id']:
        existente = Piloto.query.filter(
            Piloto.jolpica_id == data['jolpica_id'],
            Piloto.id != piloto.id
        ).first()

        if existente:
            return jsonify({
                'mensaje': 'Ya existe otro piloto con ese jolpica_id'
            }), 409

    for campo in campos_actualizables:
        if campo in data:
            setattr(piloto, campo, data[campo])

    if hasattr(piloto, 'actualizar_media'):
        piloto.actualizar_media()

    db.session.commit()

    return jsonify(piloto.to_dict()), 200


@pilotos_bp.route('/<int:piloto_id>', methods=['DELETE'])
@jwt_required()
def eliminar(piloto_id):
    piloto = Piloto.query.get_or_404(piloto_id)

    soft_delete = request.args.get('soft', 'true').lower() in ('true', '1', 'yes', 'si')

    if soft_delete:
        piloto.activo = False
        db.session.commit()

        return jsonify({
            'mensaje': 'Piloto desactivado correctamente',
            'piloto': piloto.to_dict()
        }), 200

    db.session.delete(piloto)
    db.session.commit()

    return jsonify({
        'mensaje': 'Piloto eliminado permanentemente'
    }), 200


@pilotos_bp.route('/<int:piloto_id>/activar', methods=['PATCH'])
@jwt_required()
def activar(piloto_id):
    piloto = Piloto.query.get_or_404(piloto_id)

    piloto.activo = True
    db.session.commit()

    return jsonify({
        'mensaje': 'Piloto activado correctamente',
        'piloto': piloto.to_dict()
    }), 200