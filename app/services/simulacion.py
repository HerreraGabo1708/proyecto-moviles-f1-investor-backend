"""
Servicio de simulación de carrera.
Genera resultados basados en estadísticas de pilotos, equipos,
monoplazas, circuito y eventos adversos.
"""
import random
from app import db
from app.models.piloto    import Piloto
from app.models.monoplaza import Monoplaza
from app.models.resultado import Resultado
from app.models.evento    import Evento

PUNTOS_F1 = {1:25, 2:18, 3:15, 4:12, 5:10, 6:8, 7:6, 8:4, 9:2, 10:1}


def _score_piloto(piloto: Piloto, circuito) -> float:
    habilidad = (
        piloto.skill        * 0.30 +
        piloto.racecraft    * 0.20 +
        piloto.consistencia * 0.20 +
        piloto.experiencia  * 0.15 +
        piloto.forma_actual * 0.15
    )

    mono = Monoplaza.query.filter_by(piloto_id=piloto.id).first()
    if mono:
        coche = (
            (mono.velocidad_punta / 3.5) * 0.35 +
            mono.aceleracion             * 0.25 +
            mono.aerodinamica            * 0.25 +
            mono.fiabilidad              * 0.15
        )
    else:
        coche = 50.0

    # Bonificación según tipo de circuito
    bonus = 0.0
    if circuito.tipo_pista in ('tecnico', 'callejero'):
        bonus = (piloto.racecraft - 50) * 0.3
    elif circuito.tipo_pista == 'rapido':
        bonus = ((mono.velocidad_punta / 3) - 33) * 0.2 if mono else 0

    ruido = random.gauss(0, 4)   # variabilidad realista
    return habilidad * 0.55 + coche * 0.45 + bonus + ruido


def _aplicar_eventos(puntuacion: float) -> tuple:
    eventos  = Evento.query.all()
    estado   = 'finalizado'
    for evento in eventos:
        if random.random() < evento.probabilidad:
            puntuacion += evento.efecto_valor
            if evento.tipo in ('accidente', 'fallo_mecanico') and random.random() < 0.5:
                estado     = 'abandono'
                puntuacion = -9999
    return puntuacion, estado


def simular_carrera(carrera) -> list:
    pilotos = Piloto.query.all()
    if not pilotos:
        return []

    circuito = carrera.circuito
    ranking  = []
    for piloto in pilotos:
        score, estado = _aplicar_eventos(_score_piloto(piloto, circuito))
        ranking.append((piloto, score, estado))

    ranking.sort(key=lambda x: x[1], reverse=True)

    resultados  = []
    tiempo_base = 5400.0   # ~90 min en segundos
    for pos, (piloto, _, estado) in enumerate(ranking, 1):
        tiempo = None if estado == 'abandono' else tiempo_base + (pos-1) * random.uniform(0.5, 2.5)
        puntos = 0 if estado == 'abandono' else PUNTOS_F1.get(pos, 0)

        res = Resultado(
            carrera_id   = carrera.id,
            piloto_id    = piloto.id,
            posicion     = pos,
            puntos       = puntos,
            tiempo       = tiempo,
            estado_final = estado,
        )
        db.session.add(res)
        resultados.append(res)

        # Ajustar forma según posición
        ajuste = max(-10, min(10, (10 - pos) * 1.5))
        piloto.forma_actual = max(0, min(100, piloto.forma_actual + ajuste))

    db.session.commit()
    return resultados
