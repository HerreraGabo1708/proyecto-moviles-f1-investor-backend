from app import db


class Circuito(db.Model):
    __tablename__ = 'circuitos'

    id = db.Column(db.Integer, primary_key=True)

    # Datos locales / visibles en el juego
    nombre_gp = db.Column(db.String(100), nullable=False)
    nombre_circuito = db.Column(db.String(100), nullable=False)
    pais = db.Column(db.String(80), nullable=False)

    # Datos externos provenientes de Jolpica
    jolpica_id = db.Column(db.String(100), nullable=True, unique=True)
    localidad = db.Column(db.String(100), nullable=True)
    latitud = db.Column(db.Float, nullable=True)
    longitud_geo = db.Column(db.Float, nullable=True)
    activo = db.Column(db.Boolean, default=True)

    # Datos internos de simulacion
    longitud = db.Column(db.Float, default=5.0)  # km
    num_curvas = db.Column(db.Integer, default=15)
    tipo_pista = db.Column(db.String(50), default='mixto')  # rapido/tecnico/mixto/callejero
    zonas_drs = db.Column(db.Integer, default=2)
    nivel_tecnico = db.Column(db.Float, default=50.0)
    nivel_desgaste = db.Column(db.Float, default=50.0)
    nivel_sobrepaso = db.Column(db.Float, default=50.0)

    # Multimedia
    imagen = db.Column(db.String(255), nullable=True)

    # Relaciones
    carreras = db.relationship('Carrera', backref='circuito', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre_gp': self.nombre_gp,
            'nombre_circuito': self.nombre_circuito,
            'pais': self.pais,

            'jolpica_id': self.jolpica_id,
            'localidad': self.localidad,
            'latitud': self.latitud,
            'longitud_geo': self.longitud_geo,
            'activo': self.activo,

            'longitud': self.longitud,
            'num_curvas': self.num_curvas,
            'tipo_pista': self.tipo_pista,
            'zonas_drs': self.zonas_drs,
            'nivel_tecnico': self.nivel_tecnico,
            'nivel_desgaste': self.nivel_desgaste,
            'nivel_sobrepaso': self.nivel_sobrepaso,
            'imagen': self.imagen,

            'carreras': [
                carrera.to_dict_basico() if hasattr(carrera, 'to_dict_basico') else {
                    'id': carrera.id
                }
                for carrera in self.carreras
            ]
        }

    def to_dict_basico(self):
        return {
            'id': self.id,
            'nombre_gp': self.nombre_gp,
            'nombre_circuito': self.nombre_circuito,
            'pais': self.pais,
            'jolpica_id': self.jolpica_id,
            'localidad': self.localidad,
            'latitud': self.latitud,
            'longitud_geo': self.longitud_geo,
            'tipo_pista': self.tipo_pista,
            'imagen': self.imagen,
        }

    @staticmethod
    def from_jolpica(race_data):
        """
        Convierte el circuito incluido en una carrera de Jolpica
        en una instancia de Circuito.
        No guarda automaticamente en la base de datos.
        """

        circuit_data = race_data.get('Circuit', {})
        location_data = circuit_data.get('Location', {})

        latitud = None
        longitud_geo = None

        try:
            latitud = float(location_data.get('lat')) if location_data.get('lat') else None
        except ValueError:
            latitud = None

        try:
            longitud_geo = float(location_data.get('long')) if location_data.get('long') else None
        except ValueError:
            longitud_geo = None

        circuito = Circuito(
            nombre_gp=race_data.get('raceName'),
            nombre_circuito=circuit_data.get('circuitName'),
            pais=location_data.get('country'),

            jolpica_id=circuit_data.get('circuitId'),
            localidad=location_data.get('locality'),
            latitud=latitud,
            longitud_geo=longitud_geo,
            activo=True,

            longitud=5.0,
            num_curvas=15,
            tipo_pista='mixto',
            zonas_drs=2,
            nivel_tecnico=50.0,
            nivel_desgaste=50.0,
            nivel_sobrepaso=50.0,

            imagen=None
        )

        return circuito