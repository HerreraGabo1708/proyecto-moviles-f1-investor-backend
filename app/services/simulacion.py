"""
Servicio de simulacion de carrera.

Genera resultados basados en estadisticas de pilotos, equipos,
monoplazas, circuito y eventos adversos.

Este servicio puede funcionar de forma independiente a Jolpica.
Jolpica aporta datos reales al sistema, pero esta simulacion usa
los modelos internos del juego F1 Investor.
"""

import random

from app import db
from app.models.piloto import Piloto
from app.models.monoplaza import Monoplaza
from app.models.resultado import Resultado
from app.models.evento import Evento
from app.services.mercado import actualizar_mercado


PUNTOS_F1 = {
    1: 25,
    2: 18,
    3: 15,
    4: 12,
    5: 10,
    6: 8,
    7: 6,
    8: 4,
    9: 2,
    10: 1
}


def _obtener_monoplaza(piloto: Piloto, carrera=None):
    """
    Busca el monoplaza del piloto.

    Primero intenta buscar por piloto y temporada.
    Si no encuentra, busca cualquier monoplaza asignado al piloto.
    """

    temporada_id = None

    if carrera and hasattr(carrera, "temporada_id"):
        temporada_id = carrera.temporada_id

    if temporada_id:
        monoplaza = Monoplaza.query.filter_by(
            piloto_id=piloto.id,
            temporada_id=temporada_id,
            activo=True
        ).first()

        if monoplaza:
            return monoplaza

    return Monoplaza.query.filter_by(
        piloto_id=piloto.id,
        activo=True
    ).first()


def _score_piloto(piloto: Piloto, circuito, carrera=None) -> float:
    """
    Calcula la puntuacion base de un piloto para una carrera.
    """

    habilidad = (
        piloto.skill * 0.30 +
        piloto.racecraft * 0.20 +
        piloto.consistencia * 0.20 +
        piloto.experiencia * 0.15 +
        piloto.forma_actual * 0.15
    )

    monoplaza = _obtener_monoplaza(piloto, carrera)

    if monoplaza:
        coche = (
            (monoplaza.velocidad_punta / 3.5) * 0.30 +
            monoplaza.aceleracion * 0.20 +
            monoplaza.aerodinamica * 0.25 +
            monoplaza.fiabilidad * 0.15 +
            monoplaza.media * 0.10
        )
    else:
        coche = 50.0

    bonus_circuito = 0.0

    if circuito:
        if circuito.tipo_pista in ("tecnico", "callejero"):
            bonus_circuito += (piloto.racecraft - 50.0) * 0.30
            bonus_circuito += (piloto.consistencia - 50.0) * 0.15

        elif circuito.tipo_pista == "rapido":
            if monoplaza:
                bonus_circuito += ((monoplaza.velocidad_punta / 3.0) - 100.0) * 0.20
            bonus_circuito += (piloto.skill - 50.0) * 0.10

        elif circuito.tipo_pista == "mixto":
            bonus_circuito += (piloto.consistencia - 50.0) * 0.15

        bonus_circuito += (circuito.nivel_tecnico - 50.0) * 0.05
        bonus_circuito += (circuito.nivel_sobrepaso - 50.0) * 0.03

    ruido = random.gauss(0, 4)

    return round(
        habilidad * 0.55 +
        coche * 0.45 +
        bonus_circuito +
        ruido,
        2
    )


def _probabilidad_abandono(piloto: Piloto, monoplaza: Monoplaza | None) -> float:
    """
    Calcula una probabilidad simple de abandono.
    """

    base = 0.03

    if monoplaza:
        penalizacion_fiabilidad = max(0.0, (60.0 - monoplaza.fiabilidad) / 1000.0)
        base += penalizacion_fiabilidad

    if piloto.consistencia < 50:
        base += (50.0 - piloto.consistencia) / 1000.0

    return min(base, 0.20)


def _aplicar_eventos(puntuacion: float, piloto: Piloto, monoplaza: Monoplaza | None, circuito=None) -> tuple:
    """
    Aplica eventos adversos activos a la puntuacion del piloto.
    Retorna puntuacion final, estado final y lista de eventos aplicados.
    """

    eventos = Evento.query.filter_by(activo=True).all()

    estado = "finalizado"
    eventos_aplicados = []

    for evento in eventos:
        if evento.tipo_pista and circuito:
            if evento.tipo_pista not in ("cualquiera", circuito.tipo_pista):
                continue

        if random.random() <= evento.probabilidad:
            eventos_aplicados.append(evento.nombre)

            puntuacion += evento.efecto_valor

            if evento.afecta_a == "piloto":
                if evento.efecto_forma != 0:
                    piloto.forma_actual = max(
                        0.0,
                        min(100.0, piloto.forma_actual + evento.efecto_forma)
                    )

                if evento.efecto_rendimiento != 0:
                    puntuacion += evento.efecto_rendimiento

            elif evento.afecta_a == "monoplaza" and monoplaza:
                if evento.efecto_fiabilidad != 0:
                    monoplaza.fiabilidad = max(
                        0.0,
                        min(100.0, monoplaza.fiabilidad + evento.efecto_fiabilidad)
                    )

                if evento.efecto_rendimiento != 0:
                    puntuacion += evento.efecto_rendimiento

            elif evento.afecta_a == "equipo" and piloto.equipo:
                if evento.efecto_rendimiento != 0:
                    piloto.equipo.rendimiento_coche = max(
                        0.0,
                        min(100.0, piloto.equipo.rendimiento_coche + evento.efecto_rendimiento)
                    )

            if evento.tipo in ("accidente", "fallo_mecanico"):
                if random.random() < 0.5:
                    estado = "abandono"
                    puntuacion = -9999

    if estado != "abandono":
        prob_abandono = _probabilidad_abandono(piloto, monoplaza)

        if random.random() < prob_abandono:
            estado = "abandono"
            puntuacion = -9999
            eventos_aplicados.append("Abandono por fiabilidad")

    return puntuacion, estado, eventos_aplicados


def _ajustar_forma_piloto(piloto: Piloto, posicion: int, estado: str):
    """
    Ajusta la forma actual del piloto segun resultado.
    """

    if estado == "abandono":
        ajuste = -6.0
    elif posicion == 1:
        ajuste = 6.0
    elif posicion <= 3:
        ajuste = 4.0
    elif posicion <= 10:
        ajuste = 2.0
    else:
        ajuste = -1.5

    piloto.forma_actual = max(
        0.0,
        min(100.0, piloto.forma_actual + ajuste)
    )

    if hasattr(piloto, "actualizar_media"):
        piloto.actualizar_media()


def _limpiar_resultados_previos(carrera):
    """
    Elimina resultados anteriores de una carrera para evitar duplicados
    si se vuelve a simular.
    """

    Resultado.query.filter_by(carrera_id=carrera.id).delete()


def simular_carrera(carrera, recalcular_mercado=True, limpiar_previos=True) -> list:
    """
    Simula una carrera completa.

    Parametros:
    - carrera: instancia de Carrera
    - recalcular_mercado: si True, actualiza mercado al finalizar
    - limpiar_previos: si True, elimina resultados anteriores de esa carrera

    Retorna:
    - lista de resultados generados
    """

    pilotos = Piloto.query.filter_by(activo=True).all()

    if not pilotos:
        return []

    if limpiar_previos:
        _limpiar_resultados_previos(carrera)

    circuito = carrera.circuito
    ranking = []

    for piloto in pilotos:
        monoplaza = _obtener_monoplaza(piloto, carrera)
        score_base = _score_piloto(piloto, circuito, carrera)

        score_final, estado, eventos_aplicados = _aplicar_eventos(
            puntuacion=score_base,
            piloto=piloto,
            monoplaza=monoplaza,
            circuito=circuito
        )

        ranking.append({
            "piloto": piloto,
            "monoplaza": monoplaza,
            "score": score_final,
            "estado": estado,
            "eventos": eventos_aplicados
        })

    ranking.sort(key=lambda item: item["score"], reverse=True)

    resultados = []
    tiempo_base = 5400.0

    for posicion, item in enumerate(ranking, 1):
        piloto = item["piloto"]
        monoplaza = item["monoplaza"]
        estado = item["estado"]

        if estado == "abandono":
            tiempo = None
            puntos = 0.0
            vueltas = random.randint(1, 50)
            estado_jolpica = "Retired"
        else:
            diferencia = (posicion - 1) * random.uniform(0.5, 2.5)
            tiempo = round(tiempo_base + diferencia, 3)
            puntos = float(PUNTOS_F1.get(posicion, 0))
            vueltas = 58
            estado_jolpica = "Finished"

        equipo_id = None

        if monoplaza and monoplaza.equipo_id:
            equipo_id = monoplaza.equipo_id
        elif piloto.equipo_id:
            equipo_id = piloto.equipo_id

        resultado = Resultado(
            carrera_id=carrera.id,
            piloto_id=piloto.id,
            equipo_id=equipo_id,

            posicion=posicion,
            puntos=puntos,

            posicion_texto=str(posicion),
            posicion_salida=None,
            vueltas=vueltas,
            estado_jolpica=estado_jolpica,

            tiempo=tiempo,
            estado_final=estado
        )

        db.session.add(resultado)
        resultados.append(resultado)

        _ajustar_forma_piloto(
            piloto=piloto,
            posicion=posicion,
            estado=estado
        )

    carrera.estado = "completada"

    db.session.commit()

    if recalcular_mercado:
        actualizar_mercado(carrera)

    return resultados