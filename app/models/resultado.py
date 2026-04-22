from app import db


class Resultado(db.Model):
    __tablename__ = 'resultados'

    id           = db.Column(db.Integer, primary_key=True)
    carrera_id   = db.Column(db.Integer, db.ForeignKey('carreras.id'), nullable=False)
    piloto_id    = db.Column(db.Integer, db.ForeignKey('pilotos.id'),  nullable=False)
    posicion     = db.Column(db.Integer, nullable=False)
    puntos       = db.Column(db.Integer, default=0)
    tiempo       = db.Column(db.Float, nullable=True)    # segundos simulados
    estado_final = db.Column(db.String(30), default='finalizado')  # finalizado/abandono/dsq

    def to_dict(self):
        return {
            'id':           self.id,
            'carrera_id':   self.carrera_id,
            'piloto_id':    self.piloto_id,
            'piloto':       self.piloto.nombre if self.piloto else None,
            'posicion':     self.posicion,
            'puntos':       self.puntos,
            'tiempo':       self.tiempo,
            'estado_final': self.estado_final,
        }
