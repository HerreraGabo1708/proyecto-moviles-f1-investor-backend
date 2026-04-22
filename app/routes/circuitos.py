from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.circuito import Circuito

circuitos_bp = Blueprint('circuitos', __name__)


@circuitos_bp.route('/', methods=['GET'])
@jwt_required()
def listar():
    return jsonify([c.to_dict() for c in Circuito.query.all()]), 200


@circuitos_bp.route('/<int:circuito_id>', methods=['GET'])
@jwt_required()
def detalle(circuito_id):
    return jsonify(Circuito.query.get_or_404(circuito_id).to_dict()), 200


@circuitos_bp.route('/', methods=['POST'])
@jwt_required()
def crear():
    data     = request.get_json()
    circuito = Circuito(**{k: data[k] for k in (
        'nombre_gp','nombre_circuito','pais','longitud','num_curvas',
        'tipo_pista','zonas_drs','nivel_tecnico','nivel_desgaste','nivel_sobrepaso','imagen'
    ) if k in data})
    db.session.add(circuito)
    db.session.commit()
    return jsonify(circuito.to_dict()), 201
