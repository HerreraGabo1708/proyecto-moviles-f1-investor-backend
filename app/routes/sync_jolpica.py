# app/routes/sync_jolpica.py

from flask import Blueprint, jsonify, request
from app.services.sync_jolpica import SyncJolpicaService


sync_jolpica_bp = Blueprint(
    "sync_jolpica",
    __name__,
    url_prefix="/api/sync/jolpica"
)


@sync_jolpica_bp.route("/temporadas", methods=["POST"])
def sincronizar_temporadas():
    try:
        data = request.get_json(silent=True) or {}

        limit = data.get("limit", 30)
        offset = data.get("offset", 0)

        procesados = SyncJolpicaService.sincronizar_temporadas(
            limit=limit,
            offset=offset
        )

        return jsonify({
            "message": "Temporadas sincronizadas correctamente",
            "registros_procesados": procesados
        }), 200

    except Exception as error:
        return jsonify({
            "message": "Error sincronizando temporadas",
            "error": str(error)
        }), 500


@sync_jolpica_bp.route("/equipos", methods=["POST"])
def sincronizar_equipos():
    try:
        data = request.get_json(silent=True) or {}
        season = data.get("season", "current")

        procesados = SyncJolpicaService.sincronizar_equipos(season)

        return jsonify({
            "message": "Equipos sincronizados correctamente",
            "season": season,
            "registros_procesados": procesados
        }), 200

    except Exception as error:
        return jsonify({
            "message": "Error sincronizando equipos",
            "error": str(error)
        }), 500


@sync_jolpica_bp.route("/pilotos", methods=["POST"])
def sincronizar_pilotos():
    try:
        data = request.get_json(silent=True) or {}
        season = data.get("season", "current")

        procesados = SyncJolpicaService.sincronizar_pilotos(season)

        return jsonify({
            "message": "Pilotos sincronizados correctamente",
            "season": season,
            "registros_procesados": procesados
        }), 200

    except Exception as error:
        return jsonify({
            "message": "Error sincronizando pilotos",
            "error": str(error)
        }), 500


@sync_jolpica_bp.route("/calendario", methods=["POST"])
def sincronizar_calendario():
    try:
        data = request.get_json(silent=True) or {}
        season = data.get("season", "current")

        procesados = SyncJolpicaService.sincronizar_calendario(season)

        return jsonify({
            "message": "Calendario sincronizado correctamente",
            "season": season,
            "registros_procesados": procesados
        }), 200

    except Exception as error:
        return jsonify({
            "message": "Error sincronizando calendario",
            "error": str(error)
        }), 500


@sync_jolpica_bp.route("/resultados", methods=["POST"])
def sincronizar_resultados_carrera():
    try:
        data = request.get_json(silent=True) or {}

        season = data.get("season", "current")
        round_number = data.get("round_number", "last")
        actualizar_estado = data.get("actualizar_estado", True)

        procesados = SyncJolpicaService.sincronizar_resultados_carrera(
            season=season,
            round_number=round_number,
            actualizar_estado=actualizar_estado
        )

        return jsonify({
            "message": "Resultados sincronizados correctamente",
            "season": season,
            "round_number": round_number,
            "registros_procesados": procesados
        }), 200

    except Exception as error:
        return jsonify({
            "message": "Error sincronizando resultados",
            "error": str(error)
        }), 500


@sync_jolpica_bp.route("/temporada-completa", methods=["POST"])
def sincronizar_temporada_completa():
    try:
        data = request.get_json(silent=True) or {}

        season = data.get("season", "current")
        incluir_resultados = data.get("incluir_resultados", False)

        total = SyncJolpicaService.sincronizar_temporada_completa(
            season=season,
            incluir_resultados=incluir_resultados
        )

        return jsonify({
            "message": "Temporada sincronizada correctamente",
            "season": season,
            "incluir_resultados": incluir_resultados,
            "total": total
        }), 200

    except Exception as error:
        return jsonify({
            "message": "Error sincronizando temporada completa",
            "error": str(error)
        }), 500