from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.monoplaza import Monoplaza

monoplazas_bp = Blueprint('monoplazas', __name__)


@monoplazas_bp.route('/', methods=['GET'])
@jwt_required()
def listar():
    return jsonify([m.to_dict() for m in Monoplaza.query.all()]), 200


@monoplazas_bp.route('/<int:mono_id>', methods=['GET'])
@jwt_required()
def detalle(mono_id):
    return jsonify(Monoplaza.query.get_or_404(mono_id).to_dict()), 200


@monoplazas_bp.route('/piloto/<int:piloto_id>', methods=['GET'])
@jwt_required()
def por_piloto(piloto_id):
    mono = Monoplaza.query.filter_by(piloto_id=piloto_id).first_or_404()
    return jsonify(mono.to_dict()), 200


@monoplazas_bp.route('/', methods=['POST'])
@jwt_required()
def crear():
    data = request.get_json()
    mono = Monoplaza(**{k: data[k] for k in (
        'piloto_id','equipo_id','velocidad_punta','aceleracion',
        'aerodinamica','fiabilidad','desgaste_neumaticos','foto'
    ) if k in data})
    db.session.add(mono)
    db.session.commit()
    return jsonify(mono.to_dict()), 201


@monoplazas_bp.route('/<int:mono_id>', methods=['PUT'])
@jwt_required()
def actualizar(mono_id):
    mono = Monoplaza.query.get_or_404(mono_id)
    data = request.get_json()
    for campo in ('piloto_id','equipo_id','velocidad_punta','aceleracion',
                  'aerodinamica','fiabilidad','desgaste_neumaticos','foto'):
        if campo in data:
            setattr(mono, campo, data[campo])
    db.session.commit()
    return jsonify(mono.to_dict()), 200
