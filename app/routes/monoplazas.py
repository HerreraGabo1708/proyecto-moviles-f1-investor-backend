from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app import db
from app.models.monoplaza import Monoplaza
from app.models.equipo import Equipo

monoplazas_bp = Blueprint('monoplazas', __name__)


@monoplazas_bp.route('/', methods=['GET'])
@jwt_required()
def listar():
    piloto_id = request.args.get('piloto_id', type=int)
    equipo_id = request.args.get('equipo_id', type=int)
    temporada_id = request.args.get('temporada_id', type=int)
    activo = request.args.get('activo')
    orden = request.args.get('orden', 'media')

    query = Monoplaza.query

    if piloto_id:
        query = query.filter_by(piloto_id=piloto_id)

    if equipo_id:
        query = query.filter_by(equipo_id=equipo_id)

    if temporada_id:
        query = query.filter_by(temporada_id=temporada_id)

    if activo is not None:
        activo_bool = activo.lower() in ('true', '1', 'yes', 'si')
        query = query.filter_by(activo=activo_bool)

    if orden == 'velocidad_punta':
        query = query.order_by(Monoplaza.velocidad_punta.desc())
    elif orden == 'aerodinamica':
        query = query.order_by(Monoplaza.aerodinamica.desc())
    elif orden == 'fiabilidad':
        query = query.order_by(Monoplaza.fiabilidad.desc())
    elif orden == 'nombre':
        query = query.order_by(Monoplaza.nombre.asc())
    else:
        query = query.order_by(Monoplaza.media.desc())

    monoplazas = query.all()

    return jsonify([monoplaza.to_dict() for monoplaza in monoplazas]), 200


@monoplazas_bp.route('/<int:mono_id>', methods=['GET'])
@jwt_required()
def detalle(mono_id):
    monoplaza = Monoplaza.query.get_or_404(mono_id)
    return jsonify(monoplaza.to_dict()), 200


@monoplazas_bp.route('/piloto/<int:piloto_id>', methods=['GET'])
@jwt_required()
def por_piloto(piloto_id):
    temporada_id = request.args.get('temporada_id', type=int)
    activo = request.args.get('activo', 'true').lower() in ('true', '1', 'yes', 'si')

    query = Monoplaza.query.filter_by(piloto_id=piloto_id)

    if temporada_id:
        query = query.filter_by(temporada_id=temporada_id)

    query = query.filter_by(activo=activo)

    monoplaza = query.first()

    if not monoplaza:
        return jsonify({
            'mensaje': 'No se encontro monoplaza para ese piloto'
        }), 404

    return jsonify(monoplaza.to_dict()), 200


@monoplazas_bp.route('/equipo/<int:equipo_id>', methods=['GET'])
@jwt_required()
def por_equipo(equipo_id):
    temporada_id = request.args.get('temporada_id', type=int)
    activo = request.args.get('activo')

    query = Monoplaza.query.filter_by(equipo_id=equipo_id)

    if temporada_id:
        query = query.filter_by(temporada_id=temporada_id)

    if activo is not None:
        activo_bool = activo.lower() in ('true', '1', 'yes', 'si')
        query = query.filter_by(activo=activo_bool)

    monoplazas = query.order_by(Monoplaza.media.desc()).all()

    return jsonify([monoplaza.to_dict() for monoplaza in monoplazas]), 200


@monoplazas_bp.route('/', methods=['POST'])
@jwt_required()
def crear():
    data = request.get_json() or {}

    campos_permitidos = (
        'piloto_id',
        'equipo_id',
        'temporada_id',

        'nombre',
        'codigo_modelo',

        'velocidad_punta',
        'aceleracion',
        'aerodinamica',
        'fiabilidad',
        'desgaste_neumaticos',
        'media',

        'activo',
        'foto'
    )

    monoplaza_data = {
        campo: data[campo]
        for campo in campos_permitidos
        if campo in data
    }

    monoplaza = Monoplaza(**monoplaza_data)

    if hasattr(monoplaza, 'actualizar_media'):
        monoplaza.actualizar_media()

    db.session.add(monoplaza)
    db.session.commit()

    return jsonify(monoplaza.to_dict()), 201


@monoplazas_bp.route('/desde-equipo', methods=['POST'])
@jwt_required()
def crear_desde_equipo():
    data = request.get_json() or {}

    equipo_id = data.get('equipo_id')
    temporada_id = data.get('temporada_id')
    piloto_id = data.get('piloto_id')

    if not equipo_id:
        return jsonify({
            'mensaje': 'equipo_id es obligatorio'
        }), 400

    equipo = Equipo.query.get_or_404(equipo_id)

    monoplaza = Monoplaza.crear_desde_equipo(
        equipo=equipo,
        temporada_id=temporada_id,
        piloto_id=piloto_id
    )

    if data.get('nombre'):
        monoplaza.nombre = data.get('nombre')

    if data.get('codigo_modelo'):
        monoplaza.codigo_modelo = data.get('codigo_modelo')

    if data.get('foto'):
        monoplaza.foto = data.get('foto')

    db.session.add(monoplaza)
    db.session.commit()

    return jsonify({
        'mensaje': 'Monoplaza creado desde equipo correctamente',
        'monoplaza': monoplaza.to_dict()
    }), 201


@monoplazas_bp.route('/<int:mono_id>', methods=['PUT'])
@jwt_required()
def actualizar(mono_id):
    monoplaza = Monoplaza.query.get_or_404(mono_id)
    data = request.get_json() or {}

    campos_actualizables = (
        'piloto_id',
        'equipo_id',
        'temporada_id',

        'nombre',
        'codigo_modelo',

        'velocidad_punta',
        'aceleracion',
        'aerodinamica',
        'fiabilidad',
        'desgaste_neumaticos',
        'media',

        'activo',
        'foto'
    )

    for campo in campos_actualizables:
        if campo in data:
            setattr(monoplaza, campo, data[campo])

    if hasattr(monoplaza, 'actualizar_media') and 'media' not in data:
        monoplaza.actualizar_media()

    db.session.commit()

    return jsonify(monoplaza.to_dict()), 200


@monoplazas_bp.route('/<int:mono_id>/mejorar', methods=['PATCH'])
@jwt_required()
def mejorar(mono_id):
    monoplaza = Monoplaza.query.get_or_404(mono_id)
    data = request.get_json() or {}

    tipo_mejora = data.get('tipo_mejora')
    incremento = data.get('incremento')

    if not tipo_mejora:
        return jsonify({
            'mensaje': 'tipo_mejora es obligatorio'
        }), 400

    try:
        incremento = float(incremento)
    except (ValueError, TypeError):
        return jsonify({
            'mensaje': 'incremento debe ser numerico'
        }), 400

    try:
        monoplaza.aplicar_mejora(
            tipo_mejora=tipo_mejora,
            incremento=incremento
        )

        db.session.commit()

        return jsonify({
            'mensaje': 'Mejora aplicada al monoplaza correctamente',
            'monoplaza': monoplaza.to_dict()
        }), 200

    except ValueError as error:
        db.session.rollback()

        return jsonify({
            'error': str(error)
        }), 400


@monoplazas_bp.route('/<int:mono_id>/activar', methods=['PATCH'])
@jwt_required()
def activar(mono_id):
    monoplaza = Monoplaza.query.get_or_404(mono_id)

    monoplaza.activo = True
    db.session.commit()

    return jsonify({
        'mensaje': 'Monoplaza activado correctamente',
        'monoplaza': monoplaza.to_dict()
    }), 200


@monoplazas_bp.route('/<int:mono_id>/desactivar', methods=['PATCH'])
@jwt_required()
def desactivar(mono_id):
    monoplaza = Monoplaza.query.get_or_404(mono_id)

    monoplaza.activo = False
    db.session.commit()

    return jsonify({
        'mensaje': 'Monoplaza desactivado correctamente',
        'monoplaza': monoplaza.to_dict()
    }), 200


@monoplazas_bp.route('/<int:mono_id>', methods=['DELETE'])
@jwt_required()
def eliminar(mono_id):
    monoplaza = Monoplaza.query.get_or_404(mono_id)

    soft_delete = request.args.get('soft', 'true').lower() in ('true', '1', 'yes', 'si')

    if soft_delete:
        monoplaza.activo = False
        db.session.commit()

        return jsonify({
            'mensaje': 'Monoplaza desactivado correctamente',
            'monoplaza': monoplaza.to_dict()
        }), 200

    db.session.delete(monoplaza)
    db.session.commit()

    return jsonify({
        'mensaje': 'Monoplaza eliminado permanentemente'
    }), 200