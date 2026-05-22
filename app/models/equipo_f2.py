from app import db


class EquipoF2(db.Model):
    __tablename__ = 'equipos_f2'

    id = db.Column(db.Integer, primary_key=True)

    # Datos principales
    nombre = db.Column(db.String(100), nullable=False)
    nacionalidad = db.Column(db.String(100), nullable=True)

    # Datos internos de simulacion
    rendimiento_coche = db.Column(db.Float, default=50.0)
    aerodinamica = db.Column(db.Float, default=50.0)
    motor = db.Column(db.Float, default=50.0)
    fiabilidad = db.Column(db.Float, default=50.0)
    estrategia = db.Column(db.Float, default=50.0)
    desarrollo = db.Column(db.Float, default=50.0)
    media = db.Column(db.Float, default=50.0)

    # Mercado y presupuesto
    valor_mercado = db.Column(db.Float, default=50_000.0)
    presupuesto = db.Column(db.Float, default=100_000_000.0)

    # Temporada / estado
    temporada_id = db.Column(db.Integer, db.ForeignKey('temporadas.id'), nullable=True)
    activo = db.Column(db.Boolean, default=True)

    # Multimedia
    imagen = db.Column(db.String(255), nullable=True)

    # Relaciones
    temporada = db.relationship('Temporada', backref='equipos_f2', lazy=True)

    def actualizar_media(self):
        self.media = round((
            self.rendimiento_coche +
            self.aerodinamica +
            self.motor +
            self.fiabilidad +
            self.estrategia +
            self.desarrollo
        ) / 6, 2)

        return self.media

    def mejorar_atributo(self, atributo, incremento):
        """
        Mejora un atributo del equipo F2.
        """

        if incremento <= 0:
            raise ValueError("El incremento debe ser mayor a cero")

        atributos_validos = [
            'rendimiento_coche',
            'aerodinamica',
            'motor',
            'fiabilidad',
            'estrategia',
            'desarrollo'
        ]

        if atributo not in atributos_validos:
            raise ValueError("Atributo no valido para EquipoF2")

        valor_actual = getattr(self, atributo)
        setattr(self, atributo, min(100.0, valor_actual + incremento))

        self.actualizar_media()
        return self

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'nacionalidad': self.nacionalidad,

            'rendimiento_coche': self.rendimiento_coche,
            'aerodinamica': self.aerodinamica,
            'motor': self.motor,
            'fiabilidad': self.fiabilidad,
            'estrategia': self.estrategia,
            'desarrollo': self.desarrollo,
            'media': self.media,

            'valor_mercado': self.valor_mercado,
            'presupuesto': self.presupuesto,

            'temporada_id': self.temporada_id,
            'temporada': self.temporada.anio if self.temporada else None,
            'activo': self.activo,

            'imagen': self.imagen,
        }

    def to_dict_basico(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'nacionalidad': self.nacionalidad,
            'media': self.media,
            'valor_mercado': self.valor_mercado,
            'temporada_id': self.temporada_id,
            'activo': self.activo,
            'imagen': self.imagen,
        }

    @staticmethod
    def crear_equipo_base(nombre, temporada_id=None, nacionalidad=None):
        """
        Crea un equipo F2 base.
        No guarda automaticamente en la base de datos.
        """

        equipo = EquipoF2(
            nombre=nombre,
            nacionalidad=nacionalidad,
            rendimiento_coche=50.0,
            aerodinamica=50.0,
            motor=50.0,
            fiabilidad=50.0,
            estrategia=50.0,
            desarrollo=50.0,
            media=50.0,
            valor_mercado=50_000.0,
            presupuesto=100_000_000.0,
            temporada_id=temporada_id,
            activo=True,
            imagen=None
        )

        return equipo    