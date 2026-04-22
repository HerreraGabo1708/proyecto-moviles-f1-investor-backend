from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.usuario   import Usuario
from app.models.portfolio import Portfolio
from app.models.carrera   import Carrera
from app.models.piloto    import Piloto
from app.models.equipo    import Equipo
from app.models.temporada import Temporada
from flask import Blueprint

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/', methods=['GET'])
@jwt_required()
def resumen():
    uid      = int(get_jwt_identity())
    usuario  = Usuario.query.get_or_404(uid)
    items    = Portfolio.query.filter_by(usuario_id=uid).all()

    valor_total, mejor = 0.0, None
    for item in items:
        if item.tipo_activo == 'piloto':
            obj = Piloto.query.get(item.activo_id)
        else:
            obj = Equipo.query.get(item.activo_id)
        if not obj:
            continue
        vpos = obj.valor_mercado * item.cantidad
        valor_total += vpos
        ganancia = vpos - item.valor_promedio_compra * item.cantidad
        if mejor is None or ganancia > mejor['ganancia']:
            mejor = {'nombre': obj.nombre, 'tipo': item.tipo_activo, 'ganancia': ganancia}

    temporada = Temporada.query.filter_by(activa=True).first()
    proximas  = []
    recientes = []
    if temporada:
        proximas  = [c.to_dict() for c in
                     Carrera.query.filter_by(temporada_id=temporada.id,
                                             estado='pendiente').limit(3).all()]
        recientes = [c.to_dict() for c in
                     Carrera.query.filter_by(temporada_id=temporada.id,
                                             estado='completada').order_by(
                                             Carrera.id.desc()).limit(3).all()]

    return jsonify({
        'capital':            usuario.capital,
        'valor_portafolio':   valor_total,
        'patrimonio_total':   usuario.capital + valor_total,
        'activo_mas_rentable':mejor,
        'proximas_carreras':  proximas,
        'ultimas_carreras':   recientes,
    }), 200
