# app/services/sync_jolpica.py

"""
Servicio de sincronizacion con Jolpica F1 API.

Este archivo toma datos externos de Jolpica y los guarda o actualiza
en los modelos internos del sistema F1 Investor.

Sincroniza:
- Temporadas
- Equipos / Constructores
- Pilotos
- Circuitos
- Carreras
- Resultados
"""

from datetime import datetime, date

from app import db

from app.models.temporada import Temporada
from app.models.equipo import Equipo
from app.models.piloto import Piloto
from app.models.circuito import Circuito
from app.models.carrera import Carrera
from app.models.resultado import Resultado
from app.models.sync_log import SyncLog

from app.services.jolpica import JolpicaService


class SyncJolpicaService:

    # ==========================================================
    # LOGS
    # ==========================================================

    @staticmethod
    def _crear_log(endpoint, temporada=None, estado="exitoso", mensaje=None, registros_procesados=0):
        log = SyncLog(
            fuente="jolpica",
            endpoint=endpoint,
            temporada=temporada,
            estado=estado,
            mensaje=mensaje,
            registros_procesados=registros_procesados
        )

        db.session.add(log)
        return log

    # ==========================================================
    # HELPERS
    # ==========================================================

    @staticmethod
    def _parse_int(value, default=None):
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _parse_float(value, default=0.0):
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _parse_date(value):
        if not value:
            return None

        try:
            return date.fromisoformat(value)
        except ValueError:
            return None

    @staticmethod
    def _parse_time(value):
        if not value:
            return None

        try:
            clean_value = value.replace("Z", "")
            return datetime.strptime(clean_value, "%H:%M:%S").time()
        except ValueError:
            return None

    # ==========================================================
    # TEMPORADA
    # ==========================================================

    @staticmethod
    def crear_o_actualizar_temporada(anio):
        anio = SyncJolpicaService._parse_int(anio)

        if not anio:
            raise ValueError("El año de temporada no es valido")

        temporada = Temporada.query.filter_by(anio=anio).first()

        if not temporada:
            temporada = Temporada(
                anio=anio,
                activa=False,
                fecha_inicio=None,
                fecha_fin=None,
                jolpica_id=str(anio),
                sincronizada=False,
                ultima_sincronizacion=None,
                estado="pendiente"
            )

            db.session.add(temporada)

        else:
            temporada.jolpica_id = temporada.jolpica_id or str(anio)

        return temporada

    @staticmethod
    def sincronizar_temporadas(limit=30, offset=0):
        endpoint = f"seasons.json?limit={limit}&offset={offset}"

        try:
            data = JolpicaService.get_seasons(limit=limit, offset=offset)
            seasons = JolpicaService.extract_seasons(data)

            procesados = 0

            for item in seasons:
                season_value = item.get("season")
                anio = SyncJolpicaService._parse_int(season_value)

                if not anio:
                    continue

                SyncJolpicaService.crear_o_actualizar_temporada(anio)
                procesados += 1

            SyncJolpicaService._crear_log(
                endpoint=endpoint,
                estado="exitoso",
                registros_procesados=procesados
            )

            db.session.commit()
            return procesados

        except Exception as error:
            db.session.rollback()

            SyncJolpicaService._crear_log(
                endpoint=endpoint,
                estado="error",
                mensaje=str(error),
                registros_procesados=0
            )

            db.session.commit()
            raise error

    # ==========================================================
    # EQUIPOS / CONSTRUCTORES
    # ==========================================================

    @staticmethod
    def crear_o_actualizar_equipo(constructor_data, temporada_anio=None):
        jolpica_id = constructor_data.get("constructorId")

        if not jolpica_id:
            return None

        equipo = Equipo.query.filter_by(jolpica_id=jolpica_id).first()

        if not equipo:
            equipo = Equipo.from_jolpica(
                constructor_data=constructor_data,
                temporada=temporada_anio
            )

            db.session.add(equipo)

        else:
            equipo.nombre = constructor_data.get("name") or equipo.nombre
            equipo.nacionalidad = constructor_data.get("nationality") or equipo.nacionalidad
            equipo.temporada = temporada_anio or equipo.temporada
            equipo.activo = True

        return equipo

    @staticmethod
    def sincronizar_equipos(season="current"):
        endpoint = f"{season}/constructors.json"

        try:
            data = JolpicaService.get_constructors(season)
            constructors = JolpicaService.extract_constructors(data)

            temporada_anio = SyncJolpicaService._parse_int(season)
            procesados = 0

            for constructor_data in constructors:
                equipo = SyncJolpicaService.crear_o_actualizar_equipo(
                    constructor_data=constructor_data,
                    temporada_anio=temporada_anio
                )

                if equipo:
                    procesados += 1

            SyncJolpicaService._crear_log(
                endpoint=endpoint,
                temporada=temporada_anio,
                estado="exitoso",
                registros_procesados=procesados
            )

            db.session.commit()
            return procesados

        except Exception as error:
            db.session.rollback()

            SyncJolpicaService._crear_log(
                endpoint=endpoint,
                temporada=SyncJolpicaService._parse_int(season),
                estado="error",
                mensaje=str(error),
                registros_procesados=0
            )

            db.session.commit()
            raise error

    # ==========================================================
    # PILOTOS
    # ==========================================================

    @staticmethod
    def crear_o_actualizar_piloto(driver_data, temporada_anio=None, equipo_id=None):
        jolpica_id = driver_data.get("driverId")

        if not jolpica_id:
            return None

        piloto = Piloto.query.filter_by(jolpica_id=jolpica_id).first()

        if not piloto:
            piloto = Piloto.from_jolpica(
                driver_data=driver_data,
                temporada=temporada_anio
            )

            piloto.equipo_id = equipo_id
            db.session.add(piloto)

        else:
            given_name = driver_data.get("givenName", "")
            family_name = driver_data.get("familyName", "")
            full_name = f"{given_name} {family_name}".strip()

            piloto.nombre = full_name or piloto.nombre
            piloto.codigo = driver_data.get("code") or piloto.codigo
            piloto.nacionalidad = driver_data.get("nationality") or piloto.nacionalidad
            piloto.temporada = temporada_anio or piloto.temporada
            piloto.activo = True

            permanent_number = driver_data.get("permanentNumber")
            numero = SyncJolpicaService._parse_int(permanent_number)

            if numero is not None:
                piloto.numero = numero

            fecha_nacimiento = SyncJolpicaService._parse_date(driver_data.get("dateOfBirth"))

            if fecha_nacimiento:
                piloto.fecha_nacimiento = fecha_nacimiento

            if equipo_id:
                piloto.equipo_id = equipo_id

        return piloto

    @staticmethod
    def sincronizar_pilotos(season="current"):
        endpoint = f"{season}/driverstandings.json"

        try:
            data = JolpicaService.get_driver_standings(season)
            standings = JolpicaService.extract_driver_standings(data)

            temporada_anio = SyncJolpicaService._parse_int(season)
            procesados = 0

            for item in standings:
                driver_data = item.get("Driver", {})
                constructors = item.get("Constructors", [])

                equipo_id = None

                if constructors:
                    constructor_data = constructors[0]
                    equipo = SyncJolpicaService.crear_o_actualizar_equipo(
                        constructor_data=constructor_data,
                        temporada_anio=temporada_anio
                    )

                    if equipo:
                        db.session.flush()
                        equipo_id = equipo.id

                piloto = SyncJolpicaService.crear_o_actualizar_piloto(
                    driver_data=driver_data,
                    temporada_anio=temporada_anio,
                    equipo_id=equipo_id
                )

                if piloto:
                    procesados += 1

            SyncJolpicaService._crear_log(
                endpoint=endpoint,
                temporada=temporada_anio,
                estado="exitoso",
                registros_procesados=procesados
            )

            db.session.commit()
            return procesados

        except Exception as error:
            db.session.rollback()

            SyncJolpicaService._crear_log(
                endpoint=endpoint,
                temporada=SyncJolpicaService._parse_int(season),
                estado="error",
                mensaje=str(error),
                registros_procesados=0
            )

            db.session.commit()
            raise error

    # ==========================================================
    # CIRCUITOS
    # ==========================================================

    @staticmethod
    def crear_o_actualizar_circuito(race_data):
        circuit_data = race_data.get("Circuit", {})
        location_data = circuit_data.get("Location", {})

        jolpica_id = circuit_data.get("circuitId")

        if not jolpica_id:
            return None

        circuito = Circuito.query.filter_by(jolpica_id=jolpica_id).first()

        if not circuito:
            circuito = Circuito.from_jolpica(race_data)
            db.session.add(circuito)

        else:
            circuito.nombre_gp = race_data.get("raceName") or circuito.nombre_gp
            circuito.nombre_circuito = circuit_data.get("circuitName") or circuito.nombre_circuito
            circuito.pais = location_data.get("country") or circuito.pais
            circuito.localidad = location_data.get("locality") or circuito.localidad
            circuito.latitud = SyncJolpicaService._parse_float(location_data.get("lat"), circuito.latitud)
            circuito.longitud_geo = SyncJolpicaService._parse_float(location_data.get("long"), circuito.longitud_geo)
            circuito.activo = True

        return circuito

    # ==========================================================
    # CARRERAS
    # ==========================================================

    @staticmethod
    def crear_o_actualizar_carrera(race_data, temporada_id, circuito_id):
        season = SyncJolpicaService._parse_int(race_data.get("season"))
        round_number = SyncJolpicaService._parse_int(race_data.get("round"))

        if not season or not round_number:
            return None

        jolpica_id = f"{season}_{round_number}"

        carrera = Carrera.query.filter_by(jolpica_id=jolpica_id).first()

        if not carrera:
            carrera = Carrera.from_jolpica(
                race_data=race_data,
                temporada_id=temporada_id,
                circuito_id=circuito_id
            )

            db.session.add(carrera)

        else:
            carrera.temporada_id = temporada_id
            carrera.circuito_id = circuito_id
            carrera.temporada_anio = season
            carrera.round_number = round_number
            carrera.nombre_gp = race_data.get("raceName") or carrera.nombre_gp
            carrera.fecha = SyncJolpicaService._parse_date(race_data.get("date"))
            carrera.hora = SyncJolpicaService._parse_time(race_data.get("time"))

            if carrera.fecha and carrera.fecha < date.today():
                carrera.estado = "completada"
            else:
                carrera.estado = "pendiente"

        return carrera

    @staticmethod
    def sincronizar_calendario(season="current"):
        endpoint = f"{season}/races.json"

        try:
            data = JolpicaService.get_races(season)
            races = JolpicaService.extract_races(data)

            temporada_anio = None

            if races:
                temporada_anio = SyncJolpicaService._parse_int(races[0].get("season"))

            if not temporada_anio:
                temporada_anio = SyncJolpicaService._parse_int(season)

            if not temporada_anio:
                raise ValueError("No se pudo determinar la temporada del calendario")

            temporada = SyncJolpicaService.crear_o_actualizar_temporada(temporada_anio)
            db.session.flush()

            procesados = 0
            fechas = []

            for race_data in races:
                circuito = SyncJolpicaService.crear_o_actualizar_circuito(race_data)
                db.session.flush()

                if not circuito:
                    continue

                carrera = SyncJolpicaService.crear_o_actualizar_carrera(
                    race_data=race_data,
                    temporada_id=temporada.id,
                    circuito_id=circuito.id
                )

                if carrera:
                    procesados += 1

                    if carrera.fecha:
                        fechas.append(carrera.fecha)

            if fechas:
                temporada.fecha_inicio = min(fechas)
                temporada.fecha_fin = max(fechas)

            temporada.sincronizada = True
            temporada.ultima_sincronizacion = datetime.utcnow()

            if temporada.fecha_inicio and date.today() < temporada.fecha_inicio:
                temporada.estado = "pendiente"
            elif temporada.fecha_fin and date.today() > temporada.fecha_fin:
                temporada.estado = "finalizada"
            else:
                temporada.estado = "en_curso"

            SyncJolpicaService._crear_log(
                endpoint=endpoint,
                temporada=temporada_anio,
                estado="exitoso",
                registros_procesados=procesados
            )

            db.session.commit()
            return procesados

        except Exception as error:
            db.session.rollback()

            SyncJolpicaService._crear_log(
                endpoint=endpoint,
                temporada=SyncJolpicaService._parse_int(season),
                estado="error",
                mensaje=str(error),
                registros_procesados=0
            )

            db.session.commit()
            raise error

    # ==========================================================
    # RESULTADOS
    # ==========================================================

    @staticmethod
    def crear_o_actualizar_resultado(result_data, carrera, piloto, equipo=None):
        driver_data = result_data.get("Driver", {})
        driver_id = driver_data.get("driverId")

        if not driver_id:
            return None

        jolpica_id = f"race_{carrera.id}_driver_{driver_id}"

        resultado = Resultado.query.filter_by(jolpica_id=jolpica_id).first()

        equipo_id = equipo.id if equipo else None

        if not resultado:
            resultado = Resultado.from_jolpica(
                result_data=result_data,
                carrera_id=carrera.id,
                piloto_id=piloto.id,
                equipo_id=equipo_id
            )

            resultado.jolpica_id = jolpica_id
            db.session.add(resultado)

        else:
            resultado.piloto_id = piloto.id
            resultado.equipo_id = equipo_id
            resultado.posicion = SyncJolpicaService._parse_int(result_data.get("position"), 0)
            resultado.puntos = SyncJolpicaService._parse_float(result_data.get("points"), 0.0)
            resultado.posicion_texto = result_data.get("positionText")
            resultado.posicion_salida = SyncJolpicaService._parse_int(result_data.get("grid"))
            resultado.vueltas = SyncJolpicaService._parse_int(result_data.get("laps"))
            resultado.estado_jolpica = result_data.get("status")
            resultado.tiempo = None

            if hasattr(resultado, "normalizar_estado_final"):
                resultado.normalizar_estado_final()

        return resultado

    @staticmethod
    def sincronizar_resultados_carrera(season="current", round_number="last", actualizar_estado=True):
        endpoint = f"{season}/{round_number}/results.json"

        try:
            data = JolpicaService.get_race_results(season, round_number)
            races = JolpicaService.extract_races(data)

            if not races:
                SyncJolpicaService._crear_log(
                    endpoint=endpoint,
                    temporada=SyncJolpicaService._parse_int(season),
                    estado="exitoso",
                    mensaje="No se encontraron carreras con resultados",
                    registros_procesados=0
                )

                db.session.commit()
                return 0

            race_data = races[0]
            results = race_data.get("Results", [])

            temporada_anio = SyncJolpicaService._parse_int(race_data.get("season"))
            round_real = SyncJolpicaService._parse_int(race_data.get("round"))

            temporada = SyncJolpicaService.crear_o_actualizar_temporada(temporada_anio)
            db.session.flush()

            circuito = SyncJolpicaService.crear_o_actualizar_circuito(race_data)
            db.session.flush()

            carrera = SyncJolpicaService.crear_o_actualizar_carrera(
                race_data=race_data,
                temporada_id=temporada.id,
                circuito_id=circuito.id
            )
            db.session.flush()

            procesados = 0

            for result_data in results:
                driver_data = result_data.get("Driver", {})
                constructor_data = result_data.get("Constructor", {})

                equipo = SyncJolpicaService.crear_o_actualizar_equipo(
                    constructor_data=constructor_data,
                    temporada_anio=temporada_anio
                )
                db.session.flush()

                equipo_id = equipo.id if equipo else None

                piloto = SyncJolpicaService.crear_o_actualizar_piloto(
                    driver_data=driver_data,
                    temporada_anio=temporada_anio,
                    equipo_id=equipo_id
                )
                db.session.flush()

                if not piloto:
                    continue

                resultado = SyncJolpicaService.crear_o_actualizar_resultado(
                    result_data=result_data,
                    carrera=carrera,
                    piloto=piloto,
                    equipo=equipo
                )

                if resultado:
                    procesados += 1

            if actualizar_estado:
                carrera.estado = "completada"

            temporada.sincronizada = True
            temporada.ultima_sincronizacion = datetime.utcnow()

            SyncJolpicaService._crear_log(
                endpoint=endpoint,
                temporada=temporada_anio,
                estado="exitoso",
                registros_procesados=procesados
            )

            db.session.commit()
            return procesados

        except Exception as error:
            db.session.rollback()

            SyncJolpicaService._crear_log(
                endpoint=endpoint,
                temporada=SyncJolpicaService._parse_int(season),
                estado="error",
                mensaje=str(error),
                registros_procesados=0
            )

            db.session.commit()
            raise error

    # ==========================================================
    # SINCRONIZACION COMPLETA
    # ==========================================================

    @staticmethod
    def sincronizar_temporada_completa(season="current", incluir_resultados=False):
        """
        Sincroniza datos principales de una temporada.

        Si incluir_resultados=True, tambien intenta sincronizar resultados
        de todas las carreras del calendario.
        """

        total = {
            "equipos": 0,
            "pilotos": 0,
            "carreras": 0,
            "resultados": 0
        }

        total["equipos"] = SyncJolpicaService.sincronizar_equipos(season)
        total["pilotos"] = SyncJolpicaService.sincronizar_pilotos(season)
        total["carreras"] = SyncJolpicaService.sincronizar_calendario(season)

        if incluir_resultados:
            carreras = Carrera.query.filter_by(
                temporada_anio=SyncJolpicaService._parse_int(season)
            ).all()

            for carrera in carreras:
                if carrera.round_number:
                    try:
                        total["resultados"] += SyncJolpicaService.sincronizar_resultados_carrera(
                            season=season,
                            round_number=carrera.round_number
                        )
                    except Exception:
                        continue

        return total