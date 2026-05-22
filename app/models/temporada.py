from app import db
from datetime import date


class Temporada(db.Model):
    __tablename__ = 'temporadas'

    id = db.Column(db.Integer, primary_key=True)

    # Datos principales
    anio = db.Column(db.Integer, nullable=False, unique=True)
    activa = db.Column(db.Boolean, default=False)

    # Fechas de la temporada
    fecha_inicio = db.Column(db.Date, nullable=True)
    fecha_fin = db.Column(db.Date, nullable=True)

    # Datos de integracion con Jolpica
    jolpica_id = db.Column(db.String(20), nullable=True, unique=True)
    sincronizada = db.Column(db.Boolean, default=False)
    ultima_sincronizacion = db.Column(db.DateTime, nullable=True)

    # Estado interno de la temporada
    estado = db.Column(db.String(30), default='pendiente')
    # pendiente / en_curso / finalizada

    carreras = db.relationship('Carrera', backref='temporada', lazy=True)

    def actualizar_estado(self):
        """
        Actualiza el estado de la temporada segun las fechas.
        """

        today = date.today()

        if self.fecha_inicio and today < self.fecha_inicio:
            self.estado = 'pendiente'
        elif self.fecha_fin and today > self.fecha_fin:
            self.estado = 'finalizada'
        else:
            self.estado = 'en_curso'

        return self.estado

    def to_dict(self):
        return {
            'id': self.id,
            'anio': self.anio,
            'activa': self.activa,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,

            'jolpica_id': self.jolpica_id,
            'sincronizada': self.sincronizada,
            'ultima_sincronizacion': self.ultima_sincronizacion.isoformat() if self.ultima_sincronizacion else None,
            'estado': self.estado,

            'total_carreras': len(self.carreras) if self.carreras else 0
        }

    def to_dict_basico(self):
        return {
            'id': self.id,
            'anio': self.anio,
            'activa': self.activa,
            'estado': self.estado,
            'jolpica_id': self.jolpica_id,
        }

    @staticmethod
    def from_jolpica(season_data):
        """
        Convierte una temporada de Jolpica en una instancia de Temporada.
        No guarda automaticamente en la base de datos.
        """

        season_value = season_data.get('season')

        try:
            anio = int(season_value)
        except (ValueError, TypeError):
            anio = None

        temporada = Temporada(
            anio=anio,
            activa=False,
            fecha_inicio=None,
            fecha_fin=None,
            jolpica_id=str(season_value) if season_value else None,
            sincronizada=False,
            estado='pendiente'
        )

        temporada.actualizar_estado()

        return temporada