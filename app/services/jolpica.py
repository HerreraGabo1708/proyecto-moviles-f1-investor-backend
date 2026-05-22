# app/services/jolpica.py

import requests


class JolpicaService:
    BASE_URL = "https://api.jolpi.ca/ergast/f1"

    @staticmethod
    def _get(endpoint, params=None):
        """
        Metodo interno para consumir la API de Jolpica.
        Todas las consultas externas pasan por aqui.
        """

        url = f"{JolpicaService.BASE_URL}/{endpoint}"

        try:
            response = requests.get(
                url,
                params=params,
                timeout=10
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            raise Exception("Tiempo de espera agotado al consultar Jolpica F1 API")

        except requests.exceptions.ConnectionError:
            raise Exception("No se pudo conectar con Jolpica F1 API")

        except requests.exceptions.HTTPError as error:
            raise Exception(f"Error HTTP consultando Jolpica F1 API: {str(error)}")

        except requests.exceptions.RequestException as error:
            raise Exception(f"Error consultando Jolpica F1 API: {str(error)}")

    # ==========================================================
    # HELPERS PARA EXTRAER DATOS
    # ==========================================================

    @staticmethod
    def extract_seasons(data):
        return data.get("MRData", {}).get("SeasonTable", {}).get("Seasons", [])

    @staticmethod
    def extract_drivers(data):
        return data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])

    @staticmethod
    def extract_constructors(data):
        return data.get("MRData", {}).get("ConstructorTable", {}).get("Constructors", [])

    @staticmethod
    def extract_races(data):
        return data.get("MRData", {}).get("RaceTable", {}).get("Races", [])

    @staticmethod
    def extract_driver_standings(data):
        standings_lists = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])

        if not standings_lists:
            return []

        return standings_lists[0].get("DriverStandings", [])

    @staticmethod
    def extract_constructor_standings(data):
        standings_lists = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])

        if not standings_lists:
            return []

        return standings_lists[0].get("ConstructorStandings", [])

    @staticmethod
    def extract_race_results(data):
        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])

        if not races:
            return []

        return races[0].get("Results", [])

    # ==========================================================
    # TEMPORADAS
    # ==========================================================

    @staticmethod
    def get_seasons(limit=30, offset=0):
        return JolpicaService._get(
            "seasons.json",
            params={
                "limit": limit,
                "offset": offset
            }
        )

    @staticmethod
    def get_current_season():
        return "current"

    # ==========================================================
    # PILOTOS
    # ==========================================================

    @staticmethod
    def get_drivers(season="current"):
        return JolpicaService._get(f"{season}/drivers.json")

    @staticmethod
    def get_driver_by_id(driver_id):
        return JolpicaService._get(f"drivers/{driver_id}.json")

    @staticmethod
    def get_driver_standings(season="current"):
        return JolpicaService._get(f"{season}/driverstandings.json")

    @staticmethod
    def get_driver_results(season="current", driver_id=None):
        if driver_id:
            return JolpicaService._get(f"{season}/drivers/{driver_id}/results.json")

        return JolpicaService._get(f"{season}/results.json")

    # ==========================================================
    # EQUIPOS / CONSTRUCTORES
    # ==========================================================

    @staticmethod
    def get_constructors(season="current"):
        return JolpicaService._get(f"{season}/constructors.json")

    @staticmethod
    def get_constructor_by_id(constructor_id):
        return JolpicaService._get(f"constructors/{constructor_id}.json")

    @staticmethod
    def get_constructor_standings(season="current"):
        return JolpicaService._get(f"{season}/constructorstandings.json")

    @staticmethod
    def get_constructor_results(season="current", constructor_id=None):
        if constructor_id:
            return JolpicaService._get(f"{season}/constructors/{constructor_id}/results.json")

        return JolpicaService._get(f"{season}/results.json")

    # ==========================================================
    # CARRERAS
    # ==========================================================

    @staticmethod
    def get_races(season="current"):
        return JolpicaService._get(f"{season}/races.json")

    @staticmethod
    def get_race_by_round(season="current", round_number="last"):
        return JolpicaService._get(f"{season}/{round_number}.json")

    @staticmethod
    def get_race_results(season="current", round_number="last"):
        return JolpicaService._get(f"{season}/{round_number}/results.json")

    @staticmethod
    def get_last_race_results(season="current"):
        return JolpicaService._get(f"{season}/last/results.json")

    # ==========================================================
    # CLASIFICACION / QUALIFYING
    # ==========================================================

    @staticmethod
    def get_qualifying_results(season="current", round_number="last"):
        return JolpicaService._get(f"{season}/{round_number}/qualifying.json")

    # ==========================================================
    # SPRINT
    # ==========================================================

    @staticmethod
    def get_sprint_results(season="current", round_number="last"):
        return JolpicaService._get(f"{season}/{round_number}/sprint.json")

    # ==========================================================
    # CIRCUITOS
    # ==========================================================

    @staticmethod
    def get_circuits(season="current"):
        return JolpicaService._get(f"{season}/circuits.json")

    @staticmethod
    def get_circuit_by_id(circuit_id):
        return JolpicaService._get(f"circuits/{circuit_id}.json")

    # ==========================================================
    # VUELTAS Y PIT STOPS
    # ==========================================================

    @staticmethod
    def get_laps(season="current", round_number="last"):
        return JolpicaService._get(f"{season}/{round_number}/laps.json")

    @staticmethod
    def get_pit_stops(season="current", round_number="last"):
        return JolpicaService._get(f"{season}/{round_number}/pitstops.json")