from datetime import date

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app import db
from app.models.temporada import Temporada
from app.models.carrera import Carrera

temporadas_bp = Blueprint('temporadas', __name__)


def _parse_date(value):
    if not value:
        return None

    if isinstance(value, date):
        return value

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


@temporadas_bp.route('/', methods=['GET'])
@jwt_required()
def listar():
    activa = request.args.get('activa')
    estado = request.args.get('estado')
    sincronizada = request.args.get('sincronizada')
    anio = request.args.get('anio', type=int)
    orden = request.args.get('orden', 'anio_desc')

    query = Temporada.query

    if anio:
        query = query.filter_by(anio=anio)

    if activa is not None:
        activa_bool = activa.lower() in ('true', '1', 'yes', 'si')
        query = query.filter_by(activa=activa_bool)

    if sincronizada is not None:
        sincronizada_bool = sincronizada.lower() in ('true', '1', 'yes', 'si')
        query = query.filter_by(sincronizada=sincronizada_bool)

    if estado:
        query = query.filter_by(estado=estado)

    if orden == 'anio_asc':
        query = query.order_by(Temporada.anio.asc())
    else:
        query = query.order_by(Temporada.anio.desc())

    temporadas = query.all()

    return jsonify([temporada.to_dict() for temporada in temporadas]), 200


@temporadas_bp.route('/activa', methods=['GET'])
@jwt_required()
def activa():
    temporada = Temporada.query.filter_by(activa=True).first()

    if not temporada:
        return jsonify({
            'error': 'No hay temporada activa'
        }), 404

    data = temporada.to_dict()
    data['carreras'] = [
        carrera.to_dict()
        for carrera in sorted(
            temporada.carreras,
            key=lambda c: c.round_number or 0
        )
    ]

    return jsonify(data), 200


@temporadas_bp.route('/<int:temporada_id>', methods=['GET'])
@jwt_required()
def detalle(temporada_id):
    temporada = Temporada.query.get_or_404(temporada_id)

    data = temporada.to_dict()
    data['carreras'] = [
        carrera.to_dict()
        for carrera in sorted(
            temporada.carreras,
            key=lambda c: c.round_number or 0
        )
    ]

    return jsonify(data), 200


@temporadas_bp.route('/anio/<int:anio>', methods=['GET'])
@jwt_required()
def detalle_por_anio(anio):
    temporada = Temporada.query.filter_by(anio=anio).first()

    if not temporada:
        return jsonify({
            'mensaje': 'Temporada no encontrada'
        }), 404

    data = temporada.to_dict()
    data['carreras'] = [
        carrera.to_dict()
        for carrera in sorted(
            temporada.carreras,
            key=lambda c: c.round_number or 0
        )
    ]

    return jsonify(data), 200


@temporadas_bp.route('/', methods=['POST'])
@jwt_required()
def nueva():
    data = request.get_json() or {}

    if 'anio' not in data:
        return jsonify({
            'mensaje': 'El año de la temporada es obligatorio'
        }), 400

    anio = data.get('anio')

    existente = Temporada.query.filter_by(anio=anio).first()

    if existente:
        return jsonify({
            'mensaje': 'Ya existe una temporada con ese año',
            'temporada': existente.to_dict()
        }), 409

    activar_temporada = data.get('activa', True)

    if activar_temporada:
        Temporada.query.filter_by(activa=True).update({'activa': False})

    temporada = Temporada(
        anio=anio,
        activa=activar_temporada,
        fecha_inicio=_parse_date(data.get('fecha_inicio')),
        fecha_fin=_parse_date(data.get('fecha_fin')),
        jolpica_id=data.get('jolpica_id') or str(anio),
        sincronizada=data.get('sincronizada', False),
        estado=data.get('estado', 'pendiente')
    )

    if hasattr(temporada, 'actualizar_estado'):
        temporada.actualizar_estado()

    db.session.add(temporada)
    db.session.flush()

    circuito_ids = data.get('circuito_ids', [])

    for index, circuito_id in enumerate(circuito_ids, 1):
        carrera = Carrera(
            temporada_id=temporada.id,
            circuito_id=circuito_id,
            temporada_anio=temporada.anio,
            round_number=index,
            jolpica_id=f"{temporada.anio}_{index}",
            estado='pendiente'
        )

        db.session.add(carrera)

    db.session.commit()

    return jsonify(temporada.to_dict()), 201


@temporadas_bp.route('/<int:temporada_id>', methods=['PUT'])
@jwt_required()
def actualizar(temporada_id):
    temporada = Temporada.query.get_or_404(temporada_id)
    data = request.get_json() or {}

    if 'anio' in data:
        existente = Temporada.query.filter(
            Temporada.anio == data['anio'],
            Temporada.id != temporada.id
        ).first()

        if existente:
            return jsonify({
                'mensaje': 'Ya existe otra temporada con ese año'
            }), 409

        temporada.anio = data['anio']

    if 'activa' in data:
        activar_temporada = bool(data['activa'])

        if activar_temporada:
            Temporada.query.filter(
                Temporada.id != temporada.id,
                Temporada.activa == True
            ).update({'activa': False})

        temporada.activa = activar_temporada

    if 'fecha_inicio' in data:
        temporada.fecha_inicio = _parse_date(data.get('fecha_inicio'))

    if 'fecha_fin' in data:
        temporada.fecha_fin = _parse_date(data.get('fecha_fin'))

    campos_directos = (
        'jolpica_id',
        'sincronizada',
        'ultima_sincronizacion',
        'estado'
    )

    for campo in campos_directos:
        if campo in data:
            setattr(temporada, campo, data[campo])

    if hasattr(temporada, 'actualizar_estado') and 'estado' not in data:
        temporada.actualizar_estado()

    db.session.commit()

    return jsonify(temporada.to_dict()), 200


@temporadas_bp.route('/<int:temporada_id>/activar', methods=['PATCH'])
@jwt_required()
def activar_temporada(temporada_id):
    temporada = Temporada.query.get_or_404(temporada_id)

    Temporada.query.filter_by(activa=True).update({'activa': False})

    temporada.activa = True
    db.session.commit()

    return jsonify({
        'mensaje': 'Temporada activada correctamente',
        'temporada': temporada.to_dict()
    }), 200


@temporadas_bp.route('/<int:temporada_id>/desactivar', methods=['PATCH'])
@jwt_required()
def desactivar_temporada(temporada_id):
    temporada = Temporada.query.get_or_404(temporada_id)

    temporada.activa = False
    db.session.commit()

    return jsonify({
        'mensaje': 'Temporada desactivada correctamente',
        'temporada': temporada.to_dict()
    }), 200


@temporadas_bp.route('/avanzar', methods=['PUT'])
@jwt_required()
def avanzar():
    temporada = Temporada.query.filter_by(activa=True).first()

    if not temporada:
        return jsonify({
            'error': 'No hay temporada activa'
        }), 404

    pendientes = Carrera.query.filter_by(
        temporada_id=temporada.id,
        estado='pendiente'
    ).count()

    if pendientes:
        return jsonify({
            'advertencia': 'Aun hay carreras pendientes',
            'pendientes': pendientes
        }), 200

    temporada.activa = False
    temporada.estado = 'finalizada'

    nuevo_anio = temporada.anio + 1

    existente = Temporada.query.filter_by(anio=nuevo_anio).first()

    if existente:
        existente.activa = True

        if hasattr(existente, 'actualizar_estado'):
            existente.actualizar_estado()

        db.session.commit()

        return jsonify({
            'mensaje': 'Temporada existente activada',
            'temporada': existente.to_dict()
        }), 200

    nueva_temporada = Temporada(
        anio=nuevo_anio,
        activa=True,
        jolpica_id=str(nuevo_anio),
        sincronizada=False,
        estado='pendiente'
    )

    db.session.add(nueva_temporada)
    db.session.commit()

    return jsonify({
        'mensaje': 'Nueva temporada iniciada',
        'temporada': nueva_temporada.to_dict()
    }), 201


@temporadas_bp.route('/<int:temporada_id>', methods=['DELETE'])
@jwt_required()
def eliminar(temporada_id):
    temporada = Temporada.query.get_or_404(temporada_id)

    if temporada.carreras:
        return jsonify({
            'mensaje': 'No se puede eliminar una temporada con carreras asociadas'
        }), 400

    db.session.delete(temporada)
    db.session.commit()

    return jsonify({
        'mensaje': 'Temporada eliminada correctamente'
    }), 200