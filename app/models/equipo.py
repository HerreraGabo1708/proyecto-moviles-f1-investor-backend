from app import db


class Equipo(db.Model):
    __tablename__ = 'equipos'

    id                = db.Column(db.Integer, primary_key=True)
    nombre            = db.Column(db.String(100), nullable=False)
    rendimiento_coche = db.Column(db.Float, default=50.0)
    aerodinamica      = db.Column(db.Float, default=50.0)
    motor             = db.Column(db.Float, default=50.0)
    fiabilidad        = db.Column(db.Float, default=50.0)
    estrategia        = db.Column(db.Float, default=50.0)
    desarrollo        = db.Column(db.Float, default=50.0)
    media             = db.Column(db.Float, default=50.0)
    valor_mercado     = db.Column(db.Float, default=100_000.0)
    presupuesto       = db.Column(db.Float, default=500_000_000.0)
    imagen            = db.Column(db.String(255), nullable=True)

    pilotos = db.relationship('Piloto',  backref='equipo', lazy=True)
    mejoras = db.relationship('Mejora',  backref='equipo', lazy=True)

    def to_dict(self):
        return {
            'id':                self.id,
            'nombre':            self.nombre,
            'rendimiento_coche': self.rendimiento_coche,
            'aerodinamica':      self.aerodinamica,
            'motor':             self.motor,
            'fiabilidad':        self.fiabilidad,
            'estrategia':        self.estrategia,
            'desarrollo':        self.desarrollo,
            'media':             self.media,
            'valor_mercado':     self.valor_mercado,
            'presupuesto':       self.presupuesto,
            'imagen':            self.imagen,
        }
