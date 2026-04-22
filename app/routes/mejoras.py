from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.usuario import Usuario
from app.models.equipo  import Equipo
from app.models.mejora  import Mejora

mejoras_bp   = Blueprint('mejoras', __name__)
TIPOS_VALIDOS = {'motor', 'aerodinamica', 'fiabilidad', 'estrategia', 'desarrollo'}


@mejoras_bp.route('/', methods=['POST'])
@jwt_required()
def aplicar():
    uid     = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(uid)
    data    = request.get_json()

    equipo_id      = data.get('equipo_id')
    tipo           = data.get('tipo')
    valor_agregado = float(data.get('valor_agregado', 5.0))
    costo          = float(data.get('costo', 10_000.0))

    if tipo not in TIPOS_VALIDOS:
        return jsonify({'error': f'Tipo inválido. Opciones: {TIPOS_VALIDOS}'}), 400

    equipo = Equipo.query.get_or_404(equipo_id)
    if usuario.capital < costo:
        return jsonify({'error': 'Capital insuficiente'}), 400

    usuario.capital -= costo
    valor_actual     = getattr(equipo, tipo, 50.0)
    setattr(equipo, tipo, min(100.0, valor_actual + valor_agregado))

    # Recalcular media del equipo
    equipo.media = (equipo.rendimiento_coche + equipo.aerodinamica + equipo.motor +
                    equipo.fiabilidad + equipo.estrategia + equipo.desarrollo) / 6

    mejora = Mejora(equipo_id=equipo_id, tipo=tipo,
                    valor_agregado=valor_agregado, costo=costo)
    db.session.add(mejora)
    db.session.commit()
    return jsonify({'mensaje': 'Mejora aplicada', 'equipo': equipo.to_dict(),
                    'mejora': mejora.to_dict()}), 201


@mejoras_bp.route('/equipo/<int:equipo_id>', methods=['GET'])
@jwt_required()
def historial(equipo_id):
    mejoras = Mejora.query.filter_by(equipo_id=equipo_id).order_by(Mejora.fecha.desc()).all()
    return jsonify([m.to_dict() for m in mejoras]), 200
