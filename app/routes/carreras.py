from datetime import date, time

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app import db
from app.models.carrera import Carrera
from app.models.temporada import Temporada
from app.services.simulacion import simular_carrera

carreras_bp = Blueprint('carreras', __name__)


def _parse_date(value):
    if not value:
        return None

    if isinstance(value, date):
        return value

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _parse_time(value):
    if not value:
        return None

    if isinstance(value, time):
        return value

    try:
        clean_value = value.replace('Z', '')
        return time.fromisoformat(clean_value)
    except ValueError:
        return None


@carreras_bp.route('/', methods=['GET'])
@jwt_required()
def listar():
    temporada_id = request.args.get('temporada_id', type=int)
    temporada_anio = request.args.get('temporada_anio', type=int)
    circuito_id = request.args.get('circuito_id', type=int)
    estado = request.args.get('estado')
    jolpica_id = request.args.get('jolpica_id')
    round_number = request.args.get('round_number', type=int)
    orden = request.args.get('orden', 'fecha')

    query = Carrera.query

    if temporada_id:
        query = query.filter_by(temporada_id=temporada_id)

    if temporada_anio:
        query = query.filter_by(temporada_anio=temporada_anio)

    if circuito_id:
        query = query.filter_by(circuito_id=circuito_id)

    if estado:
        query = query.filter_by(estado=estado)

    if jolpica_id:
        query = query.filter_by(jolpica_id=jolpica_id)

    if round_number:
        query = query.filter_by(round_number=round_number)

    if orden == 'round':
        query = query.order_by(
            Carrera.temporada_anio.desc(),
            Carrera.round_number.asc()
        )
    elif orden == 'nombre':
        query = query.order_by(Carrera.nombre_gp.asc())
    elif orden == 'estado':
        query = query.order_by(Carrera.estado.asc())
    else:
        query = query.order_by(Carrera.fecha.asc())

    carreras = query.all()

    return jsonify([carrera.to_dict() for carrera in carreras]), 200


@carreras_bp.route('/temporada/<int:temporada_id>', methods=['GET'])
@jwt_required()
def por_temporada(temporada_id):
    carreras = Carrera.query.filter_by(
        temporada_id=temporada_id
    ).order_by(
        Carrera.round_number.asc()
    ).all()

    return jsonify([carrera.to_dict() for carrera in carreras]), 200


@carreras_bp.route('/temporada-anio/<int:temporada_anio>', methods=['GET'])
@jwt_required()
def por_temporada_anio(temporada_anio):
    carreras = Carrera.query.filter_by(
        temporada_anio=temporada_anio
    ).order_by(
        Carrera.round_number.asc()
    ).all()

    return jsonify([carrera.to_dict() for carrera in carreras]), 200


@carreras_bp.route('/jolpica/<string:jolpica_id>', methods=['GET'])
@jwt_required()
def detalle_por_jolpica_id(jolpica_id):
    carrera = Carrera.query.filter_by(jolpica_id=jolpica_id).first()

    if not carrera:
        return jsonify({
            'mensaje': 'Carrera no encontrada'
        }), 404

    return jsonify(carrera.to_dict()), 200

@carreras_bp.route('/simular-siguiente', methods=['POST'])
@jwt_required()
def simular_siguiente():
    data = request.get_json(silent=True) or {}

    recalcular_mercado = data.get('recalcular_mercado', True)
    limpiar_previos = data.get('limpiar_previos', True)

    temporada = Temporada.query.filter_by(activa=True).first()

    query = Carrera.query.filter_by(estado='pendiente')

    if temporada:
        query = query.filter_by(temporada_id=temporada.id)

    carrera = query.order_by(
        Carrera.round_number.asc(),
        Carrera.fecha.asc()
    ).first()

    if not carrera:
        return jsonify({
            'mensaje': 'No hay carreras pendientes para simular'
        }), 404

    resultados = simular_carrera(
        carrera=carrera,
        recalcular_mercado=recalcular_mercado,
        limpiar_previos=limpiar_previos
    )

    siguiente_carrera = Carrera.query.filter_by(
        estado='pendiente',
        temporada_id=carrera.temporada_id
    ).order_by(
        Carrera.round_number.asc(),
        Carrera.fecha.asc()
    ).first()

    return jsonify({
        'mensaje': 'Siguiente carrera simulada correctamente',
        'carrera_simulada': carrera.to_dict(),
        'siguiente_carrera': siguiente_carrera.to_dict() if siguiente_carrera else None,
        'resultados': [resultado.to_dict() for resultado in resultados],
    }), 200

@carreras_bp.route('/<int:carrera_id>', methods=['GET'])
@jwt_required()
def detalle(carrera_id):
    carrera = Carrera.query.get_or_404(carrera_id)

    data = carrera.to_dict()
    data['resultados'] = [
        resultado.to_dict()
        for resultado in carrera.resultados
    ]

    return jsonify(data), 200


@carreras_bp.route('/', methods=['POST'])
@jwt_required()
def crear():
    data = request.get_json() or {}

    if 'temporada_id' not in data:
        return jsonify({
            'mensaje': 'temporada_id es obligatorio'
        }), 400

    if 'circuito_id' not in data:
        return jsonify({
            'mensaje': 'circuito_id es obligatorio'
        }), 400

    temporada_anio = data.get('temporada_anio')
    round_number = data.get('round_number')

    jolpica_id = data.get('jolpica_id')

    if not jolpica_id and temporada_anio and round_number:
        jolpica_id = f"{temporada_anio}_{round_number}"

    if jolpica_id:
        existente = Carrera.query.filter_by(jolpica_id=jolpica_id).first()

        if existente:
            return jsonify({
                'mensaje': 'Ya existe una carrera con ese jolpica_id',
                'carrera': existente.to_dict()
            }), 409

    carrera = Carrera(
        temporada_id=data['temporada_id'],
        circuito_id=data['circuito_id'],

        jolpica_id=jolpica_id,
        temporada_anio=temporada_anio,
        round_number=round_number,
        nombre_gp=data.get('nombre_gp'),

        fecha=_parse_date(data.get('fecha')),
        hora=_parse_time(data.get('hora')),

        estado=data.get('estado', 'pendiente')
    )

    if hasattr(carrera, 'actualizar_estado_por_fecha'):
        carrera.actualizar_estado_por_fecha()

    db.session.add(carrera)
    db.session.commit()

    return jsonify(carrera.to_dict()), 201


@carreras_bp.route('/<int:carrera_id>', methods=['PUT'])
@jwt_required()
def actualizar(carrera_id):
    carrera = Carrera.query.get_or_404(carrera_id)
    data = request.get_json() or {}

    if 'jolpica_id' in data and data['jolpica_id']:
        existente = Carrera.query.filter(
            Carrera.jolpica_id == data['jolpica_id'],
            Carrera.id != carrera.id
        ).first()

        if existente:
            return jsonify({
                'mensaje': 'Ya existe otra carrera con ese jolpica_id'
            }), 409

    campos_directos = (
        'temporada_id',
        'circuito_id',
        'jolpica_id',
        'temporada_anio',
        'round_number',
        'nombre_gp',
        'estado'
    )

    for campo in campos_directos:
        if campo in data:
            setattr(carrera, campo, data[campo])

    if 'fecha' in data:
        carrera.fecha = _parse_date(data.get('fecha'))

    if 'hora' in data:
        carrera.hora = _parse_time(data.get('hora'))

    if not carrera.jolpica_id and carrera.temporada_anio and carrera.round_number:
        carrera.jolpica_id = f"{carrera.temporada_anio}_{carrera.round_number}"

    db.session.commit()

    return jsonify(carrera.to_dict()), 200


@carreras_bp.route('/<int:carrera_id>/simular', methods=['POST'])
@jwt_required()
def simular(carrera_id):
    carrera = Carrera.query.get_or_404(carrera_id)

    data = request.get_json(silent=True) or {}

    permitir_resimular = data.get('permitir_resimular', False)
    recalcular_mercado = data.get('recalcular_mercado', True)
    limpiar_previos = data.get('limpiar_previos', True)

    if carrera.estado == 'completada' and not permitir_resimular:
        return jsonify({
            'error': 'Esta carrera ya fue simulada',
            'detalle': 'Envie permitir_resimular=true si desea volver a simularla'
        }), 400

    resultados = simular_carrera(
        carrera=carrera,
        recalcular_mercado=recalcular_mercado,
        limpiar_previos=limpiar_previos
    )

    return jsonify({
        'mensaje': 'Carrera simulada correctamente',
        'carrera': carrera.to_dict(),
        'resultados': [resultado.to_dict() for resultado in resultados],
    }), 200





@carreras_bp.route('/<int:carrera_id>/marcar-pendiente', methods=['PATCH'])
@jwt_required()
def marcar_pendiente(carrera_id):
    carrera = Carrera.query.get_or_404(carrera_id)

    carrera.estado = 'pendiente'
    db.session.commit()

    return jsonify({
        'mensaje': 'Carrera marcada como pendiente',
        'carrera': carrera.to_dict()
    }), 200


@carreras_bp.route('/<int:carrera_id>/marcar-completada', methods=['PATCH'])
@jwt_required()
def marcar_completada(carrera_id):
    carrera = Carrera.query.get_or_404(carrera_id)

    carrera.estado = 'completada'
    db.session.commit()

    return jsonify({
        'mensaje': 'Carrera marcada como completada',
        'carrera': carrera.to_dict()
    }), 200


@carreras_bp.route('/<int:carrera_id>', methods=['DELETE'])
@jwt_required()
def eliminar(carrera_id):
    carrera = Carrera.query.get_or_404(carrera_id)

    db.session.delete(carrera)
    db.session.commit()

    return jsonify({
        'mensaje': 'Carrera eliminada correctamente'
    }), 200

@carreras_bp.route('/ultima-completada', methods=['GET'])
@jwt_required()
def ultima_completada():
    temporada = Temporada.query.filter_by(activa=True).first()

    query = Carrera.query.filter_by(estado='completada')

    if temporada:
        query = query.filter_by(temporada_id=temporada.id)

    carrera = query.order_by(
        Carrera.round_number.desc(),
        Carrera.fecha.desc()
    ).first()

    if not carrera:
        return jsonify({
            'mensaje': 'No hay carreras completadas',
            'carrera': None,
            'resultados': []
        }), 200

    resultados = sorted(
        carrera.resultados,
        key=lambda resultado: resultado.posicion or 999
    )

    return jsonify({
        'mensaje': 'Última carrera completada encontrada',
        'carrera': carrera.to_dict(),
        'resultados': [resultado.to_dict() for resultado in resultados],
    }), 200