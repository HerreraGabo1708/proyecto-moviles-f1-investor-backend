from app import db


class Equipo(db.Model):
    __tablename__ = 'equipos'

    id = db.Column(db.Integer, primary_key=True)

    # Datos locales / visibles en el juego
    nombre = db.Column(db.String(100), nullable=False)

    # Datos externos provenientes de Jolpica
    jolpica_id = db.Column(db.String(100), nullable=True, unique=True)
    nacionalidad = db.Column(db.String(100), nullable=True)
    temporada = db.Column(db.Integer, nullable=True)
    activo = db.Column(db.Boolean, default=True)

    # Atributos de simulacion del equipo
    rendimiento_coche = db.Column(db.Float, default=50.0)
    aerodinamica = db.Column(db.Float, default=50.0)
    motor = db.Column(db.Float, default=50.0)
    fiabilidad = db.Column(db.Float, default=50.0)
    estrategia = db.Column(db.Float, default=50.0)
    desarrollo = db.Column(db.Float, default=50.0)
    media = db.Column(db.Float, default=50.0)

    # Mercado
    valor_mercado = db.Column(db.Float, default=100_000.0)
    presupuesto = db.Column(db.Float, default=500_000_000.0)

    # Multimedia
    imagen = db.Column(db.String(255), nullable=True)

    # Relaciones
    pilotos = db.relationship('Piloto', backref='equipo', lazy=True)
    mejoras = db.relationship('Mejora', backref='equipo', lazy=True)

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

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,

            'jolpica_id': self.jolpica_id,
            'nacionalidad': self.nacionalidad,
            'temporada': self.temporada,
            'activo': self.activo,

            'rendimiento_coche': self.rendimiento_coche,
            'aerodinamica': self.aerodinamica,
            'motor': self.motor,
            'fiabilidad': self.fiabilidad,
            'estrategia': self.estrategia,
            'desarrollo': self.desarrollo,
            'media': self.media,
            'valor_mercado': self.valor_mercado,
            'presupuesto': self.presupuesto,
            'imagen': self.imagen,

            'pilotos': [
                piloto.to_dict_basico() if hasattr(piloto, 'to_dict_basico') else {
                    'id': piloto.id,
                    'nombre': piloto.nombre,
                    'numero': piloto.numero
                }
                for piloto in self.pilotos
            ]
        }

    def to_dict_basico(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'jolpica_id': self.jolpica_id,
            'nacionalidad': self.nacionalidad,
            'media': self.media,
            'valor_mercado': self.valor_mercado,
            'imagen': self.imagen,
        }

    @staticmethod
    def from_jolpica(constructor_data, temporada=None):
        """
        Convierte un constructor de Jolpica en una instancia de Equipo.
        No guarda automaticamente en la base de datos.
        """

        equipo = Equipo(
            nombre=constructor_data.get('name'),
            jolpica_id=constructor_data.get('constructorId'),
            nacionalidad=constructor_data.get('nationality'),
            temporada=temporada,
            activo=True,

            rendimiento_coche=50.0,
            aerodinamica=50.0,
            motor=50.0,
            fiabilidad=50.0,
            estrategia=50.0,
            desarrollo=50.0,
            media=50.0,

            valor_mercado=100_000.0,
            presupuesto=500_000_000.0,
            imagen=None
        )

        return equipo