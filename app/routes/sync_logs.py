from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.models.sync_log import SyncLog

sync_logs_bp = Blueprint('sync_logs', __name__)


@sync_logs_bp.route('/', methods=['GET'])
@jwt_required()
def listar():
    fuente = request.args.get('fuente')
    estado = request.args.get('estado')
    temporada = request.args.get('temporada', type=int)
    limite = request.args.get('limite', 50, type=int)

    query = SyncLog.query

    if fuente:
        query = query.filter_by(fuente=fuente)

    if estado:
        query = query.filter_by(estado=estado)

    if temporada:
        query = query.filter_by(temporada=temporada)

    logs = query.order_by(
        SyncLog.fecha.desc()
    ).limit(limite).all()

    return jsonify([log.to_dict() for log in logs]), 200


@sync_logs_bp.route('/<int:log_id>', methods=['GET'])
@jwt_required()
def detalle(log_id):
    log = SyncLog.query.get_or_404(log_id)
    return jsonify(log.to_dict()), 200


@sync_logs_bp.route('/errores', methods=['GET'])
@jwt_required()
def errores():
    limite = request.args.get('limite', 50, type=int)

    logs = SyncLog.query.filter_by(
        estado='error'
    ).order_by(
        SyncLog.fecha.desc()
    ).limit(limite).all()

    return jsonify([log.to_dict() for log in logs]), 200


@sync_logs_bp.route('/exitosos', methods=['GET'])
@jwt_required()
def exitosos():
    limite = request.args.get('limite', 50, type=int)

    logs = SyncLog.query.filter_by(
        estado='exitoso'
    ).order_by(
        SyncLog.fecha.desc()
    ).limit(limite).all()

    return jsonify([log.to_dict() for log in logs]), 200


@sync_logs_bp.route('/resumen', methods=['GET'])
@jwt_required()
def resumen():
    total = SyncLog.query.count()
    exitosos_count = SyncLog.query.filter_by(estado='exitoso').count()
    errores_count = SyncLog.query.filter_by(estado='error').count()

    ultimo_log = SyncLog.query.order_by(
        SyncLog.fecha.desc()
    ).first()

    ultimo_error = SyncLog.query.filter_by(
        estado='error'
    ).order_by(
        SyncLog.fecha.desc()
    ).first()

    return jsonify({
        'total_logs': total,
        'total_exitosos': exitosos_count,
        'total_errores': errores_count,
        'ultimo_log': ultimo_log.to_dict() if ultimo_log else None,
        'ultimo_error': ultimo_error.to_dict() if ultimo_error else None,
    }), 200


@sync_logs_bp.route('/limpiar', methods=['DELETE'])
@jwt_required()
def limpiar():
    estado = request.args.get('estado')
    fuente = request.args.get('fuente')

    query = SyncLog.query

    if estado:
        query = query.filter_by(estado=estado)

    if fuente:
        query = query.filter_by(fuente=fuente)

    cantidad = query.count()

    query.delete(synchronize_session=False)

    from app import db
    db.session.commit()

    return jsonify({
        'mensaje': 'Logs eliminados correctamente',
        'cantidad_eliminada': cantidad
    }), 200