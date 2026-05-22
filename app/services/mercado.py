"""
Servicio de mercado: actualiza el valor de pilotos y equipos
despues de cada carrera, usando resultados simulados o importados desde Jolpica.
"""

from app import db
from app.models.resultado import Resultado
from app.models.piloto import Piloto
from app.models.equipo import Equipo
from app.models.portfolio import Portfolio
from app.models.market_history import MarketHistory


# Variacion base segun posicion final
_VAR_POSICION = {
    1:  0.12,
    2:  0.08,
    3:  0.06,
    4:  0.04,
    5:  0.03,
    6:  0.02,
    7:  0.01,
    8:  0.00,
    9: -0.01,
    10: -0.02,
}


def _variacion_por_resultado(resultado: Resultado) -> float:
    """
    Calcula la variacion porcentual del valor de mercado
    segun posicion, puntos, posiciones ganadas/perdidas y estado final.
    """

    if resultado.estado_final == "abandono":
        return -0.08

    if resultado.estado_final == "dsq":
        return -0.12

    variacion = _VAR_POSICION.get(resultado.posicion, -0.03)

    # Bonus pequeño por puntos
    if resultado.puntos and resultado.puntos > 0:
        variacion += min(resultado.puntos * 0.002, 0.04)

    # Bonus o castigo por posiciones ganadas/perdidas
    if resultado.posicion_salida is not None and resultado.posicion is not None:
        posiciones_ganadas = resultado.posicion_salida - resultado.posicion

        if posiciones_ganadas > 0:
            variacion += min(posiciones_ganadas * 0.005, 0.04)

        elif posiciones_ganadas < 0:
            variacion += max(posiciones_ganadas * 0.004, -0.04)

    return round(variacion, 4)


def _calcular_media_piloto(piloto: Piloto) -> float:
    """
    Calcula la media general del piloto usando sus atributos internos.
    """

    media = (
        piloto.skill * 0.25 +
        piloto.racecraft * 0.20 +
        piloto.consistencia * 0.20 +
        piloto.experiencia * 0.15 +
        piloto.potencial * 0.10 +
        piloto.forma_actual * 0.10
    )

    return round(media, 2)


def _calcular_media_equipo(equipo: Equipo) -> float:
    """
    Calcula la media general del equipo usando sus atributos internos.
    """

    media = (
        equipo.rendimiento_coche +
        equipo.aerodinamica +
        equipo.motor +
        equipo.fiabilidad +
        equipo.estrategia +
        equipo.desarrollo
    ) / 6

    return round(media, 2)


def _registrar_historial_mercado(
    tipo_activo,
    activo_id,
    jolpica_id,
    nombre_activo,
    temporada_id,
    carrera_id,
    valor_anterior,
    valor_nuevo,
    motivo
):
    """
    Registra el cambio de valor en MarketHistory.
    """

    historial = MarketHistory(
        tipo_activo=tipo_activo,
        activo_id=activo_id,
        jolpica_id=jolpica_id,
        nombre_activo=nombre_activo,
        temporada_id=temporada_id,
        carrera_id=carrera_id,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        motivo=motivo
    )

    historial.calcular_variacion()

    db.session.add(historial)

    return historial


def _actualizar_portfolio_activo(tipo_activo, activo_id, nuevo_valor):
    """
    Actualiza el valor actual de todos los portfolios que tengan este activo.
    """

    items = Portfolio.query.filter_by(
        tipo_activo=tipo_activo,
        activo_id=activo_id
    ).all()

    for item in items:
        item.valor_actual = nuevo_valor


def actualizar_mercado(carrera) -> None:
    """
    Actualiza el valor de mercado de pilotos y equipos despues de una carrera.

    Este metodo sirve tanto para carreras simuladas como para resultados
    importados desde Jolpica, siempre que existan registros en Resultado.
    """

    resultados = Resultado.query.filter_by(carrera_id=carrera.id).all()

    if not resultados:
        return

    equipos_var = {}

    temporada_id = carrera.temporada_id if hasattr(carrera, "temporada_id") else None
    carrera_id = carrera.id

    # ==========================================================
    # Actualizar pilotos
    # ==========================================================

    for resultado in resultados:
        piloto = Piloto.query.get(resultado.piloto_id)

        if not piloto:
            continue

        valor_anterior = piloto.valor_mercado or 0.0

        variacion = _variacion_por_resultado(resultado)

        nuevo_valor = max(
            1_000.0,
            valor_anterior * (1 + variacion)
        )

        piloto.valor_mercado = round(nuevo_valor, 2)

        # Ajuste simple de forma actual
        if resultado.estado_final == "abandono":
            piloto.forma_actual = max(0.0, piloto.forma_actual - 5.0)
        elif resultado.posicion <= 3:
            piloto.forma_actual = min(100.0, piloto.forma_actual + 4.0)
        elif resultado.posicion <= 10:
            piloto.forma_actual = min(100.0, piloto.forma_actual + 1.5)
        else:
            piloto.forma_actual = max(0.0, piloto.forma_actual - 1.0)

        piloto.media = _calcular_media_piloto(piloto)

        _registrar_historial_mercado(
            tipo_activo="piloto",
            activo_id=piloto.id,
            jolpica_id=piloto.jolpica_id,
            nombre_activo=piloto.nombre,
            temporada_id=temporada_id,
            carrera_id=carrera_id,
            valor_anterior=valor_anterior,
            valor_nuevo=piloto.valor_mercado,
            motivo=f"Resultado carrera P{resultado.posicion}"
        )

        _actualizar_portfolio_activo(
            tipo_activo="piloto",
            activo_id=piloto.id,
            nuevo_valor=piloto.valor_mercado
        )

        equipo_id = resultado.equipo_id or piloto.equipo_id

        if equipo_id:
            equipos_var.setdefault(equipo_id, []).append(variacion)

    # ==========================================================
    # Actualizar equipos
    # ==========================================================

    for equipo_id, variaciones in equipos_var.items():
        equipo = Equipo.query.get(equipo_id)

        if not equipo:
            continue

        valor_anterior = equipo.valor_mercado or 0.0

        variacion_promedio = sum(variaciones) / len(variaciones)

        # El equipo se mueve menos que el piloto individual
        variacion_equipo = variacion_promedio * 0.5

        nuevo_valor = max(
            10_000.0,
            valor_anterior * (1 + variacion_equipo)
        )

        equipo.valor_mercado = round(nuevo_valor, 2)
        equipo.media = _calcular_media_equipo(equipo)

        _registrar_historial_mercado(
            tipo_activo="equipo",
            activo_id=equipo.id,
            jolpica_id=equipo.jolpica_id,
            nombre_activo=equipo.nombre,
            temporada_id=temporada_id,
            carrera_id=carrera_id,
            valor_anterior=valor_anterior,
            valor_nuevo=equipo.valor_mercado,
            motivo="Promedio de resultados de pilotos del equipo"
        )

        _actualizar_portfolio_activo(
            tipo_activo="equipo",
            activo_id=equipo.id,
            nuevo_valor=equipo.valor_mercado
        )

    db.session.commit()