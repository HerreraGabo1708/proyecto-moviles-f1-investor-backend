from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.temporada import Temporada
from app.models.carrera   import Carrera

temporadas_bp = Blueprint('temporadas', __name__)


@temporadas_bp.route('/', methods=['GET'])
@jwt_required()
def listar():
    return jsonify([t.to_dict() for t in Temporada.query.all()]), 200


@temporadas_bp.route('/activa', methods=['GET'])
@jwt_required()
def activa():
    temporada = Temporada.query.filter_by(activa=True).first()
    if not temporada:
        return jsonify({'error': 'No hay temporada activa'}), 404
    data = temporada.to_dict()
    data['carreras'] = [c.to_dict() for c in temporada.carreras]
    return jsonify(data), 200


@temporadas_bp.route('/', methods=['POST'])
@jwt_required()
def nueva():
    data = request.get_json()
    Temporada.query.filter_by(activa=True).update({'activa': False})

    temporada = Temporada(
        anio         = data['anio'],
        activa       = True,
        fecha_inicio = data.get('fecha_inicio'),
        fecha_fin    = data.get('fecha_fin'),
    )
    db.session.add(temporada)
    db.session.flush()

    # Crear carreras si se pasan circuito_ids
    for cid in data.get('circuito_ids', []):
        db.session.add(Carrera(temporada_id=temporada.id, circuito_id=cid))

    db.session.commit()
    return jsonify(temporada.to_dict()), 201


@temporadas_bp.route('/avanzar', methods=['PUT'])
@jwt_required()
def avanzar():
    temporada = Temporada.query.filter_by(activa=True).first()
    if not temporada:
        return jsonify({'error': 'No hay temporada activa'}), 404

    pendientes = Carrera.query.filter_by(temporada_id=temporada.id, estado='pendiente').count()
    if pendientes:
        return jsonify({'advertencia': 'Aún hay carreras pendientes', 'pendientes': pendientes}), 200

    temporada.activa = False
    nueva = Temporada(anio=temporada.anio + 1, activa=True)
    db.session.add(nueva)
    db.session.commit()
    return jsonify({'mensaje': 'Nueva temporada iniciada', 'temporada': nueva.to_dict()}), 201
