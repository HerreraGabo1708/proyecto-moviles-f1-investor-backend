from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.usuario import Usuario
from app.models.inversion import Inversion
from app.models.portfolio import Portfolio
from app.models.piloto import Piloto
from app.models.equipo import Equipo

inversiones_bp = Blueprint('inversiones', __name__)


def _obtener_activo(tipo_activo, activo_id):
    if tipo_activo == 'piloto':
        return Piloto.query.get(activo_id)

    if tipo_activo == 'equipo':
        return Equipo.query.get(activo_id)

    return None


def _datos_activo(tipo_activo, activo_id):
    activo = _obtener_activo(tipo_activo, activo_id)

    if not activo:
        return None

    return {
        'objeto': activo,
        'valor_mercado': activo.valor_mercado or 0.0,
        'nombre': activo.nombre,
        'jolpica_id': activo.jolpica_id
    }


def _validar_tipo_activo(tipo_activo):
    return tipo_activo in ('piloto', 'equipo')


def _parse_cantidad(value):
    try:
        cantidad = float(value)
    except (ValueError, TypeError):
        return None

    if cantidad <= 0:
        return None

    return cantidad


@inversiones_bp.route('/comprar', methods=['POST'])
@jwt_required()
def comprar():
    uid = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)
    data = request.get_json() or {}

    tipo_activo = data.get('tipo_activo')
    activo_id = data.get('activo_id')
    cantidad = _parse_cantidad(data.get('cantidad', 1.0))

    if not _validar_tipo_activo(tipo_activo):
        return jsonify({
            'error': 'tipo_activo debe ser piloto o equipo'
        }), 400

    if not activo_id:
        return jsonify({
            'error': 'activo_id es obligatorio'
        }), 400

    if cantidad is None:
        return jsonify({
            'error': 'La cantidad debe ser mayor a cero'
        }), 400

    datos = _datos_activo(tipo_activo, activo_id)

    if not datos:
        return jsonify({
            'error': 'Activo no encontrado'
        }), 404

    valor = datos['valor_mercado']
    nombre_activo = datos['nombre']
    jolpica_id = datos['jolpica_id']

    if valor <= 0:
        return jsonify({
            'error': 'El activo no tiene un valor de mercado valido'
        }), 400

    monto = round(valor * cantidad, 2)

    if not usuario.tiene_capital_suficiente(monto):
        return jsonify({
            'error': 'Capital insuficiente',
            'capital_actual': usuario.capital,
            'monto_requerido': monto
        }), 400

    try:
        usuario.debitar_capital(monto)

        inversion = Inversion.crear_compra(
            usuario_id=uid,
            tipo_activo=tipo_activo,
            activo_id=activo_id,
            nombre_activo=nombre_activo,
            precio_unitario=valor,
            cantidad=cantidad,
            jolpica_id=jolpica_id
        )

        db.session.add(inversion)

        item_portfolio = Portfolio.query.filter_by(
            usuario_id=uid,
            tipo_activo=tipo_activo,
            activo_id=activo_id
        ).first()

        if item_portfolio:
            item_portfolio.actualizar_por_compra(
                cantidad_comprada=cantidad,
                precio_unitario=valor
            )

            item_portfolio.jolpica_id = jolpica_id
            item_portfolio.nombre_activo = nombre_activo
            item_portfolio.valor_actual = valor
            item_portfolio.activo = True

        else:
            item_portfolio = Portfolio.crear_item(
                usuario_id=uid,
                tipo_activo=tipo_activo,
                activo_id=activo_id,
                nombre_activo=nombre_activo,
                cantidad=cantidad,
                precio_unitario=valor,
                jolpica_id=jolpica_id
            )

            db.session.add(item_portfolio)

        db.session.commit()

        return jsonify({
            'mensaje': 'Compra realizada correctamente',
            'capital_restante': usuario.capital,
            'inversion': inversion.to_dict(),
            'portfolio_item': item_portfolio.to_dict()
        }), 201

    except ValueError as error:
        db.session.rollback()

        return jsonify({
            'error': str(error)
        }), 400

    except Exception as error:
        db.session.rollback()

        return jsonify({
            'error': 'Error realizando la compra',
            'detalle': str(error)
        }), 500


@inversiones_bp.route('/vender', methods=['POST'])
@jwt_required()
def vender():
    uid = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)
    data = request.get_json() or {}

    tipo_activo = data.get('tipo_activo')
    activo_id = data.get('activo_id')
    cantidad = _parse_cantidad(data.get('cantidad', 1.0))

    if not _validar_tipo_activo(tipo_activo):
        return jsonify({
            'error': 'tipo_activo debe ser piloto o equipo'
        }), 400

    if not activo_id:
        return jsonify({
            'error': 'activo_id es obligatorio'
        }), 400

    if cantidad is None:
        return jsonify({
            'error': 'La cantidad debe ser mayor a cero'
        }), 400

    item_portfolio = Portfolio.query.filter_by(
        usuario_id=uid,
        tipo_activo=tipo_activo,
        activo_id=activo_id,
        activo=True
    ).first()

    if not item_portfolio or item_portfolio.cantidad < cantidad:
        return jsonify({
            'error': 'No tienes suficientes activos para vender'
        }), 400

    datos = _datos_activo(tipo_activo, activo_id)

    if not datos:
        return jsonify({
            'error': 'Activo no encontrado'
        }), 404

    valor = datos['valor_mercado']
    nombre_activo = datos['nombre']
    jolpica_id = datos['jolpica_id']

    if valor <= 0:
        return jsonify({
            'error': 'El activo no tiene un valor de mercado valido'
        }), 400

    monto = round(valor * cantidad, 2)

    try:
        usuario.acreditar_capital(monto)

        item_portfolio.actualizar_por_venta(cantidad)

        item_portfolio.valor_actual = valor
        item_portfolio.nombre_activo = nombre_activo
        item_portfolio.jolpica_id = jolpica_id

        inversion = Inversion.crear_venta(
            usuario_id=uid,
            tipo_activo=tipo_activo,
            activo_id=activo_id,
            nombre_activo=nombre_activo,
            precio_unitario=valor,
            cantidad=cantidad,
            jolpica_id=jolpica_id
        )

        db.session.add(inversion)
        db.session.commit()

        return jsonify({
            'mensaje': 'Venta realizada correctamente',
            'capital_actual': usuario.capital,
            'inversion': inversion.to_dict(),
            'portfolio_item': item_portfolio.to_dict()
        }), 200

    except ValueError as error:
        db.session.rollback()

        return jsonify({
            'error': str(error)
        }), 400

    except Exception as error:
        db.session.rollback()

        return jsonify({
            'error': 'Error realizando la venta',
            'detalle': str(error)
        }), 500


@inversiones_bp.route('/historial', methods=['GET'])
@jwt_required()
def historial():
    uid = int(get_jwt_identity())

    tipo_activo = request.args.get('tipo_activo')
    tipo_operacion = request.args.get('tipo_operacion')
    estado = request.args.get('estado')

    query = Inversion.query.filter_by(usuario_id=uid)

    if tipo_activo:
        query = query.filter_by(tipo_activo=tipo_activo)

    if tipo_operacion:
        query = query.filter_by(tipo_operacion=tipo_operacion)

    if estado:
        query = query.filter_by(estado=estado)

    inversiones = query.order_by(Inversion.fecha.desc()).all()

    return jsonify([inversion.to_dict() for inversion in inversiones]), 200


@inversiones_bp.route('/portfolio', methods=['GET'])
@jwt_required()
def portfolio():
    uid = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)

    incluir_inactivos = request.args.get(
        'incluir_inactivos',
        'false'
    ).lower() in ('true', '1', 'yes', 'si')

    query = Portfolio.query.filter_by(usuario_id=uid)

    if not incluir_inactivos:
        query = query.filter_by(activo=True)

    items = query.all()

    resultado = []
    valor_total = 0.0
    ganancia_total = 0.0

    for item in items:
        datos = _datos_activo(item.tipo_activo, item.activo_id)

        if datos:
            valor_actual = datos['valor_mercado']
            item.valor_actual = valor_actual
            item.nombre_activo = datos['nombre']
            item.jolpica_id = datos['jolpica_id']
        else:
            valor_actual = item.valor_actual or 0.0

        valor_posicion = round(valor_actual * item.cantidad, 2)
        ganancia = round(
            valor_posicion - (item.valor_promedio_compra * item.cantidad),
            2
        )

        valor_total += valor_posicion
        ganancia_total += ganancia

        resultado.append(item.to_dict())

    patrimonio = round(usuario.capital + valor_total, 2)

    db.session.commit()

    return jsonify({
        'capital': usuario.capital,
        'valor_total': round(valor_total, 2),
        'ganancia_total': round(ganancia_total, 2),
        'patrimonio': patrimonio,
        'portfolio': resultado
    }), 200


@inversiones_bp.route('/resumen', methods=['GET'])
@jwt_required()
def resumen():
    uid = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)

    inversiones = Inversion.query.filter_by(usuario_id=uid).all()
    items = Portfolio.query.filter_by(usuario_id=uid, activo=True).all()

    total_compras = sum(
        inversion.monto
        for inversion in inversiones
        if inversion.tipo_operacion == 'compra'
    )

    total_ventas = sum(
        inversion.monto
        for inversion in inversiones
        if inversion.tipo_operacion == 'venta'
    )

    valor_portfolio = 0.0

    for item in items:
        datos = _datos_activo(item.tipo_activo, item.activo_id)

        if datos:
            item.valor_actual = datos['valor_mercado']

        valor_portfolio += item.valor_actual_total()

    patrimonio = round(usuario.capital + valor_portfolio, 2)
    ganancia_neta = round(patrimonio - usuario.capital_inicial, 2)

    rendimiento = 0.0

    if usuario.capital_inicial > 0:
        rendimiento = round((ganancia_neta / usuario.capital_inicial) * 100, 2)

    db.session.commit()

    return jsonify({
        'usuario_id': usuario.id,
        'capital_inicial': usuario.capital_inicial,
        'capital_actual': usuario.capital,
        'valor_portfolio': round(valor_portfolio, 2),
        'patrimonio': patrimonio,
        'ganancia_neta': ganancia_neta,
        'rendimiento_porcentaje': rendimiento,
        'total_compras': round(total_compras, 2),
        'total_ventas': round(total_ventas, 2),
        'cantidad_inversiones': len(inversiones),
        'cantidad_activos_portfolio': len(items)
    }), 200