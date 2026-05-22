from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app import db
from app.models.circuito import Circuito

circuitos_bp = Blueprint('circuitos', __name__)


@circuitos_bp.route('/', methods=['GET'])
@jwt_required()
def listar():
    pais = request.args.get('pais')
    tipo_pista = request.args.get('tipo_pista')
    activo = request.args.get('activo')
    jolpica_id = request.args.get('jolpica_id')
    search = request.args.get('search', '').strip()
    orden = request.args.get('orden', 'nombre_gp')

    query = Circuito.query

    if pais:
        query = query.filter(Circuito.pais.ilike(f"%{pais}%"))

    if tipo_pista:
        query = query.filter_by(tipo_pista=tipo_pista)

    if jolpica_id:
        query = query.filter_by(jolpica_id=jolpica_id)

    if activo is not None:
        activo_bool = activo.lower() in ('true', '1', 'yes', 'si')
        query = query.filter_by(activo=activo_bool)

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Circuito.nombre_gp.ilike(like),
                Circuito.nombre_circuito.ilike(like),
                Circuito.pais.ilike(like),
                Circuito.localidad.ilike(like)
            )
        )

    if orden == 'pais':
        query = query.order_by(Circuito.pais.asc())
    elif orden == 'tipo_pista':
        query = query.order_by(Circuito.tipo_pista.asc())
    elif orden == 'nivel_tecnico':
        query = query.order_by(Circuito.nivel_tecnico.desc())
    elif orden == 'nivel_sobrepaso':
        query = query.order_by(Circuito.nivel_sobrepaso.desc())
    elif orden == 'nivel_desgaste':
        query = query.order_by(Circuito.nivel_desgaste.desc())
    else:
        query = query.order_by(Circuito.nombre_gp.asc())

    circuitos = query.all()

    return jsonify([circuito.to_dict() for circuito in circuitos]), 200


@circuitos_bp.route('/<int:circuito_id>', methods=['GET'])
@jwt_required()
def detalle(circuito_id):
    circuito = Circuito.query.get_or_404(circuito_id)
    return jsonify(circuito.to_dict()), 200


@circuitos_bp.route('/jolpica/<string:jolpica_id>', methods=['GET'])
@jwt_required()
def detalle_por_jolpica_id(jolpica_id):
    circuito = Circuito.query.filter_by(jolpica_id=jolpica_id).first()

    if not circuito:
        return jsonify({
            'mensaje': 'Circuito no encontrado'
        }), 404

    return jsonify(circuito.to_dict()), 200


@circuitos_bp.route('/', methods=['POST'])
@jwt_required()
def crear():
    data = request.get_json() or {}

    campos_permitidos = (
        'nombre_gp',
        'nombre_circuito',
        'pais',

        'jolpica_id',
        'localidad',
        'latitud',
        'longitud_geo',
        'activo',

        'longitud',
        'num_curvas',
        'tipo_pista',
        'zonas_drs',
        'nivel_tecnico',
        'nivel_desgaste',
        'nivel_sobrepaso',
        'imagen'
    )

    circuito_data = {
        campo: data[campo]
        for campo in campos_permitidos
        if campo in data
    }

    campos_obligatorios = ('nombre_gp', 'nombre_circuito', 'pais')

    for campo in campos_obligatorios:
        if campo not in circuito_data or not circuito_data[campo]:
            return jsonify({
                'mensaje': f'{campo} es obligatorio'
            }), 400

    if 'jolpica_id' in circuito_data and circuito_data['jolpica_id']:
        existente = Circuito.query.filter_by(
            jolpica_id=circuito_data['jolpica_id']
        ).first()

        if existente:
            return jsonify({
                'mensaje': 'Ya existe un circuito con ese jolpica_id',
                'circuito': existente.to_dict()
            }), 409

    circuito = Circuito(**circuito_data)

    db.session.add(circuito)
    db.session.commit()

    return jsonify(circuito.to_dict()), 201


@circuitos_bp.route('/<int:circuito_id>', methods=['PUT'])
@jwt_required()
def actualizar(circuito_id):
    circuito = Circuito.query.get_or_404(circuito_id)
    data = request.get_json() or {}

    campos_actualizables = (
        'nombre_gp',
        'nombre_circuito',
        'pais',

        'jolpica_id',
        'localidad',
        'latitud',
        'longitud_geo',
        'activo',

        'longitud',
        'num_curvas',
        'tipo_pista',
        'zonas_drs',
        'nivel_tecnico',
        'nivel_desgaste',
        'nivel_sobrepaso',
        'imagen'
    )

    if 'jolpica_id' in data and data['jolpica_id']:
        existente = Circuito.query.filter(
            Circuito.jolpica_id == data['jolpica_id'],
            Circuito.id != circuito.id
        ).first()

        if existente:
            return jsonify({
                'mensaje': 'Ya existe otro circuito con ese jolpica_id'
            }), 409

    for campo in campos_actualizables:
        if campo in data:
            setattr(circuito, campo, data[campo])

    db.session.commit()

    return jsonify(circuito.to_dict()), 200


@circuitos_bp.route('/<int:circuito_id>', methods=['DELETE'])
@jwt_required()
def eliminar(circuito_id):
    circuito = Circuito.query.get_or_404(circuito_id)

    soft_delete = request.args.get('soft', 'true').lower() in ('true', '1', 'yes', 'si')

    if soft_delete:
        circuito.activo = False
        db.session.commit()

        return jsonify({
            'mensaje': 'Circuito desactivado correctamente',
            'circuito': circuito.to_dict()
        }), 200

    db.session.delete(circuito)
    db.session.commit()

    return jsonify({
        'mensaje': 'Circuito eliminado permanentemente'
    }), 200


@circuitos_bp.route('/<int:circuito_id>/activar', methods=['PATCH'])
@jwt_required()
def activar(circuito_id):
    circuito = Circuito.query.get_or_404(circuito_id)

    circuito.activo = True
    db.session.commit()

    return jsonify({
        'mensaje': 'Circuito activado correctamente',
        'circuito': circuito.to_dict()
    }), 200