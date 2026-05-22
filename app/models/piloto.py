from app import db
from datetime import date


class Piloto(db.Model):
    __tablename__ = 'pilotos'

    id = db.Column(db.Integer, primary_key=True)

    # Datos locales / visibles en el juego
    nombre = db.Column(db.String(100), nullable=False)
    numero = db.Column(db.Integer, nullable=True)
    edad = db.Column(db.Integer, default=20)

    # Relacion con equipo interno del juego
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=True)

    # Datos externos provenientes de Jolpica
    jolpica_id = db.Column(db.String(100), nullable=True, unique=True)
    codigo = db.Column(db.String(10), nullable=True)
    nacionalidad = db.Column(db.String(100), nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    temporada = db.Column(db.Integer, nullable=True)
    activo = db.Column(db.Boolean, default=True)

    # Atributos de simulacion
    skill = db.Column(db.Float, default=50.0)
    consistencia = db.Column(db.Float, default=50.0)
    racecraft = db.Column(db.Float, default=50.0)
    experiencia = db.Column(db.Float, default=50.0)
    potencial = db.Column(db.Float, default=50.0)
    media = db.Column(db.Float, default=50.0)

    # Mercado
    valor_mercado = db.Column(db.Float, default=50_000.0)
    forma_actual = db.Column(db.Float, default=50.0)

    # Multimedia
    foto = db.Column(db.String(255), nullable=True)

    # Relaciones
    monoplaza = db.relationship('Monoplaza', backref='piloto', uselist=False, lazy=True)
    resultados = db.relationship('Resultado', backref='piloto', lazy=True)

    def calcular_edad(self):
        if not self.fecha_nacimiento:
            return self.edad

        today = date.today()

        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) <
            (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def actualizar_media(self):
        self.media = round((
            self.skill +
            self.consistencia +
            self.racecraft +
            self.experiencia +
            self.potencial
        ) / 5, 2)

        return self.media

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'numero': self.numero,
            'edad': self.calcular_edad(),
            'equipo_id': self.equipo_id,
            'equipo': self.equipo.nombre if self.equipo else None,

            'jolpica_id': self.jolpica_id,
            'codigo': self.codigo,
            'nacionalidad': self.nacionalidad,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'temporada': self.temporada,
            'activo': self.activo,

            'skill': self.skill,
            'consistencia': self.consistencia,
            'racecraft': self.racecraft,
            'experiencia': self.experiencia,
            'potencial': self.potencial,
            'media': self.media,
            'valor_mercado': self.valor_mercado,
            'forma_actual': self.forma_actual,
            'foto': self.foto,
        }

    @staticmethod
    def from_jolpica(driver_data, temporada=None):
        """
        Convierte un piloto de Jolpica en una instancia de Piloto.
        No guarda automaticamente en la base de datos.
        """

        full_name = f"{driver_data.get('givenName', '')} {driver_data.get('familyName', '')}".strip()

        permanent_number = driver_data.get('permanentNumber')

        try:
            numero = int(permanent_number) if permanent_number else None
        except ValueError:
            numero = None

        fecha_nacimiento = None

        if driver_data.get('dateOfBirth'):
            try:
                fecha_nacimiento = date.fromisoformat(driver_data.get('dateOfBirth'))
            except ValueError:
                fecha_nacimiento = None

        piloto = Piloto(
            nombre=full_name,
            numero=numero,
            edad=20,
            jolpica_id=driver_data.get('driverId'),
            codigo=driver_data.get('code'),
            nacionalidad=driver_data.get('nationality'),
            fecha_nacimiento=fecha_nacimiento,
            temporada=temporada,
            activo=True,

            skill=50.0,
            consistencia=50.0,
            racecraft=50.0,
            experiencia=50.0,
            potencial=50.0,
            media=50.0,
            valor_mercado=50_000.0,
            forma_actual=50.0,
            foto=None
        )

        return piloto
