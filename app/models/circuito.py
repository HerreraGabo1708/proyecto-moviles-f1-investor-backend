from app import db


class Circuito(db.Model):
    __tablename__ = 'circuitos'

    id               = db.Column(db.Integer, primary_key=True)
    nombre_gp        = db.Column(db.String(100), nullable=False)
    nombre_circuito  = db.Column(db.String(100), nullable=False)
    pais             = db.Column(db.String(80),  nullable=False)
    longitud         = db.Column(db.Float,  default=5.0)     # km
    num_curvas       = db.Column(db.Integer, default=15)
    tipo_pista       = db.Column(db.String(50), default='mixto')  # rapido/tecnico/mixto/callejero
    zonas_drs        = db.Column(db.Integer, default=2)
    nivel_tecnico    = db.Column(db.Float, default=50.0)
    nivel_desgaste   = db.Column(db.Float, default=50.0)
    nivel_sobrepaso  = db.Column(db.Float, default=50.0)
    imagen           = db.Column(db.String(255), nullable=True)

    carreras = db.relationship('Carrera', backref='circuito', lazy=True)

    def to_dict(self):
        return {
            'id':              self.id,
            'nombre_gp':       self.nombre_gp,
            'nombre_circuito': self.nombre_circuito,
            'pais':            self.pais,
            'longitud':        self.longitud,
            'num_curvas':      self.num_curvas,
            'tipo_pista':      self.tipo_pista,
            'zonas_drs':       self.zonas_drs,
            'nivel_tecnico':   self.nivel_tecnico,
            'nivel_desgaste':  self.nivel_desgaste,
            'nivel_sobrepaso': self.nivel_sobrepaso,
            'imagen':          self.imagen,
        }
