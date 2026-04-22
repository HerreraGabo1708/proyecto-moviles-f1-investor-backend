from app import db


class Temporada(db.Model):
    __tablename__ = 'temporadas'

    id           = db.Column(db.Integer, primary_key=True)
    anio         = db.Column(db.Integer, nullable=False)
    activa       = db.Column(db.Boolean, default=False)
    fecha_inicio = db.Column(db.Date, nullable=True)
    fecha_fin    = db.Column(db.Date, nullable=True)

    carreras = db.relationship('Carrera', backref='temporada', lazy=True)

    def to_dict(self):
        return {
            'id':           self.id,
            'anio':         self.anio,
            'activa':       self.activa,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin':    self.fecha_fin.isoformat()    if self.fecha_fin    else None,
        }
