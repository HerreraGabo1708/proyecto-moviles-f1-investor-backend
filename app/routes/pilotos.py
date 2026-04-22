from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.piloto import Piloto

pilotos_bp = Blueprint('pilotos', __name__)


@pilotos_bp.route('/', methods=['GET'])
@jwt_required()
def listar():
    equipo_id = request.args.get('equipo_id', type=int)
    orden     = request.args.get('orden', 'media')   # media | valor_mercado
    query     = Piloto.query
    if equipo_id:
        query = query.filter_by(equipo_id=equipo_id)
    if orden == 'valor_mercado':
        query = query.order_by(Piloto.valor_mercado.desc())
    else:
        query = query.order_by(Piloto.media.desc())
    return jsonify([p.to_dict() for p in query.all()]), 200


@pilotos_bp.route('/<int:piloto_id>', methods=['GET'])
@jwt_required()
def detalle(piloto_id):
    return jsonify(Piloto.query.get_or_404(piloto_id).to_dict()), 200


@pilotos_bp.route('/', methods=['POST'])
@jwt_required()
def crear():
    data   = request.get_json()
    piloto = Piloto(**{k: data[k] for k in (
        'nombre','numero','edad','equipo_id','skill','consistencia',
        'racecraft','experiencia','potencial','media','valor_mercado','forma_actual','foto'
    ) if k in data})
    db.session.add(piloto)
    db.session.commit()
    return jsonify(piloto.to_dict()), 201


@pilotos_bp.route('/<int:piloto_id>', methods=['PUT'])
@jwt_required()
def actualizar(piloto_id):
    piloto = Piloto.query.get_or_404(piloto_id)
    data   = request.get_json()
    for campo in ('nombre','numero','edad','equipo_id','skill','consistencia',
                  'racecraft','experiencia','potencial','media',
                  'valor_mercado','forma_actual','foto'):
        if campo in data:
            setattr(piloto, campo, data[campo])
    db.session.commit()
    return jsonify(piloto.to_dict()), 200


@pilotos_bp.route('/<int:piloto_id>', methods=['DELETE'])
@jwt_required()
def eliminar(piloto_id):
    piloto = Piloto.query.get_or_404(piloto_id)
    db.session.delete(piloto)
    db.session.commit()
    return jsonify({'mensaje': 'Piloto eliminado'}), 200
