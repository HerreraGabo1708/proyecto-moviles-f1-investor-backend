from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.equipo import Equipo

equipos_bp = Blueprint('equipos', __name__)


@equipos_bp.route('/', methods=['GET'])
@jwt_required()
def listar():
    orden = request.args.get('orden', 'media')
    query = Equipo.query
    if orden == 'valor_mercado':
        query = query.order_by(Equipo.valor_mercado.desc())
    else:
        query = query.order_by(Equipo.media.desc())
    return jsonify([e.to_dict() for e in query.all()]), 200


@equipos_bp.route('/<int:equipo_id>', methods=['GET'])
@jwt_required()
def detalle(equipo_id):
    equipo = Equipo.query.get_or_404(equipo_id)
    data   = equipo.to_dict()
    data['pilotos'] = [p.to_dict() for p in equipo.pilotos]
    return jsonify(data), 200


@equipos_bp.route('/', methods=['POST'])
@jwt_required()
def crear():
    data   = request.get_json()
    equipo = Equipo(**{k: data[k] for k in (
        'nombre','rendimiento_coche','aerodinamica','motor','fiabilidad',
        'estrategia','desarrollo','media','valor_mercado','presupuesto','imagen'
    ) if k in data})
    db.session.add(equipo)
    db.session.commit()
    return jsonify(equipo.to_dict()), 201


@equipos_bp.route('/<int:equipo_id>', methods=['PUT'])
@jwt_required()
def actualizar(equipo_id):
    equipo = Equipo.query.get_or_404(equipo_id)
    data   = request.get_json()
    for campo in ('nombre','rendimiento_coche','aerodinamica','motor','fiabilidad',
                  'estrategia','desarrollo','media','valor_mercado','presupuesto','imagen'):
        if campo in data:
            setattr(equipo, campo, data[campo])
    db.session.commit()
    return jsonify(equipo.to_dict()), 200
