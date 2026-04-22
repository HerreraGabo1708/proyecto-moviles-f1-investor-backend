from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.carrera import Carrera
from app.services.simulacion import simular_carrera
from app.services.mercado    import actualizar_mercado

carreras_bp = Blueprint('carreras', __name__)


@carreras_bp.route('/', methods=['GET'])
@jwt_required()
def listar():
    return jsonify([c.to_dict() for c in Carrera.query.all()]), 200


@carreras_bp.route('/temporada/<int:temporada_id>', methods=['GET'])
@jwt_required()
def por_temporada(temporada_id):
    carreras = Carrera.query.filter_by(temporada_id=temporada_id).all()
    return jsonify([c.to_dict() for c in carreras]), 200


@carreras_bp.route('/<int:carrera_id>', methods=['GET'])
@jwt_required()
def detalle(carrera_id):
    carrera = Carrera.query.get_or_404(carrera_id)
    data    = carrera.to_dict()
    data['resultados'] = [r.to_dict() for r in carrera.resultados]
    return jsonify(data), 200


@carreras_bp.route('/', methods=['POST'])
@jwt_required()
def crear():
    data    = request.get_json()
    carrera = Carrera(
        temporada_id = data['temporada_id'],
        circuito_id  = data['circuito_id'],
        fecha        = data.get('fecha'),
    )
    db.session.add(carrera)
    db.session.commit()
    return jsonify(carrera.to_dict()), 201


@carreras_bp.route('/<int:carrera_id>/simular', methods=['POST'])
@jwt_required()
def simular(carrera_id):
    carrera = Carrera.query.get_or_404(carrera_id)
    if carrera.estado == 'completada':
        return jsonify({'error': 'Esta carrera ya fue simulada'}), 400

    resultados      = simular_carrera(carrera)
    actualizar_mercado(carrera)
    carrera.estado  = 'completada'
    db.session.commit()

    return jsonify({
        'mensaje':    'Carrera simulada correctamente',
        'resultados': [r.to_dict() for r in resultados],
    }), 200
