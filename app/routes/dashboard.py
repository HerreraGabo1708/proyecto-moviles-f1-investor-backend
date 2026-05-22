from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.usuario import Usuario
from app.models.portfolio import Portfolio
from app.models.carrera import Carrera
from app.models.piloto import Piloto
from app.models.equipo import Equipo
from app.models.temporada import Temporada
from app.models.inversion import Inversion

dashboard_bp = Blueprint('dashboard', __name__)


def _obtener_activo(tipo_activo, activo_id):
    if tipo_activo == 'piloto':
        return Piloto.query.get(activo_id)

    if tipo_activo == 'equipo':
        return Equipo.query.get(activo_id)

    return None


def _calcular_item_portfolio(item):
    activo = _obtener_activo(item.tipo_activo, item.activo_id)

    if not activo:
        valor_actual = item.valor_actual or 0.0
        nombre = item.nombre_activo
        jolpica_id = item.jolpica_id
    else:
        valor_actual = activo.valor_mercado or 0.0
        nombre = activo.nombre
        jolpica_id = activo.jolpica_id

        item.valor_actual = valor_actual
        item.nombre_activo = nombre
        item.jolpica_id = jolpica_id

    valor_invertido = round(item.valor_promedio_compra * item.cantidad, 2)
    valor_posicion = round(valor_actual * item.cantidad, 2)
    ganancia = round(valor_posicion - valor_invertido, 2)

    rendimiento = 0.0

    if valor_invertido > 0:
        rendimiento = round((ganancia / valor_invertido) * 100, 2)

    return {
        'id': item.id,
        'tipo_activo': item.tipo_activo,
        'activo_id': item.activo_id,
        'jolpica_id': jolpica_id,
        'nombre_activo': nombre,
        'cantidad': item.cantidad,
        'valor_promedio_compra': item.valor_promedio_compra,
        'valor_actual': valor_actual,
        'valor_invertido': valor_invertido,
        'valor_posicion': valor_posicion,
        'ganancia_perdida': ganancia,
        'rendimiento_porcentaje': rendimiento,
        'activo': item.activo,
    }


@dashboard_bp.route('/', methods=['GET'])
@jwt_required()
def resumen():
    uid = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)

    items = Portfolio.query.filter_by(
        usuario_id=uid,
        activo=True
    ).all()

    portfolio_resumen = []
    valor_portfolio = 0.0
    ganancia_total = 0.0
    activo_mas_rentable = None
    activo_menos_rentable = None

    for item in items:
        item_data = _calcular_item_portfolio(item)

        valor_portfolio += item_data['valor_posicion']
        ganancia_total += item_data['ganancia_perdida']

        if activo_mas_rentable is None or item_data['ganancia_perdida'] > activo_mas_rentable['ganancia_perdida']:
            activo_mas_rentable = item_data

        if activo_menos_rentable is None or item_data['ganancia_perdida'] < activo_menos_rentable['ganancia_perdida']:
            activo_menos_rentable = item_data

        portfolio_resumen.append(item_data)

    patrimonio_total = round(usuario.capital + valor_portfolio, 2)
    ganancia_neta = round(patrimonio_total - usuario.capital_inicial, 2)

    rendimiento_porcentaje = 0.0

    if usuario.capital_inicial and usuario.capital_inicial > 0:
        rendimiento_porcentaje = round(
            (ganancia_neta / usuario.capital_inicial) * 100,
            2
        )

    temporada = Temporada.query.filter_by(activa=True).first()

    proximas_carreras = []
    ultimas_carreras = []

    if temporada:
        proximas_carreras = [
            carrera.to_dict()
            for carrera in Carrera.query.filter_by(
                temporada_id=temporada.id,
                estado='pendiente'
            ).order_by(
                Carrera.round_number.asc(),
                Carrera.fecha.asc()
            ).limit(3).all()
        ]

        ultimas_carreras = [
            carrera.to_dict()
            for carrera in Carrera.query.filter_by(
                temporada_id=temporada.id,
                estado='completada'
            ).order_by(
                Carrera.round_number.desc(),
                Carrera.fecha.desc()
            ).limit(3).all()
        ]

    top_pilotos_mercado = [
        piloto.to_dict()
        for piloto in Piloto.query.filter_by(
            activo=True
        ).order_by(
            Piloto.valor_mercado.desc()
        ).limit(5).all()
    ]

    top_equipos_mercado = [
        equipo.to_dict()
        for equipo in Equipo.query.filter_by(
            activo=True
        ).order_by(
            Equipo.valor_mercado.desc()
        ).limit(5).all()
    ]

    inversiones_recientes = [
        inversion.to_dict()
        for inversion in Inversion.query.filter_by(
            usuario_id=uid
        ).order_by(
            Inversion.fecha.desc()
        ).limit(5).all()
    ]

    total_inversiones = Inversion.query.filter_by(usuario_id=uid).count()

    db.session.commit()

    return jsonify({
        'usuario': {
            'id': usuario.id,
            'nombre': usuario.nombre,
            'correo': usuario.correo,
            'capital_inicial': usuario.capital_inicial,
            'capital_actual': usuario.capital,
        },

        'resumen_financiero': {
            'capital': round(usuario.capital, 2),
            'valor_portfolio': round(valor_portfolio, 2),
            'patrimonio_total': patrimonio_total,
            'ganancia_total_portfolio': round(ganancia_total, 2),
            'ganancia_neta': ganancia_neta,
            'rendimiento_porcentaje': rendimiento_porcentaje,
            'total_inversiones': total_inversiones,
            'cantidad_activos_portfolio': len(items),
        },

        'activo_mas_rentable': activo_mas_rentable,
        'activo_menos_rentable': activo_menos_rentable,

        'temporada_activa': temporada.to_dict() if temporada else None,
        'proximas_carreras': proximas_carreras,
        'ultimas_carreras': ultimas_carreras,

        'top_pilotos_mercado': top_pilotos_mercado,
        'top_equipos_mercado': top_equipos_mercado,
        'inversiones_recientes': inversiones_recientes,

        'portfolio': portfolio_resumen,
    }), 200


@dashboard_bp.route('/mercado', methods=['GET'])
@jwt_required()
def resumen_mercado():
    pilotos = Piloto.query.filter_by(
        activo=True
    ).order_by(
        Piloto.valor_mercado.desc()
    ).limit(10).all()

    equipos = Equipo.query.filter_by(
        activo=True
    ).order_by(
        Equipo.valor_mercado.desc()
    ).limit(10).all()

    return jsonify({
        'pilotos_top': [piloto.to_dict() for piloto in pilotos],
        'equipos_top': [equipo.to_dict() for equipo in equipos],
    }), 200


@dashboard_bp.route('/calendario', methods=['GET'])
@jwt_required()
def resumen_calendario():
    temporada = Temporada.query.filter_by(activa=True).first()

    if not temporada:
        return jsonify({
            'mensaje': 'No hay temporada activa',
            'temporada': None,
            'carreras': []
        }), 200

    carreras = Carrera.query.filter_by(
        temporada_id=temporada.id
    ).order_by(
        Carrera.round_number.asc(),
        Carrera.fecha.asc()
    ).all()

    pendientes = [carrera for carrera in carreras if carrera.estado == 'pendiente']
    completadas = [carrera for carrera in carreras if carrera.estado == 'completada']

    return jsonify({
        'temporada': temporada.to_dict(),
        'total_carreras': len(carreras),
        'pendientes': len(pendientes),
        'completadas': len(completadas),
        'carreras': [carrera.to_dict() for carrera in carreras],
    }), 200