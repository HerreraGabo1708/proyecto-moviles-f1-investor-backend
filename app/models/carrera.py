from app import db


class Carrera(db.Model):
    __tablename__ = 'carreras'

    id           = db.Column(db.Integer, primary_key=True)
    temporada_id = db.Column(db.Integer, db.ForeignKey('temporadas.id'), nullable=False)
    circuito_id  = db.Column(db.Integer, db.ForeignKey('circuitos.id'),  nullable=False)
    fecha        = db.Column(db.Date, nullable=True)
    estado       = db.Column(db.String(20), default='pendiente')   # pendiente / completada

    resultados = db.relationship('Resultado', backref='carrera', lazy=True)

    def to_dict(self):
        return {
            'id':           self.id,
            'temporada_id': self.temporada_id,
            'circuito_id':  self.circuito_id,
            'circuito':     self.circuito.nombre_gp if self.circuito else None,
            'fecha':        self.fecha.isoformat() if self.fecha else None,
            'estado':       self.estado,
        }
