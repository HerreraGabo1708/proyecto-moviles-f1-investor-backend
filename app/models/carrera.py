from app import db
from datetime import date, time


class Carrera(db.Model):
    __tablename__ = 'carreras'

    id = db.Column(db.Integer, primary_key=True)

    # Relaciones internas
    temporada_id = db.Column(db.Integer, db.ForeignKey('temporadas.id'), nullable=False)
    circuito_id = db.Column(db.Integer, db.ForeignKey('circuitos.id'), nullable=False)

    # Datos provenientes de Jolpica
    jolpica_id = db.Column(db.String(100), nullable=True, unique=True)
    temporada_anio = db.Column(db.Integer, nullable=True)
    round_number = db.Column(db.Integer, nullable=True)
    nombre_gp = db.Column(db.String(150), nullable=True)

    # Fecha y hora de la carrera
    fecha = db.Column(db.Date, nullable=True)
    hora = db.Column(db.Time, nullable=True)

    # Estado interno del juego
    estado = db.Column(db.String(20), default='pendiente')  # pendiente / completada

    resultados = db.relationship('Resultado', backref='carrera', lazy=True)

    def actualizar_estado_por_fecha(self):
        """
        Marca la carrera como completada si la fecha ya paso.
        Si no tiene fecha, se mantiene pendiente.
        """

        if not self.fecha:
            self.estado = 'pendiente'
            return self.estado

        if self.fecha < date.today():
            self.estado = 'completada'
        else:
            self.estado = 'pendiente'

        return self.estado

    def to_dict(self):
        return {
            'id': self.id,
            'temporada_id': self.temporada_id,
            'circuito_id': self.circuito_id,
            'circuito': self.circuito.nombre_gp if self.circuito else None,

            'jolpica_id': self.jolpica_id,
            'temporada_anio': self.temporada_anio,
            'round_number': self.round_number,
            'nombre_gp': self.nombre_gp,

            'fecha': self.fecha.isoformat() if self.fecha else None,
            'hora': self.hora.isoformat() if self.hora else None,
            'estado': self.estado,

            'resultados': [
                resultado.to_dict_basico() if hasattr(resultado, 'to_dict_basico') else {
                    'id': resultado.id
                }
                for resultado in self.resultados
            ]
        }

    def to_dict_basico(self):
        return {
            'id': self.id,
            'temporada_id': self.temporada_id,
            'circuito_id': self.circuito_id,
            'circuito': self.circuito.nombre_gp if self.circuito else None,
            'jolpica_id': self.jolpica_id,
            'temporada_anio': self.temporada_anio,
            'round_number': self.round_number,
            'nombre_gp': self.nombre_gp,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'hora': self.hora.isoformat() if self.hora else None,
            'estado': self.estado,
        }

    @staticmethod
    def from_jolpica(race_data, temporada_id, circuito_id):
        """
        Convierte una carrera de Jolpica en una instancia de Carrera.
        No guarda automaticamente en la base de datos.
        """

        season = race_data.get('season')
        round_value = race_data.get('round')

        try:
            temporada_anio = int(season) if season else None
        except ValueError:
            temporada_anio = None

        try:
            round_number = int(round_value) if round_value else None
        except ValueError:
            round_number = None

        fecha = None

        if race_data.get('date'):
            try:
                fecha = date.fromisoformat(race_data.get('date'))
            except ValueError:
                fecha = None

        hora = None

        if race_data.get('time'):
            try:
                clean_time = race_data.get('time').replace('Z', '')
                hora = time.fromisoformat(clean_time)
            except ValueError:
                hora = None

        jolpica_id = None

        if temporada_anio is not None and round_number is not None:
            jolpica_id = f"{temporada_anio}_{round_number}"

        carrera = Carrera(
            temporada_id=temporada_id,
            circuito_id=circuito_id,

            jolpica_id=jolpica_id,
            temporada_anio=temporada_anio,
            round_number=round_number,
            nombre_gp=race_data.get('raceName'),

            fecha=fecha,
            hora=hora,
            estado='pendiente'
        )

        carrera.actualizar_estado_por_fecha()

        return carrera