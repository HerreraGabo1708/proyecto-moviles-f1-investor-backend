"""
Servicio de mercado: actualiza el valor de pilotos y equipos
tras cada carrera simulada.
"""
from app import db
from app.models.resultado import Resultado
from app.models.piloto    import Piloto
from app.models.equipo    import Equipo

_VAR = {
    1:  0.12,  2:  0.08, 3:  0.06,
    4:  0.04,  5:  0.03, 6:  0.02,
    7:  0.01,  8:  0.00, 9: -0.01,
    10:-0.02,
}


def _variacion(posicion: int, estado: str) -> float:
    if estado == 'abandono':
        return -0.08
    return _VAR.get(posicion, -0.03)


def actualizar_mercado(carrera) -> None:
    resultados        = Resultado.query.filter_by(carrera_id=carrera.id).all()
    equipos_var: dict = {}

    for res in resultados:
        piloto = Piloto.query.get(res.piloto_id)
        if not piloto:
            continue

        var = _variacion(res.posicion, res.estado_final)
        piloto.valor_mercado = max(1_000.0, piloto.valor_mercado * (1 + var))
        piloto.media = (
            piloto.skill        * 0.25 +
            piloto.racecraft    * 0.20 +
            piloto.consistencia * 0.20 +
            piloto.experiencia  * 0.15 +
            piloto.potencial    * 0.10 +
            piloto.forma_actual * 0.10
        )

        if piloto.equipo_id:
            equipos_var.setdefault(piloto.equipo_id, []).append(var)

    for equipo_id, variaciones in equipos_var.items():
        equipo = Equipo.query.get(equipo_id)
        if not equipo:
            continue
        var_avg = sum(variaciones) / len(variaciones)
        equipo.valor_mercado = max(10_000.0, equipo.valor_mercado * (1 + var_avg * 0.5))

    db.session.commit()
