from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.usuario   import Usuario
from app.models.inversion import Inversion
from app.models.portfolio import Portfolio
from app.models.piloto    import Piloto
from app.models.equipo    import Equipo

inversiones_bp = Blueprint('inversiones', __name__)


def _valor_activo(tipo, activo_id):
    obj = Piloto.query.get(activo_id) if tipo == 'piloto' else Equipo.query.get(activo_id)
    return obj.valor_mercado if obj else None


@inversiones_bp.route('/comprar', methods=['POST'])
@jwt_required()
def comprar():
    uid     = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)
    data    = request.get_json()

    tipo, activo_id = data.get('tipo_activo'), data.get('activo_id')
    cantidad        = float(data.get('cantidad', 1.0))
    valor           = _valor_activo(tipo, activo_id)

    if valor is None:
        return jsonify({'error': 'Activo no encontrado'}), 404

    monto = valor * cantidad
    if usuario.capital < monto:
        return jsonify({'error': 'Capital insuficiente'}), 400

    usuario.capital -= monto

    inv = Inversion(usuario_id=uid, tipo_activo=tipo, activo_id=activo_id,
                    tipo_operacion='compra', monto=monto, cantidad=cantidad)
    db.session.add(inv)

    port = Portfolio.query.filter_by(usuario_id=uid, tipo_activo=tipo,
                                     activo_id=activo_id).first()
    if port:
        total = port.cantidad + cantidad
        port.valor_promedio_compra = (port.valor_promedio_compra * port.cantidad +
                                      valor * cantidad) / total
        port.cantidad = total
    else:
        port = Portfolio(usuario_id=uid, tipo_activo=tipo, activo_id=activo_id,
                         cantidad=cantidad, valor_promedio_compra=valor)
        db.session.add(port)

    db.session.commit()
    return jsonify({'mensaje': 'Compra realizada', 'capital_restante': usuario.capital,
                    'inversion': inv.to_dict()}), 201


@inversiones_bp.route('/vender', methods=['POST'])
@jwt_required()
def vender():
    uid     = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)
    data    = request.get_json()

    tipo, activo_id = data.get('tipo_activo'), data.get('activo_id')
    cantidad        = float(data.get('cantidad', 1.0))

    port = Portfolio.query.filter_by(usuario_id=uid, tipo_activo=tipo,
                                     activo_id=activo_id).first()
    if not port or port.cantidad < cantidad:
        return jsonify({'error': 'No tienes suficientes activos para vender'}), 400

    valor = _valor_activo(tipo, activo_id)
    if valor is None:
        return jsonify({'error': 'Activo no encontrado'}), 404

    monto            = valor * cantidad
    usuario.capital += monto
    port.cantidad   -= cantidad
    if port.cantidad <= 0:
        db.session.delete(port)

    inv = Inversion(usuario_id=uid, tipo_activo=tipo, activo_id=activo_id,
                    tipo_operacion='venta', monto=monto, cantidad=cantidad)
    db.session.add(inv)
    db.session.commit()
    return jsonify({'mensaje': 'Venta realizada', 'capital_actual': usuario.capital,
                    'inversion': inv.to_dict()}), 200


@inversiones_bp.route('/historial', methods=['GET'])
@jwt_required()
def historial():
    uid = int(get_jwt_identity())
    inv = Inversion.query.filter_by(usuario_id=uid).order_by(Inversion.fecha.desc()).all()
    return jsonify([i.to_dict() for i in inv]), 200


@inversiones_bp.route('/portfolio', methods=['GET'])
@jwt_required()
def portfolio():
    uid     = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)
    items   = Portfolio.query.filter_by(usuario_id=uid).all()

    resultado, valor_total = [], 0.0
    for item in items:
        va     = _valor_activo(item.tipo_activo, item.activo_id) or 0
        vpos   = va * item.cantidad
        ganancia = vpos - item.valor_promedio_compra * item.cantidad
        valor_total += vpos
        resultado.append({
            **item.to_dict(),
            'valor_actual':     va,
            'valor_posicion':   vpos,
            'ganancia_perdida': ganancia,
        })

    return jsonify({
        'capital':     usuario.capital,
        'valor_total': valor_total,
        'patrimonio':  usuario.capital + valor_total,
        'portfolio':   resultado,
    }), 200
