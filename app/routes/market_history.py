from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.models.market_history import MarketHistory

market_history_bp = Blueprint('market_history', __name__)


@market_history_bp.route('/', methods=['GET'])
@jwt_required()
def listar():
    tipo_activo = request.args.get('tipo_activo')
    activo_id = request.args.get('activo_id', type=int)
    temporada_id = request.args.get('temporada_id', type=int)
    carrera_id = request.args.get('carrera_id', type=int)
    jolpica_id = request.args.get('jolpica_id')
    limite = request.args.get('limite', 50, type=int)

    query = MarketHistory.query

    if tipo_activo:
        query = query.filter_by(tipo_activo=tipo_activo)

    if activo_id:
        query = query.filter_by(activo_id=activo_id)

    if temporada_id:
        query = query.filter_by(temporada_id=temporada_id)

    if carrera_id:
        query = query.filter_by(carrera_id=carrera_id)

    if jolpica_id:
        query = query.filter_by(jolpica_id=jolpica_id)

    registros = query.order_by(
        MarketHistory.fecha.desc()
    ).limit(limite).all()

    return jsonify([registro.to_dict() for registro in registros]), 200


@market_history_bp.route('/<int:history_id>', methods=['GET'])
@jwt_required()
def detalle(history_id):
    registro = MarketHistory.query.get_or_404(history_id)
    return jsonify(registro.to_dict()), 200


@market_history_bp.route('/activo/<string:tipo_activo>/<int:activo_id>', methods=['GET'])
@jwt_required()
def historial_activo(tipo_activo, activo_id):
    limite = request.args.get('limite', 100, type=int)

    if tipo_activo not in ('piloto', 'equipo'):
        return jsonify({
            'error': 'tipo_activo debe ser piloto o equipo'
        }), 400

    registros = MarketHistory.query.filter_by(
        tipo_activo=tipo_activo,
        activo_id=activo_id
    ).order_by(
        MarketHistory.fecha.asc()
    ).limit(limite).all()

    return jsonify([registro.to_dict() for registro in registros]), 200


@market_history_bp.route('/grafico/<string:tipo_activo>/<int:activo_id>', methods=['GET'])
@jwt_required()
def datos_grafico(tipo_activo, activo_id):
    limite = request.args.get('limite', 100, type=int)

    if tipo_activo not in ('piloto', 'equipo'):
        return jsonify({
            'error': 'tipo_activo debe ser piloto o equipo'
        }), 400

    registros = MarketHistory.query.filter_by(
        tipo_activo=tipo_activo,
        activo_id=activo_id
    ).order_by(
        MarketHistory.fecha.asc()
    ).limit(limite).all()

    labels = []
    valores = []
    variaciones = []

    for registro in registros:
        labels.append(registro.fecha.isoformat() if registro.fecha else None)
        valores.append(registro.valor_nuevo)
        variaciones.append(registro.porcentaje_variacion)

    return jsonify({
        'tipo_activo': tipo_activo,
        'activo_id': activo_id,
        'labels': labels,
        'valores': valores,
        'variaciones': variaciones,
        'registros': [registro.to_dict() for registro in registros]
    }), 200


@market_history_bp.route('/ultimos-cambios', methods=['GET'])
@jwt_required()
def ultimos_cambios():
    limite = request.args.get('limite', 10, type=int)

    registros = MarketHistory.query.order_by(
        MarketHistory.fecha.desc()
    ).limit(limite).all()

    return jsonify([registro.to_dict() for registro in registros]), 200


@market_history_bp.route('/mayores-subidas', methods=['GET'])
@jwt_required()
def mayores_subidas():
    limite = request.args.get('limite', 10, type=int)

    registros = MarketHistory.query.order_by(
        MarketHistory.porcentaje_variacion.desc()
    ).limit(limite).all()

    return jsonify([registro.to_dict() for registro in registros]), 200


@market_history_bp.route('/mayores-bajadas', methods=['GET'])
@jwt_required()
def mayores_bajadas():
    limite = request.args.get('limite', 10, type=int)

    registros = MarketHistory.query.order_by(
        MarketHistory.porcentaje_variacion.asc()
    ).limit(limite).all()

    return jsonify([registro.to_dict() for registro in registros]), 200